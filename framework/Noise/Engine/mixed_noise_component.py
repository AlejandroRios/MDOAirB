"""
File name :
Authors   : 
Email     : aarc.88@gmail.com
Date      : 
Last edit :
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This function calculates the noise contribution of the mixed jet component. Adapted from SUAVE.
Inputs:
    - SPL_m               [dB]
    - Velocity_primary    [m/s]
    - theta_m             [rad]
    - sound_ambient       [SPL]
    - Velocity_secondary  [m/s]
    - Velocity_aircraft   [m/s]
    - Area_primary        [m^2]
    - Area_secondary      [m^2]
    - DSPL_m              [SPL]
    - EX_m
    - Str_m
    - Velocity_mixed      [m/s]
    - XBPR                   
Outputs:
    - SPL_m                [dB]
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
def mixed_noise_component(SPL_m,V_primary,theta_m,sound_ambient,V_secondary,
                          V_aircraft,area_primary,area_secondary,DSPL_m,EX_m,Str_m,V_mixed,XBPR):

    #Calculation of the velocity exponent
    velocity_exponent = (V_mixed/sound_ambient)**0.5*(0.6+(0.2/(0.2+Str_m) * \
        np.exp(-0.3*(theta_m+(Str_m/(1+Str_m))-2.7)**2)))

    #Calculation of the Source Strengh Function (FV)
    FV = ((V_mixed-V_aircraft)/sound_ambient)**velocity_exponent * \
        ((V_mixed+V_aircraft)/sound_ambient)**(1-velocity_exponent)

    #Determination of the noise model coefficients
    Z1 = -30*((1.8*theta_m/np.pi)-0.6)**2
    Z2 = -9 -4*((V_primary-V_secondary)/sound_ambient)-38*((1.8*theta_m/np.pi)-0.6)**3 + \
        30*(0.6-np.log10(1+area_secondary/area_primary))*(1.8*theta_m/np.pi - 0.6)
    Z3 = 1-0.4*((1.8*theta_m/np.pi)-0.6)**2
    Z4 = 0.44-0.5/np.exp(((4.5*theta_m/np.pi)-4)**2) + 0.2*V_primary/sound_ambient - \
        0.7*V_mixed/sound_ambient - 0.2*np.log10((1+area_secondary)/area_primary) + \
        0.05*(XBPR)*np.exp(-5*(theta_m-2.4)**2)
    Z5 = 34 + 81*theta_m/np.pi - 20*((1.8*theta_m/np.pi)-0.6)**3
    Z6 = 108 + 37.8*theta_m/np.pi + 5*V_mixed*(V_primary-V_secondary)/(sound_ambient**2) - \
        np.exp(-5*(theta_m-1.8)**2) + 7*V_mixed/sound_ambient*(1-0.4*(V_primary/sound_ambient) * \
        np.exp(-0.7*np.abs(Str_m-0.8))) / np.exp(8*(theta_m-2.4)**2) + 0.8*(XBPR)*np.exp(theta_m-2.3-V_mixed/sound_ambient) + \
        DSPL_m + EX_m

    #Determination of Sound Pressure Level for the mixed jet component
    SPL_m = (Z1*np.log10(FV)+Z2)*(np.log10(Str_m)-Z3*np.log10(FV)-Z4)**2 + Z5*np.log10(FV) + Z6

    return SPL_m 

# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
