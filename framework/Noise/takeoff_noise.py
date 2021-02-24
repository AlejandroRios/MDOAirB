"""
File name : takeoff noise function
Author    : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : February 2021
Last edit : 
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This function evaluates the noise generated by the aircraft during takeoff phase
Inputs:
    -
Outputs:
    -
TODO's:
    -

"""
# =============================================================================
# IMPORTS
# =============================================================================
import numpy as np

from framework.Attributes.Atmosphere.atmosphere_ISA_deviation import atmosphere_ISA_deviation
from framework.Performance.Engine.engine_performance import turbofan
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
global GRAVITY
GRAVITY = 9.8067
ms_to_knot = 1.9438

def takeoff_noise(vehicle):
    
    aircraft = vehicle['aircraft']
    wing = vehicle['wing']

    theta, delta, sigma, T_ISA, P_ISA, rho_ISA, a = atmosphere_ISA_deviation(altitude, delta_ISA)

    V_rotation = V_rotation_over_V_stall * np.sqrt((2*aircraft['maximum_takeoff_weight']*GRAVITY)/(rho_ISA*wing['area']*CL_max))  # [m/s]
    V_2 = V_2_over_V_stall * np.sqrt((2*aircraft['maximum_takeoff_weight']*GRAVITY)/(rho_ISA*wing['area']*CL_max))  # [m/s]
    V_climb = V_2 + 10/ms_to_knot
    V_vector = np.array([0, (V_2 + 20)/2, (V_2+20)])
    thrust_vector = V_vector/a

    thrust_force, fuel_flow = turbofan(altitude, mach, 1.0, vehicle)

    i_2 = 1
    time_history = np.array([0, 0, 0, 0, 0,   ])

















    return
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
