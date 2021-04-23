"""
File name :
Authors   : 
Email     : aarc.88@gmail.com
Date      : 
Last edit :
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This function calculates the noise contribution of the secondary jet component. Adapted from SUAVE.
Inputs:
    - SPL_s               [dB]
    - velocity_primary    [m/s]
    - theta_s             [rad]
    - sound_ambient       [dB]
    - V_secondary  [m/s]
    - V_aircraft   [m/s]
    - area_primary        [m^2]
    - area_secondary      [m^2]
    - DSPL_s              [dB]
    - EX_s                [-]
    - Str_s               [-]

Outputs:
    - SPL_s               [dB]
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
def secondary_noise_component(SPL_s,velocity_primary,theta_s,sound_ambient,V_secondary,V_aircraft,
                              area_primary,area_secondary,DSPL_s,EX_s,Str_s):
    # Calculation of the velocity exponent
    velocity_exponent = 0.5 * 0.1*theta_s

    # Calculation of the Source Strengh Function (FV)
    FV = ((V_secondary-V_aircraft)/sound_ambient)**velocity_exponent * \
        ((V_secondary+V_aircraft)/sound_ambient)**(1-velocity_exponent)

    # Determination of the noise model coefficients
    Z1 = -18*((1.8*theta_s/np.pi)-0.6)**2
    Z2 = -14-8*((1.8*theta_s/np.pi)-0.6)**3
    Z3 = -0.7
    Z4 = 0.6 - 0.5*((1.8*theta_s/np.pi)-0.6)**2+0.5*(0.6-np.log10(1+area_secondary/area_primary))
    Z5 = 51 + 54*theta_s/np.pi - 9*((1.8*theta_s/np.pi)-0.6)**3
    Z6 = 99 + 36*theta_s/np.pi - 15*((1.8*theta_s/np.pi)-0.6)**4 + 5*V_secondary*(velocity_primary-V_secondary)/(sound_ambient**2) + \
        DSPL_s + EX_s

    # Determination of Sound Pressure Level for the secondary jet component
    SPL_s = (Z1*np.log10(FV)+Z2)*(np.log10(Str_s)-Z3*np.log10(FV)-Z4)**2 + Z5*np.log10(FV) + Z6

    return SPL_s 


# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
