"""
File name :
Authors   : 
Email     : aarc.88@gmail.com
Date      : 
Last edit :
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This function calculates the angle of attack effect, in decibels, to be added 
    to the predicted mixed jet noise level. . Adapted from SUAVE.
    -
Inputs:
    - angle of attack [rad]
    - Mach number  [-]
    - theta_m        [rad]
Outputs:
    -
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
def angle_of_attack_effect (angle_of_attack, mach,theta_m):

    # Angle of attack effect
    ATK_m = 0.5*angle_of_attack*mach*((1.8*theta_m/np.pi)-0.6)**2

    return ATK_m
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
# angle_of_attack = 10*(np.pi/180)
# mach = 0.3
# theta_m = 20*(np.pi/180)
# print(angle_of_attack_effect (angle_of_attack, mach,theta_m))