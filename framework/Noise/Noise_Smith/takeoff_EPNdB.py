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
from framework.Noise.Noise_Smith.takeoff_noise import takeoff_noise
import numpy as np
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
def takeoff_EPNdB(time_vec,velocity_vec,distance_vec,velocity_horizontal_vec,altitude_vec,velocity_vertical_vec,trajectory_angle_vec,fan_rotation_vec,compressor_rotation_vec, throttle_position, takeoff_parameters,noise_parameters,aircraft_geometry,engine_parameters,vehicle):

    f, SPL, tetaout, time_vec, distance_vec, altitude_vec = takeoff_noise(time_vec,velocity_vec,distance_vec,velocity_horizontal_vec,altitude_vec,velocity_vertical_vec,trajectory_angle_vec,fan_rotation_vec,compressor_rotation_vec, throttle_position, takeoff_parameters,noise_parameters,aircraft_geometry,engine_parameters,vehicle)
    
    a2,a1 = SPL.shape
    ## Eliminação dos pontos não calculados ##
    # [a1 a2]             = np.size(SPL)
    for i1 in range(a1):
        for i2 in range(a2):
            print(i1,i2)
            if SPL[i2,i1]<0 or np.isnan(SPL[i2,i1]):
                SPL[i2,i1] = 0
    
    ## Transformação de SPL para NOY ##
    [f,NOY]             = calcNOY(f,SPL)
    # VERIFICAÇÃO EM DEBUG
    # x                   = tempo
    # y                   = f(3:24)
    # figure()
    # surf(x,y,NOY)
    # grid on
    # shading interp

    # ## Cálculo de Perceived Noise Level (PNL) ##
    # [PNL]               = calcPNL(f,NOY)

    # ## Cálculo da correção de tom para PNL ##
    # [~, a2]             = size(SPL)
    # for i1 = 1:a2
    #     C(i1)           = calcPNLT(f,SPL(:,i1))
    # end
    # ## Cálculo de Perceived Noise Level - tone corrected (PNLT) ##
    # PNLT                = PNL+C
    # # VERIFICAÇÃO EM DEBUG
    # # x                   = tempo
    # # figure()
    # # plot(x,PNL,'-b',x,PNLT,'-r')
    # # grid on

    # ## Cálculo de Effective Perceived Noise Level (EPNdB) ##
    # TOEPNdB             = calcEPNdB(tempo,PNLT)

    return
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
