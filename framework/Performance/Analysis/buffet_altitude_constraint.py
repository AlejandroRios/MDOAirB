"""
File name : Buffet altitude constraint
Author    : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : November/2020
Last edit : November/2020
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This module obtain the cruise altutude considering buffeting constraints
    - Reference: Ruijgrok, Elements of airplane performance
    - Chapter 10, pag 261
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
from framework.Attributes.Atmosphere.atmosphere_ISA_deviation import atmosphere_ISA_deviation
import numpy as np

from framework.Attributes.Airspeed.airspeed import mach_to_V_tas
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
global GRAVITY
GRAVITY = 9.80665


def buffet_altitude(vehicle, mass, altitude, limit_altitude, mach_climb):
    airport_departure = vehicle['airport_departure']
    wing = vehicle['wing']
    wing_surface = wing['area']
    step = 100
    load_factor = 1.3
    gamma = 1.4
    delta_ISA = airport_departure['delta_ISA']

    # Typical values of wing loading for jet airplanes around 5749 [Pascal]
    wing_loading_constraint = 6000
    _, _, _, _, P_ISA, _, _, _ = atmosphere_ISA_deviation(
        limit_altitude, delta_ISA)
    CL_constraint = ((2)/(gamma*P_ISA*mach_climb**2))*wing_loading_constraint

    CL = 0.1

    while CL < CL_constraint:
        theta, delta, sigma, T_ISA, P_ISA, rho_ISA, _, a = atmosphere_ISA_deviation(
            altitude, delta_ISA)
        CL = ((2*load_factor)/(gamma*P_ISA*mach_climb*mach_climb)) * \
            (mass*GRAVITY/wing_surface)
        altitude = altitude+step

    return altitude

# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
# weight = 43112
# altitude = 10000
# limit_altitude = 41000
# mach_climb = 0.78
# print(buffet_altitude(weight, altitude, limit_altitude, mach_climb))
