"""
File name : Landig field length function
Authors   : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : September/2020
Last edit : September/2020
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    -
    -
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
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================


def landing_field_length(vehicle, weight_landing):
    '''
    '''
    # Aircraft data import

    aircraft = vehicle['aircraft']
    wing = vehicle['wing']
    airport_destination = vehicle['airport_destination']
    
    CL_max_landing = aircraft['CL_maximum_landing']
    wing_surface = wing['area']  # [m2]

    # Airport data import
    airfield_elevation = airport_destination['elevation']  # [ft]
    delta_ISA = airport_destination['tref']  # [deg C]

    _, _, sigma, _, _, rho, _, _ = atmosphere_ISA_deviation(
        airfield_elevation, delta_ISA)  # [kg/m3]

    gamma_bar = 0.1  # mean value of (D-T)/W
    h_landing = 15.3  # screen height in landing - [m]
    g = 9.807  # [m/s2]
    a_bar_g = 0.4  # mean_deceleration, between 0.4 to 0.5 for jets
    Delta_n = 0.1  # incremental_load_factor during flare
    f_land = 5/3  # landing safe factor FAR Part 91

    aux1 = 1/gamma_bar
    aux2 = 1.69*((weight_landing/wing_surface) /
                 (h_landing*rho*g*CL_max_landing))
    aux3 = (1/a_bar_g) * (1 - ((gamma_bar**2)/Delta_n)) + (gamma_bar/Delta_n)

    S_landing_h_landing = aux1 + aux2*aux3

    return S_landing_h_landing*h_landing*f_land
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
