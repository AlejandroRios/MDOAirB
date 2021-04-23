"""
File name :
Authors   : 
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
from framework.Noise.Noise_Smith.approach_noise import approach_noise
from framework.Noise.Noise_Smith.noise_levels import *
import numpy as np
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================

def approach_EPNdB(time_vec,velocity_vec,distance_vec,altitude_vec,landing_parameters,noise_parameters,aircraft_geometry,vehicle):
    f, SPL, tetaout, time_vec, distance_vec, altitude_vec = approach_noise(time_vec,velocity_vec,distance_vec,altitude_vec,landing_parameters,noise_parameters,aircraft_geometry,vehicle)

    f,NOY = calculate_NOY(f,SPL)

    PNL = calculate_PNL(f,NOY)
    a2,_ = SPL.shape
    
    C = []
    for i1 in range(a2):
        C.append(calculate_PNLT(f,SPL[:][i1]))

    ## Cálculo de Perceived Noise Level - tone corrected (PNLT) ##
    PNLT                =PNL+C
    # VERIFICAÇÃO EM DEBUG
    # x                   = tempo
    # figure()
    # plot(x,PNL,'-b',x,PNLT,'-r')
    # grid on

    ## Cálculo de Effective Perceived Noise Level (EPNdB) ##
    LDEPNdB             = calculate_EPNdB(time_vec,PNLT)

    return LDEPNdB


# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
