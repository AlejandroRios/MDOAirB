"""
File name :
Author    : 
Email     : aarc.88@gmail.com
Date      : 
Last edit :
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
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
import numpy as np
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
def secondary_noise_component(SPL_s,Velocity_primary,theta_s,sound_ambient,Velocity_secondary,Velocity_aircraft,
                              Area_primary,Area_secondary,DSPL_s,EX_s,Str_s):
    # Calculation of the velocity exponent
    velocity_exponent = 0.5 * 0.1*theta_s

    # Calculation of the Source Strengh Function (FV)
    FV = ((Velocity_secondary-Velocity_aircraft)/sound_ambient)**velocity_exponent * \
        ((Velocity_secondary+Velocity_aircraft)/sound_ambient)**(1-velocity_exponent)

    # Determination of the noise model coefficients
    Z1 = -18*((1.8*theta_s/np.pi)-0.6)**2
    Z2 = -14-8*((1.8*theta_s/np.pi)-0.6)**3
    Z3 = -0.7
    Z4 = 0.6 - 0.5*((1.8*theta_s/np.pi)-0.6)**2+0.5*(0.6-np.log10(1+Area_secondary/Area_primary))
    Z5 = 51 + 54*theta_s/np.pi - 9*((1.8*theta_s/np.pi)-0.6)**3
    Z6 = 99 + 36*theta_s/np.pi - 15*((1.8*theta_s/np.pi)-0.6)**4 + 5*Velocity_secondary*(Velocity_primary-Velocity_secondary)/(sound_ambient**2) + \
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
