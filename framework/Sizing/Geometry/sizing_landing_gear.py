"""
File name : Sizing landing gear
Author    : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : January 2021
Last edit : February 2021
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This module performs the landing gear sizing.
Inputs:
    - Vehicle dictionary
Outputs:
    - Vehicle dictionary with landing gear information updated
TODO's:
    -

"""
# =============================================================================
# IMPORTS
# =============================================================================
import numpy as np
from framework.Sizing.Geometry.landig_gear_position import landig_gear_position
from framework.Sizing.Geometry.landing_gear_layout import landing_gear_layout
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================


def sizing_landing_gear(vehicle):

    fuselage = vehicle['fuselage']
    wing = vehicle['wing']
    horizontal_tail = vehicle['horizontal_tail']
    nose_landing_gear = vehicle['nose_landing_gear']
    main_landing_gear = vehicle['main_landing_gear']
    engine = vehicle['engine']

    wing['root_chord_yposiion'] = 0.85*(fuselage['width']/2)

    if (engine['position'] == 2 and horizontal_tail['position'] == 1):
        horizontal_tail['position'] = 2

    main_landing_gear['tyre_diameter'] = 0.95
    main_landing_gear_tyre_diameter_new = 100
    nose_landing_gear_tyre_diameter_new = 100
    main_landing_gear['piston_length'] = 1

    # Dont know the meaning of these variables:
    nose_landing_gear['tyre_diameter'] = 0.8
    nose_landing_gear['piston_length'] = 0.8*main_landing_gear['piston_length']

    while (np.abs(main_landing_gear['tyre_diameter'] - main_landing_gear_tyre_diameter_new) > 0.01 or np.abs(nose_landing_gear['tyre_diameter'] - nose_landing_gear_tyre_diameter_new) > 0.01):
        vehicle, yc_trunnion = landig_gear_position(vehicle)

        (vehicle, A_min, nt_m, main_landing_gear_tyre_diameter_new, wm_max, Lpist_m_new, ds_m, Lpist_n, ds_n, wn_max, nose_landing_gear_tyre_diameter_new) = landing_gear_layout(
            vehicle)

        main_landing_gear['piston_length'] = 0.40 * \
            main_landing_gear['piston_length'] + 0.60*Lpist_m_new
        main_landing_gear['tyre_diameter'] = (
            0.40*main_landing_gear['tyre_diameter'] + 0.60*main_landing_gear_tyre_diameter_new)
        nose_landing_gear['piston_length'] = (
            Lpist_n + nose_landing_gear['piston_length'])/2
        nose_landing_gear['tyre_diameter'] = (
            nose_landing_gear_tyre_diameter_new + nose_landing_gear['tyre_diameter'])/2

    return vehicle
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
