"""
File name :  Second segment climb function
Author    : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : September/2020
Last edit : September/2020
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This function calculates the thrust to weight ratio following the requiremnts
      of climb to second segment with one-engine-inoperative accoring to FAR 25.121.
      For this case the climb gradient expressed as a percentage takes a value of 0.024 (for two engine aircraft).
      The lading gear is up and takeoff flaps are deployed
      References: FAR 25.121 and ROSKAM 1997 - Part 1, pag. 146

    -
Inputs:
    - aircraft_data
Outputs:
    -
TODO's:
    -

"""
# =============================================================================
# IMPORTS
# =============================================================================
from framework.Attributes.Atmosphere.atmosphere_ISA_deviation import atmosphere_ISA_deviation
# from framework.Aerodynamics.aerodynamic_coefficients import zero_fidelity_drag_coefficient
from framework.Aerodynamics.aerodynamic_coefficients_ANN import aerodynamic_coefficients_ANN
import numpy as np
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
ft_to_m = 0.3048
kt_to_ms = 0.514444
def residual_rate_of_climb(vehicle, weight_takeoff,engine_cruise_thrust):
    '''
    '''

    aircraft = vehicle['aircraft']
    wing = vehicle['wing']
    airport_departure = vehicle['airport_departure']
    engine = vehicle['engine']

    CL_maximum_takeoff = aircraft['CL_maximum_takeoff']
    wing_surface = wing['area']
    maximum_takeoff_weight = weight_takeoff  # [N]

    airfield_elevation = airport_departure['elevation']
    airfield_delta_ISA = airport_departure['delta_ISA']
    
    thrust_takeoff = engine['maximum_thrust']*0.98

    _, _, _, _, _, rho, _, a = atmosphere_ISA_deviation(
        airfield_elevation, airfield_delta_ISA)  # [kg/m3]

    V = 1.2*np.sqrt(2*maximum_takeoff_weight /
                    (CL_maximum_takeoff*wing_surface*rho))
    mach = V/a*kt_to_ms
    phase = 'cruise'

    # CD_takeoff = zero_fidelity_drag_coefficient(aircraft_data, CL_maximum_takeoff, phase)
    # Input for neural network: 0 for CL | 1 for alpha
    switch_neural_network = 0
    alpha_deg = 1
    CD_wing, _ = aerodynamic_coefficients_ANN(
        vehicle, airfield_elevation*ft_to_m, mach, CL_maximum_takeoff,alpha_deg,switch_neural_network)

    friction_coefficient = wing['friction_coefficient']
    CD_ubrige = friction_coefficient * \
        (aircraft['wetted_area'] - wing['wetted_area']) / \
        wing['area']

    CD_takeoff = CD_wing + CD_ubrige

    L_to_D = CL_maximum_takeoff/CD_takeoff
    if aircraft['number_of_engines']  == 2:
        steady_gradient_of_climb = 0.024  # 2.4% for two engines airplane
    elif aircraft['number_of_engines']  == 3:
        steady_gradient_of_climb = 0.027  # 2.4% for two engines airplane
    elif aircraft['number_of_engines']  == 4:
        steady_gradient_of_climb = 0.03  # 2.4% for two engines airplane


    thrust_to_weight_residual = 1/((engine_cruise_thrust/thrust_takeoff)*L_to_D)

    return thrust_to_weight_residual
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================