"""
File name : Descent to altitude function
Authors   : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : November/2020
Last edit : November/2020
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This module calculates the aircraft performance during descent by integrating
    in time the point mass equations of movement. 
Inputs:
    - initial mass [kg]
    - mach_climb
    - climb_V_cas [knots]
    - delta_ISA [C deg]
    - final_altitude [ft]
    - initial_altitude [ft]
    - vehicle dictionary
Outputs:
    - final_distance [ft]
    - total_climb_time [min]
    - total_burned_fuel [kg]
    - final_altitude [ft]
TODO's:
    - Include a better description of this module

"""
# =============================================================================
# IMPORTS
# =============================================================================
from framework.Attributes.Airspeed.airspeed import V_cas_to_mach, mach_to_V_cas, crossover_altitude
from framework.Attributes.Atmosphere.atmosphere_ISA_deviation import atmosphere_ISA_deviation
from framework.Performance.Engine.engine_performance import turbofan
from framework.Performance.Analysis.descent_deceleration import decelaration_to_250
from framework.Performance.Analysis.descent_to_altitude import rate_of_descent_calculation

import numpy as np
# from scipy.integrate import odeint
# from scipy.integrate import ode
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
global GRAVITY
GRAVITY = 9.8067
kghr_to_kgmin = 0.01667


def descent_integration(mass, mach_descent, descent_V_cas, delta_ISA, final_altitude, initial_altitude, vehicle):
    rate_of_descent = -500

    time_descent1 = 0
    time_descent2 = 0
    time_descent3 = 0

    transition_altitude = crossover_altitude(
        mach_descent, descent_V_cas, delta_ISA)

    time = 0
    distance = 0
    fuel1 = 0
    fuel2 = 0
    fuel3 = 0

    if initial_altitude >= transition_altitude:
        flag1 = 1
        flag2 = 1
        flag3 = 1

    if (initial_altitude >= 10000 and initial_altitude < transition_altitude):
        flag1 = 0
        flag2 = 1
        flag3 = 1

    if initial_altitude < 10000:
        flag1 = 0
        flag2 = 0
        flag3 = 1

    total_burned_fuel = []
    total_descent_time = []

    throttle_position = 0.3

    if flag1 == 1:

        final_block_altitude = transition_altitude

        initial_block_distance = 0
        initial_block_altitude = initial_altitude
        initial_block_mass = mass
        initial_block_time = 0

        final_block_distance, final_block_altitude, final_block_mass, final_block_time = climb_integrator(
            initial_block_distance, initial_block_altitude, initial_block_mass, initial_block_time, final_block_altitude, 0, mach_descent, delta_ISA, vehicle)
       
        delta_distance = 0
        delta_time = 0
        delta_altitude = 0
        delta_fuel = 0

        burned_fuel = initial_block_mass - final_block_mass
        descent_time = final_block_time - initial_block_time
        total_burned_fuel.append(burned_fuel)
        total_descent_time.append(descent_time)

    if flag2 == 1:

        if flag1 == 0:
            initial_block_distance = 0
            initial_block_altitude = initial_altitude
            initial_block_mass = mass
            initial_block_time = 0
        else:
            initial_block_distance = final_block_distance
            initial_block_altitude = final_block_altitude
            initial_block_mass = final_block_mass
            initial_block_time = final_block_time

        final_block_altitude = 10000

        final_block_distance, final_block_altitude, final_block_mass, final_block_time = climb_integrator(
            initial_block_distance, initial_block_altitude, initial_block_mass, initial_block_time, final_block_altitude, descent_V_cas, 0, delta_ISA, vehicle)

        delta_distance, delta_time, delta_altitude, delta_fuel = decelaration_to_250(
            rate_of_descent, descent_V_cas, delta_ISA, vehicle)

        burned_fuel = initial_block_mass - final_block_mass
        descent_time = final_block_time - initial_block_time
        total_burned_fuel.append(burned_fuel)
        total_descent_time.append(descent_time)
        # plt.plot(time_interval, state[:, 1])

    if flag3 == 1:
        if flag1 == 0 and flag2 == 0:
            initial_block_distance = 0
            initial_block_altitude = initial_altitude
            initial_block_mass = mass
            initial_block_time = 0

        else:
            initial_block_distance = final_block_distance
            initial_block_altitude = final_block_altitude
            initial_block_mass = final_block_mass
            initial_block_time = final_block_time

        final_block_altitude = 1500

        final_block_distance, final_block_altitude, final_block_mass, final_block_time = climb_integrator(
            initial_block_distance, initial_block_altitude, initial_block_mass, initial_block_time, final_block_altitude, 250, 0, delta_ISA, vehicle)

        delta_distance = 0
        delta_time = 0
        delta_altitude = 0
        delta_fuel = 0

        burned_fuel = initial_block_mass - final_block_mass
        descent_time = final_block_time - initial_block_time
        total_burned_fuel.append(burned_fuel)
        total_descent_time.append(descent_time)

        # plt.plot(time_interval, state[:, 1])

    final_altitude = final_block_altitude

    final_distance = final_block_distance + delta_distance
    total_burned_fuel = sum(total_burned_fuel) + delta_fuel
    total_descent_time = sum(total_descent_time) + delta_time

    return final_distance, total_descent_time, total_burned_fuel, final_altitude


def climb_integrator(initial_block_distance, initial_block_altitude, initial_block_mass, initial_block_time, final_block_altitude, climb_V_cas, mach_climb, delta_ISA, vehicle):

    Tsim = initial_block_time + 40
    stop_condition.terminal = True

    stop_criteria = final_block_altitude

    sol = solve_ivp(climb, [initial_block_time, Tsim], [initial_block_distance, initial_block_altitude, initial_block_mass],
            events = stop_condition,method='LSODA',args = (climb_V_cas, mach_climb, delta_ISA, vehicle,stop_criteria), dense_output=True)

    distance = sol.y[0]
    altitude = sol.y[1]
    mass = sol.y[2]
    time = sol.t

    final_block_distance = distance[-1]
    final_block_altitude = altitude[-1]
    final_block_mass = mass[-1]
    final_block_time = time[-1]
    return final_block_distance, final_block_altitude, final_block_mass, final_block_time

def stop_condition(time, state, climb_V_cas, mach_climb, delta_ISA, vehicle,stop_criteria):
    H = state[1]
    return 0 if H<stop_criteria else 1


def climb(time, state, climb_V_cas, mach_climb, delta_ISA, vehicle,stop_criteria):

    aircraft = vehicle['aircraft']
    distance = state[0]
    altitude = state[1]
    mass = state[2]

    # print('t',time)
    # print('alt',altitude)

    # print('current:',altitude)
    # print('limit altitude:',final_block_altitude )
    # if altitude < final_block_altitude:
    #     return

    _, _, _, _, _, rho_ISA, _, _ = atmosphere_ISA_deviation(altitude, delta_ISA)
    throttle_position = 0.4

    if climb_V_cas > 0:
        mach = V_cas_to_mach(climb_V_cas, altitude, delta_ISA)
    else:
        mach = mach_climb

    thrust_force, fuel_flow , vehicle = turbofan(
        altitude, mach, throttle_position, vehicle)  # force [N], fuel flow [kg/hr]

    total_thrust_force = thrust_force*aircraft['number_of_engines']
    total_fuel_flow = fuel_flow*aircraft['number_of_engines']
    step_throttle = 0.01

    while (total_fuel_flow < 0 and throttle_position <= 1):
        thrust_force, fuel_flow , vehicle = turbofan(
            altitude, mach, throttle_position, vehicle)  # force [N], fuel flow [kg/hr]
        TSFC = (fuel_flow*GRAVITY)/thrust_force
        total_fuel_flow = aircraft['number_of_engines'] * fuel_flow
        throttle_position = throttle_position+step_throttle

    
    thrust_to_weight = aircraft['number_of_engines'] * \
        thrust_force/(mass*GRAVITY)
    
    # if thrust_to_weight < 0.001:
    #     return

    # print('T to W:',thrust_to_weight)
    rate_of_climb, V_tas, climb_path_angle = rate_of_descent_calculation(
        thrust_to_weight, altitude, delta_ISA, mach, mass, vehicle)

    x_dot = (V_tas*101.269)*np.cos(climb_path_angle)  # ft/min
    h_dot = (V_tas*101.269)*np.sin(climb_path_angle)  # ft/min
    # if (altitude < 10000 and altitude > 1500):
    #     h_dot = -500
    W_dot = -2*fuel_flow*kghr_to_kgmin  # kg/min
    # time_dot =  h_dot
    dout = [x_dot, h_dot, W_dot]

    return dout
# =============================================================================
# MAIN
# =============================================================================


# =============================================================================
# TEST
# =============================================================================
# mass = 43112
# mach_climb = 0.78
# climb_V_cas = 280
# delta_ISA = 0
# final_altitude = 39000
# initial_altitude = 0
# print(climb_integration(mass, mach_climb, climb_V_cas, delta_ISA, final_altitude, initial_altitude))
# print(state)
