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
from framework.Noise.Noise_Smith.takeoff_EPNdB import takeoff_EPNdB
import numpy as np
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
def sideline_EPNdB(time_vec,velocity_vec,distance_vec,velocity_horizontal_vec,altitude_vec,velocity_vertical_vec,trajectory_angle_vec,fan_rotation_vec,compressor_rotation_vec,throttle_position,takeoff_parameters,noise_parameters,aircraft_geometry,engine_parameters,vehicle):


    ## CORPO DA FUNÇÃO ##
    ## Cálculo do ruído lateral por aproximações sucessivas do ponto onde ele é mais intenso
    # 1ª aproximação (milhares de metros)
    Dmax1               = takeoff_parameters['trajectory_max_distance']
    Dmin1               = 0
    DD                  = 1000
    ncount              = int((Dmax1-Dmin1)/DD+1)
    XA                  = np.zeros(ncount)
    SLnoise             = np.zeros(ncount)
    for i in range(ncount):
        XA[i] = DD*(i)+Dmin1
        noise_parameters['takeoff_longitudinal_distance_mic']           = XA[i]
        SLnoise[i]      = takeoff_EPNdB(time_vec,velocity_vec,distance_vec,velocity_horizontal_vec,altitude_vec,velocity_vertical_vec,trajectory_angle_vec,fan_rotation_vec,compressor_rotation_vec, throttle_position, takeoff_parameters,noise_parameters,aircraft_geometry,engine_parameters,vehicle)

    S1max      = max(SLnoise)
    I1max = np.argmax(SLnoise)
    # 2ª aproximação (centenas de metros)
    Dmax2               = DD*(I1max+1)+Dmin1
    Dmin2               = DD*(I1max-1)+Dmin1
    DD                  = 100
    ncount              = int((Dmax2-Dmin2)/DD+1)
    XA                  = np.zeros(ncount)
    SLnoise             = np.zeros(ncount)

    for i in range(ncount):
        XA[i] = DD*(i)+Dmin2
        noise_parameters['takeoff_longitudinal_distance_mic']           = XA[i]
        SLnoise[i]      = takeoff_EPNdB(time_vec,velocity_vec,distance_vec,velocity_horizontal_vec,altitude_vec,velocity_vertical_vec,trajectory_angle_vec,fan_rotation_vec,compressor_rotation_vec, throttle_position, takeoff_parameters,noise_parameters,aircraft_geometry,engine_parameters,vehicle)

    S1max      = max(SLnoise)
    I1max = np.argmax(SLnoise)
    # 3ª aproximação (dezenas de metros)
    Dmax3               = DD*(I1max+1)+Dmin2
    Dmin3               = DD*(I1max-1)+Dmin2
    DD                  = 10
    ncount              = int((Dmax3-Dmin3)/DD+1)
    XA                  = np.zeros(ncount)
    SLnoise             = np.zeros(ncount)
    for i in range(ncount):
        XA[i] = DD*(i)+Dmin3
        noise_parameters['takeoff_longitudinal_distance_mic']           = XA[i]
        SLnoise[i]      = takeoff_EPNdB(time_vec,velocity_vec,distance_vec,velocity_horizontal_vec,altitude_vec,velocity_vertical_vec,trajectory_angle_vec,fan_rotation_vec,compressor_rotation_vec, throttle_position, takeoff_parameters,noise_parameters,aircraft_geometry,engine_parameters,vehicle)

    S1max      = max(SLnoise)
    I1max = np.argmax(SLnoise)
    # 4ª aproximação (metros)
    Dmax4               = DD*(I1max+1)+Dmin3
    Dmin4               = DD*(I1max-1)+Dmin3
    DD                  = 1
    ncount              = int((Dmax4-Dmin4)/DD+1)
    XA                  = np.zeros(ncount)
    SLnoise             = np.zeros(ncount)
    for i in range(ncount):
        XA[i] = DD*(i)+Dmin4
        noise_parameters['takeoff_longitudinal_distance_mic']           = XA[i]
        SLnoise[i]      = takeoff_EPNdB(time_vec,velocity_vec,distance_vec,velocity_horizontal_vec,altitude_vec,velocity_vertical_vec,trajectory_angle_vec,fan_rotation_vec,compressor_rotation_vec, throttle_position, takeoff_parameters,noise_parameters,aircraft_geometry,engine_parameters,vehicle)

    S1max      = max(SLnoise)
    I1max = np.argmax(SLnoise)


    ## SAÍDA DOS DADOS ## 
    SLEPNdB             = SLnoise[I1max]
    XApeak              = XA[I1max]

    return SLEPNdB, XApeak


# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
