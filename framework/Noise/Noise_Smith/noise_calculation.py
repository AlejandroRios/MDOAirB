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

from framework.Noise.Noise_Smith.takeoff_profile import takeoff_profile
from framework.Noise.Noise_Smith.takeoff_EPNdB import takeoff_EPNdB
from framework.Noise.Noise_Smith.sideline_EPNdB import sideline_EPNdB
from framework.Noise.Noise_Smith.approach_profile import approach_profile
from framework.Noise.Noise_Smith.approach_EPNdB import approach_EPNdB

# from framework.Attributes.Atmosphere.atmosphere_ISA_deviation import atmosphere_ISA_deviation
# from framework.Performance.Engine.engine_performance import turbofan
# from framework.Attributes.Airspeed.airspeed import V_cas_to_mach, mach_to_V_cas, crossover_altitude
# from framework.Performance.Analysis.climb_to_altitude import rate_of_climb_calculation
from datetime import datetime
from framework.utilities.logger import get_logger

import numpy as np
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
log = get_logger(__file__.split('.')[0])
global GRAVITY
GRAVITY = 9.81
kt_to_ms = 0.514444
deg_to_rad = np.pi/180



def aircraft_noise(takeoff_parameters, landing_parameters,aircraft_parameters,aircraft_geometry,engine_parameters,runaway_parameters,noise_parameters,vehicle):
    log.info('---- Start aircraft noise module ----')
    
    # ---- Takeoff noise ----

    # Takeoff flight path:
    # start = time.time()
    time_vec,velocity_vec,distance_vec,velocity_horizontal_vec,altitude_vec,velocity_vertical_vec,trajectory_angle_vec,fan_rotation_vec,compressor_rotation_vec = takeoff_profile(takeoff_parameters,landing_parameters,aircraft_parameters,runaway_parameters,engine_parameters,vehicle)
    # end = time.time()
    # print("takeoff path = %s" % (end - start))

    throttle_position = 1

    # Noise calculation - EPNdB
    # start = time.time()
    noise_parameters
    TO_noise = takeoff_EPNdB(time_vec,velocity_vec,distance_vec,velocity_horizontal_vec,altitude_vec,velocity_vertical_vec,trajectory_angle_vec,fan_rotation_vec,compressor_rotation_vec, throttle_position, takeoff_parameters,noise_parameters,aircraft_geometry,engine_parameters,vehicle)
    # end = time.time()
    # print("takeoff noise = %s" % (end - start))

    # start = time.time()
    sideline_noise,_ = sideline_EPNdB(time_vec,velocity_vec,distance_vec,velocity_horizontal_vec,altitude_vec,velocity_vertical_vec,trajectory_angle_vec,fan_rotation_vec,compressor_rotation_vec,throttle_position,takeoff_parameters,noise_parameters,aircraft_geometry,engine_parameters,vehicle)
    # end = time.time()
    # print("sideline noise = %s" % (end - start))

    # ---- Aproach and landing noise ----
    # Takeoff flight path:
    # start = time.time()
    t, d, h, FN, CD, CL, VT = approach_profile(takeoff_parameters,landing_parameters,aircraft_parameters,vehicle)
    # end = time.time()
    # print("approach path = %s" % (end - start))

    # Noise calculation - EPNdB
    # start = time.time()
    landing_noise = approach_EPNdB(t,VT,d,h,landing_parameters,noise_parameters,aircraft_geometry,vehicle)
    # end = time.time()
    # print("landing noise= %s" % (end - start))
    return TO_noise, sideline_noise, landing_noise


def noise_calculation(vehicle):
    start_time = datetime.now()
    GRAVITY = 9.8065

    aircraft = vehicle['aircraft']
    airport_departure = vehicle['airport_departure']
    engine = vehicle['engine']
    wing = vehicle['wing']
    noise = vehicle['noise']


    maximum_takeoff_weight = aircraft['maximum_takeoff_weight']*GRAVITY
    maximum_landing_weight = aircraft['maximum_landing_weight']*GRAVITY

    takeoff_parameters = {}

    takeoff_parameters['takeoff_weight'] = maximum_takeoff_weight  # [N]
    takeoff_parameters['lambda'] = noise['takeoff_lambda']
    takeoff_parameters['k1'] = noise['takeoff_k1'] 
    takeoff_parameters['k2'] = noise['takeoff_k2']
    takeoff_parameters['time_1'] = noise['takeoff_time_1']  # [s]
    takeoff_parameters['obstacle_altitude'] = noise['takeoff_obstacle_altitude']  # [ft]
    takeoff_parameters['time_step'] = noise['takeoff_time_step']  # [s]
    takeoff_parameters['time_2'] = noise['takeoff_time_2']  # [s]
    takeoff_parameters['trajectory_max_distance'] = noise['takeoff_trajectory_max_distance']  # [m]

    landing_parameters = {}
    landing_parameters['gamma'] = noise['landing_gamma']
    landing_parameters['CL_3P'] = noise['landing_CL_3P']
    landing_parameters['CD_3P'] = noise['landing_CD_3P']
    landing_parameters['mu_roll'] = noise['landing_mu_roll']
    landing_parameters['mu_brake'] = noise['landing_mu_brake']
    landing_parameters['transition_time'] = noise['landing_transition_time']
    landing_parameters['load_factor_flare'] = noise['landing_load_factor_flare']

    aircraft_parameters = {}
    aircraft_parameters['CL_3P'] = noise['aircraft_parameters_CL_3P']
    aircraft_parameters['CL_air'] = noise['aircraft_parameters_CL_air']
    aircraft_parameters['CD_3P'] = noise['aircraft_parameters_CD_3P']
    aircraft_parameters['CD_air_LG_down'] = noise['aircraft_parameters_CD_air_LG_down']
    aircraft_parameters['CD_air_LG_up'] = noise['aircraft_parameters_CD_air_LG_up']

    aircraft_geometry = {}
    aircraft_geometry['fuselage_surface'] = noise['aircraft_geometry_fuselage_surface']
    aircraft_geometry['fuselage_length'] = noise['aircraft_geometry_fuselage_length']
    aircraft_geometry['flap_deflection_TO'] = wing['flap_deflection_takeoff']
    aircraft_geometry['flap_deflection_LD'] = wing['flap_deflection_landing']
    aircraft_geometry['main_landing_gear_number'] = noise['aircraft_geometry_main_landing_gear_number']
    aircraft_geometry['nose_landig_gear_number'] = noise['aircraft_geometry_nose_landing_gear_number']

    aircraft_geometry['main_landing_gear_length'] = noise['aircraft_geometry_main_landing_gear_length']
    aircraft_geometry['nose_landing_gear_length'] = noise['aircraft_geometry_nose_landing_gear_length']
    aircraft_geometry['main_landing_gear_wheels'] = noise['aircraft_geometry_main_landing_gear_wheels']
    aircraft_geometry['nose_landing_gear_wheels'] = noise['aircraft_geometry_nose_landing_gear_wheels']
    aircraft_geometry['wing_flap_type1_position'] = noise['aircraft_geometry_wing_flap_type1_position']
    aircraft_geometry['wing_flap_type2_position'] = noise['aircraft_geometry_wing_flap_type2_position']
    aircraft_geometry['slats_position'] = noise['aircraft_geometry_slats_position']
    aircraft_geometry['slots_number'] = noise['aircraft_geometry_slots_number']
    aircraft_geometry['main_landing_gear_position'] = noise['aircraft_geometry_main_landing_gear_position']
    aircraft_geometry['nose_landing_gear_position'] = noise['aircraft_geometry_nose_landing_gear_position']
    aircraft_geometry['altitude_retracted'] = noise['aircraft_geometry_altitude_retracted']
    aircraft_geometry['delta_ISA_retracted'] =airport_departure['delta_ISA']

    engine_parameters = {}
    engine_parameters['throttle_position'] = noise['engine_parameters_throttle_position']
    engine['fan_rotation'] = noise['engine_parameters_fan_rotation']
    engine['compressor_rotation'] = noise['engine_parameters_compressor_rotation']

    runaway_parameters = {}
    runaway_parameters['mu_roll'] = noise['runaway_parameters_mu_roll']
    runaway_parameters['mu_brake'] = noise['runaway_parameters_mu_brake']

    noise_parameters = {}
    noise_parameters['relative_humidity'] = noise['relative_humidity']
    noise_parameters['landing_lateral_distance_mic'] = noise['landing_lateral_distance_mic'] 
    noise_parameters['sideline_lateral_distance_mic'] = noise['sideline_lateral_distance_mic']
    noise_parameters['takeoff_lateral_distance_mic'] = noise['takeoff_lateral_distance_mic'] 
    noise_parameters['landing_longitudinal_distance_mic'] = noise['landing_longitudinal_distance_mic']
    noise_parameters['sideline_longitudinal_distance_mic'] = noise['sideline_longitudinal_distance_mic']
    noise_parameters['takeoff_longitudinal_distance_mic'] = noise['takeoff_longitudinal_distance_mic']

    takeoff_noise, sideline_noise, landing_noise = aircraft_noise(takeoff_parameters, landing_parameters,aircraft_parameters,aircraft_geometry,engine_parameters,runaway_parameters,noise_parameters,vehicle)
   
    end_time = datetime.now()
    log.info('Noise check execution time: {}'.format(end_time - start_time))
    log.info('---- End aircraft noise module ----')


    return takeoff_noise, sideline_noise, landing_noise

# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
# from framework.Database.Aircrafts.baseline_aircraft_parameters import *
# import time


# wing['area'] = 72
# wing['span'] = 24

# horizontal_tail['area'] = 25.6445
# horizontal_tail['span'] = 4.6734

# vertical_tail['area'] = 18.2006
# vertical_tail['span'] = 4.6734

# aircraft['maximum_takeoff_weight'] = 25579
# aircraft['maximum_landing_weight'] = 23021
# aircraft['CL_maximum_landing'] = 2.8517
# aircraft['CL_maximum_takeoff'] = 2.2517

# engine['fan_pressure_ratio'] = 1.6
# engine['compressor_pressure_ratio'] = 27
# engine['bypass'] = 4
# engine['engine_diameter'] = 1
# engine['turbine_inlet_temperature'] = 1410

# main_landing_gear['tyre_diameter'] = 0.6181
# nose_landing_gear['tyre_diameter'] = 0.6147

# start = time.time()
# print(noise_calculation(vehicle))

# end = time.time()
# print("Elapsed (after compilation) = %s" % (end - start))