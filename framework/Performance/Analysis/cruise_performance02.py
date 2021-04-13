"""
File name : Cruise performance function
Author    : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : November/2020
Last edit : November/2020
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This module calculates the cruise performance using the Breguet equations
Inputs:
    - Cruise altitude [ft]
    - Delta ISA [C deg]
    - Mach number
    - Mass at top of climb
    - Cruise distance [mn]
    - Vehicle dictionary
Outputs:
    - Cruise time [min]
    - Mass at top of descent [kg]
TODO's:
    - Rename variables 

"""
# =============================================================================
# IMPORTS
# =============================================================================
from inspect import isfunction
import numpy as np
# from scipy.optimize import fsolve
from scipy.optimize import minimize
from scipy import optimize
from framework.Performance.Engine.engine_performance import turbofan
from framework.Attributes.Atmosphere.atmosphere_ISA_deviation import atmosphere_ISA_deviation
from framework.Attributes.Airspeed.airspeed import V_cas_to_mach, mach_to_V_cas, mach_to_V_tas, crossover_altitude
# from framework.Aerodynamics.aerodynamic_coefficients import zero_fidelity_drag_coefficient
from framework.Aerodynamics.aerodynamic_coefficients_ANN import aerodynamic_coefficients_ANN

# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
global GRAVITY
GRAVITY = 9.80665


def cruise_performance(altitude, delta_ISA, mach, mass, distance_cruise, vehicle):
    n = 10
    step_cruise = distance_cruise/n
    distance = 0
    time_cruise = 0
    mass_fuel_cruise = 0
    d = 0
    

    V_tas = mach_to_V_tas(mach, altitude, delta_ISA)

    for i in range(n):

        TSFC, L_over_D, fuel_flow, throttle_position = specific_fuel_consumption(
            vehicle, mach, altitude, delta_ISA, mass)

        mass_fuel, time = breguet(altitude, delta_ISA, mach, L_over_D, TSFC,step_cruise,mass)

        time_cruise = time_cruise + time

        mass_fuel_cruise = mass_fuel_cruise + mass_fuel

        d = d+step_cruise
        # print(mass_fuel)

    final_mass = mass - mass_fuel_cruise
    # print(final_mass)

    return time_cruise, final_mass


def specific_fuel_consumption(vehicle, mach, altitude, delta_ISA, mass):

    knots_to_meters_second = 0.514444

    aircraft = vehicle['aircraft']
    wing = vehicle['wing']
    wing_surface = wing['area']

    V_tas = mach_to_V_tas(mach, altitude, delta_ISA)
    _, _, _, _, _, rho_ISA, _, _ = atmosphere_ISA_deviation(altitude, delta_ISA)

    CL_required = (2*mass*GRAVITY) / \
        (rho_ISA*((knots_to_meters_second*V_tas)**2)*wing_surface)
    # print('CL',CL_required)
    phase = 'cruise'
    # CD = zero_fidelity_drag_coefficient(aircraft_data, CL_required, phase)

    # Input for neural network: 0 for CL | 1 for alpha
    switch_neural_network = 0
    alpha_deg = 1
    CD_wing, _ = aerodynamic_coefficients_ANN(
        vehicle, altitude, mach, CL_required, alpha_deg, switch_neural_network)

    friction_coefficient = wing['friction_coefficient']
    CD_ubrige = friction_coefficient * \
        (aircraft['wetted_area'] - wing['wetted_area']) / \
        wing['area']

    CD = CD_wing + CD_ubrige

    
    L_over_D = CL_required/CD
    throttle_position = 0.6

    thrust_force, fuel_flow , vehicle = turbofan(
        altitude, mach, throttle_position, vehicle)  # force [N], fuel flow [kg/hr]

    FnR = mass*GRAVITY/L_over_D

    step_throttle = 0.01
    throttle_position = 0.6
    total_thrust_force = 0

    while (total_thrust_force < FnR and throttle_position <= 1):
        thrust_force, fuel_flow , vehicle = turbofan(
            altitude, mach, throttle_position, vehicle)  # force [N], fuel flow [kg/hr]
        TSFC = (fuel_flow*GRAVITY)/thrust_force
        total_thrust_force = aircraft['number_of_engines'] * thrust_force
        throttle_position = throttle_position+step_throttle

    L_over_D = CL_required/CD

    return TSFC, L_over_D, fuel_flow, throttle_position


def mission_segment(mass_0, step_cruise, L_over_D, TSFC, V_tas):
    knots_to_meters_second = 0.514444
    second_to_miniute = 0.01667
    fixedW = mass_0  # [kg]
    R = step_cruise*1852  # convert 600 nmi to m [m]
    TSFC = TSFC*(1/3600)  # 1/s

    V = V_tas*knots_to_meters_second  # [m/s]
    segments = [breguet('jet', 'cruise', R, L_over_D, TSFC, V, False)]
    fuel_safety_margin = 0.06
    FF = (1+fuel_safety_margin)*missionfuelburn(segments)

    def EWfunc(w0): 
        return 3.03*w0**-0.235

    mass_0 = fuelfractionsizing(EWfunc, fixedW, FF, False, False)

    # print(FF)
    # print(mass_0)
    mass_fuel = FF*mass_0
    time = 1/TSFC * L_over_D * np.log(1/segments[0])
    return mass_fuel, time*second_to_miniute


def breguet(altitude, delta_ISA, mach, LD, SFC,step_cruise,W0):
    second_to_miniute = 0.01667
    _, _, _, _, _, _, _, a = atmosphere_ISA_deviation(altitude, delta_ISA)
    V=mach*a
    a1=SFC*(1/LD)
    a2=step_cruise*a1/V;
    f=np.exp(a2)
    Wf=W0/f
    mass_fuel=W0-Wf
    t=(1/a1)*np.log(W0/Wf)*60
    R = step_cruise*1852
    time = 1/SFC * LD * np.log(1/(np.exp(-R*SFC/(V*LD))))

    # print(varargout)
    return mass_fuel, time*second_to_miniute


def fuelfractionsizing(sf, fixedW, FF, tol, maxW):

    if isfunction(sf) is not True:
        if len(sf) == 1:
            W0 = fixedW/(1-FF-sf[0])
            return
        elif len(sf) == 2:
            def sf(w0): return sf[0]*w0**(sf[1])
        elif len(sf) == 3:
            def sf(w0): return sf[2]*sf[0]*w0**(sf[1])
        else:
            print('invalid empty weight function sf')

    if isinstance(sf, (np.ndarray)) is True:
        FF = missionfuelburn(FF)

    minW = fixedW/(1-FF)

    # # default maxW represents an aircraft with a terrible fixedW fraction
    if not maxW:
        maxW = 800000/GRAVITY

    if not tol:
        tol = 1e-5*minW

    def f(W): 
        
        return 1 - sf(W) - FF - fixedW/W

    W0_init = np.mean([minW, maxW])
    # (0.015,0.2)
    # bounds = minW
    if minW > maxW:
        return
    

    # bnds = ((minW,maxW))
    # res = minimize(f, W0_init, bounds=((minW,maxW),), tol=tol, options={'disp': False})
    # W0 = res.x[0]
    W0 =  optimize.newton(f, W0_init,tol=tol)
    # W0 = res

    # bounds = np.array([minW, maxW])
    # bounds = minW
    # W0 = fsolve(f, W0_init, xtol=tol)

    # print(W0)

    return(W0)


def missionfuelburn(varargin):
    n = len(varargin)
    fracs = [0]*(n+1)
    fracs[0] = 1
    for ii in range(n):
        fracs[ii+1] = fracs[ii]*varargin[ii]
    FF = 1 - fracs[-1]
    return(FF)

# =============================================================================
# MAIN
# =============================================================================


# =============================================================================
# TEST
# =============================================================================

# from framework.Database.Aircrafts.baseline_aircraft_parameters import *
# altitude = 39000
# delta_ISA = 30
# mach = 0.8
# mass = 50000
# distance_cruise = 1500
# # results = cruise_performance(altitude, delta_ISA, mach, mass, distance_cruise,vehicle)
# # print(results)

# # res = []
# # enes = []
# # for n in range(1,50):
# #     print(n)
# #     _,aux = cruise_performance(altitude, delta_ISA, mach, mass, distance_cruise,vehicle,n)
# #     res.append(float(aux))
# #     enes.append(n)

# # import matplotlib.pyplot as plt


# # print(res)
# # print(n)
# # plt.plot(enes, res)
# # plt.show()
# from datetime import datetime
# start_time = datetime.now()
# _,aux = cruise_performance(altitude, delta_ISA, mach, mass, distance_cruise,vehicle)
# end_time = datetime.now()
# print('Mission sizing execution time: {}'.format(end_time - start_time))