"""
File name :
Authors   : 
Email     : aarc.88@gmail.com
Date      : 
Last edit :
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This function calculates the ground proximity effect, in decibels, and is used for full-scale 
    engine test stand. Adapted from SUAVE.
Inputs:
    - Velocity_mixed  [m/s]
    - sound_ambient   [SPL]
    - theta_m         [rad]
    - engine_height   [m]
    - Diameter_mixed  [m]
    - frequency       [1/s]

Outputs:
    - GPROX_m         [dB]
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
def ground_proximity_effect(V_mixed,sound_ambient,theta_m,engine_height,diameter_mixed,frequency):

    # Ground proximity is applied only for the mixed jet component
    GPROX_m = (5*V_mixed/sound_ambient)*np.exp(-(9*(theta_m/np.pi)-6.75)**2- \
        ((engine_height/diameter_mixed)-2.5)**2)*(1+(np.sin((np.pi*engine_height*frequency/sound_ambient)-np.pi/2))**2)/ \
        (2+np.abs((engine_height*frequency/sound_ambient)-1))

    return GPROX_m
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
# V_mixed = 300
# sound_ambient = 10
# theta_m = 0.1
# engine_height = 0.5
# diameter_mixed = 2
# frequency = 2
# print(ground_proximity_effect(V_mixed,sound_ambient,theta_m,engine_height,diameter_mixed,frequency))