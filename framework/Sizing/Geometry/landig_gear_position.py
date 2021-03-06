"""
File name : Landing gear position function
Author    : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : January 2021
Last edit : February 2021
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This module performs the calculation of the main landing gear position
Inputs:
    - Vehicle dictionary
Outputs:
    - Vehicle dictionary with landing gear information updated
    - y position trunnion
TODO's:
    -

"""
# =============================================================================
# IMPORTS
# =============================================================================
import numpy as np
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
global deg_to_rad
deg_to_rad = np.pi/180


def landig_gear_position(vehicle):

    engine = vehicle['engine']
    wing = vehicle['wing']
    nose_landing_gear = vehicle['nose_langing_gear']
    main_landing_gear = vehicle['main_langing_gear']

    wing['semi_span'] = wing['span']/2
    wing['root_thickness'] = wing['thickness_ratio'][0]*wing['root_chord']
    
    if engine['position'] == 1:
        lref1 = wing['semi_span_kink']*wing['semi_span'] - engine['diameter']/2
        lref3 = wing['root_thickness']*0.5*0.8 + engine['diameter']*1.1
        wing['trunnion_length'] = max(lref3,main_landing_gear['piston_length'])

        if wing['trunnion_length'] < (lref1 - wing['root_chord_yposiion']):
            yc_trunnion = wing['root_chord_yposiion'] + wing['trunnion_length']
        else:
            yc_trunnion = lref1

    if engine['position'] == 2:
        lref1 = (wing['kink_yposition']-wing['root_chord_yposiion'])*np.tan(wing['sweep_leading_edge']*deg_to_rad)
        wing['trunnion_length'] = max(lref1,main_landing_gear['piston_length'])
        yc_trunnion = max(0.1*wing['semi_span'], 0.55*wing['kink_yposition'])

        if (wing['trunnion_length'] - main_landing_gear['tyre_diameter']*0.5) < (0.55*wing['kink_yposition'] - wing['root_chord_yposiion']):
            wing['trunnion_length'] = yc_trunnion - wing['root_chord_yposiion'] + main_landing_gear['tyre_diameter']*0.5
    
    tanaux = np.tan(wing['sweep_leading_edge']*deg_to_rad)

    x1 = wing['leading_edge_xposition'] + wing['semi_span_kink']*wing['semi_span']*tanaux + wing['rear_spar_ref']*wing['kink_chord']
    y1 = wing['semi_span_kink']*wing['semi_span']
    x2 = wing['leading_edge_xposition'] + wing['semi_span']*tanaux + wing['rear_spar_ref']*wing['kink_chord']
    y2 = wing['semi_span']

    if x1 == x2:
        x075trunnion_front = x1
    else:
        slope = (y2-y1)/(x2-x1)
        x075trunnion_front = ((yc_trunnion-y1)/slope)+x1
    
    x1 = wing['leading_edge_xposition'] + wing['semi_span_kink'] + wing['semi_span']*np.tan(wing['sweep_leading_edge']*deg_to_rad) + wing['rear_spar_ref']*wing['kink_chord']
    y1 = wing['semi_span_kink']*wing['semi_span']
    x2 = wing['leading_edge_xposition'] + wing['root_chord_yposiion']*np.tan(wing['sweep_leading_edge']*deg_to_rad) +  wing['rear_spar_ref']*wing['root_chord']
    y2 = wing['root_chord_yposiion']


    if x2 < x1:
        slope = (y2-y1)/(x2-x1)
        xtrunnion_front = ((yc_trunnion-y1)/slope)+x1
    else:
        xtrunnion_front = x1
    
    main_landing_gear['xpostion']  = 0.50*(x075trunnion_front+xtrunnion_front)-0.10

    return vehicle, yc_trunnion









        












    return
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
