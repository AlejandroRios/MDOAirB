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
from framework.Database.Aircrafts.baseline_aircraft_parameters import *
from framework.Attributes.Atmosphere.atmosphere_ISA_deviation import atmosphere_ISA_deviation
from framework.Performance.Engine.engine_performance import turbofan
from framework.Attributes.Airspeed.airspeed import V_cas_to_mach, mach_to_V_cas, crossover_altitude
from framework.Performance.Analysis.climb_to_altitude import rate_of_climb_calculation

import math
from scipy.integrate import ode
import matplotlib.pyplot as plt
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
global GRAVITY
GRAVITY = 9.81
kt_to_ms = 0.514444
deg_to_rad = np.pi/180

def aircraft_noise(takeoff_parameters, landing_parameters,aircraft_parameters,aircraft_geometry,engine_parameters,runaway_parameters,noise_parameters,vehicle):
    
    # ---- Takeoff noise ----

    # Takeoff flight path:
    time_vec,velocity_vec,distance_vec,velocity_horizontal_vec,altitude_vec,velocity_vertical_vec,trajectory_angle_vec,fan_rotation_vec,compressor_rotation_vec = takeoff_profile(takeoff_parameters,landing_parameters,aircraft_parameters,runaway_parameters,engine_parameters,vehicle)

    # Noise calculation - EPNdB
    TO_noise = takeoff_EPNdB(time_vec,velocity_vec,distance_vec,velocity_horizontal_vec,altitude_vec,velocity_vertical_vec,trajectory_angle_vec,fan_rotation_vec,compressor_rotation_vec, throttle_position, takeoff_parameters,noise_parameters,aircraft_geometry,engine_parameters,vehicle)
    sideline_noise,_ = sideline_EPNdB(time_history,throttle_position,takeoff_parameters,noise_parameters,aircraft_geometry,engine_parameters,vehicle)

    # ---- Aproach and landing noise ----

    # Takeoff flight path:
    _ = approach_profile(takeoff_parameters,landing_parameters,aircraft_parameters,vehicle)

    # Noise calculation - EPNdB
    landing_noise = approach_EPNdB(_,landing_parameters,noise_parameters,aircraft_geometry,vehicle)

    return takeoff_noise, sideline_noise, landing_noise


def noise_calculation(vehicle):
    GRAVITY = 9.81

    aircraft = vehicle['aircraft']
    airport_departure = vehicle['airport_departure']
    maximum_takeoff_weight = aircraft['maximum_takeoff_weight']*GRAVITY
    maximum_landing_weight = aircraft['maximum_landing_weight']*GRAVITY

    takeoff_parameters = {}

    takeoff_parameters['takeoff_weight'] = maximum_takeoff_weight  # [N]
    takeoff_parameters['lambda'] = 0
    takeoff_parameters['k1'] = 1.1
    takeoff_parameters['k2'] = 1.2
    takeoff_parameters['time_1'] = 3.0  # [s]
    takeoff_parameters['obstacle_altitude'] = 35  # [ft]
    takeoff_parameters['time_step'] = 0.5  # [s]
    takeoff_parameters['time_2'] = 3.0  # [s]
    takeoff_parameters['trajectory_max_distance'] = 10000  # [m]

    landing_parameters = {}
    landing_parameters['gamma'] = -3
    landing_parameters['CL_3P'] = 0.3
    landing_parameters['CD_3P'] = 0.08
    landing_parameters['mu_roll'] = 0.03
    landing_parameters['mu_brake'] = 0.3
    landing_parameters['transition_time'] = 1.0
    landing_parameters['load_factor_flare'] = 1.1

    aircraft_parameters = {}
    aircraft_parameters['CL_3P'] = 0.3
    aircraft_parameters['CL_air'] = 1.65
    aircraft_parameters['CD_3P'] = 0.08
    aircraft_parameters['CD_air_LG_down'] = 0.111
    aircraft_parameters['CD_air_LG_up'] = 0.081

    aircraft_geometry = {}
    aircraft_geometry['fuselage_surface'] = 21.1
    aircraft_geometry['fuselage_length'] = 22.28
    aircraft_geometry['flap_deflection_TO'] = 10
    aircraft_geometry['flap_deflection_LD'] = 35 
    aircraft_geometry['main_landing_gear_number'] = 2
    aircraft_geometry['nose_landig_gear_number'] = 1

    aircraft_geometry['main_landing_gear_length'] = 1.88 
    aircraft_geometry['nose_landing_gear_length'] = 1.21
    aircraft_geometry['main_landing_gear_wheels'] = 2
    aircraft_geometry['nose_landing_gear_wheels'] = 2
    aircraft_geometry['wing_flap_type1_position'] = 1 
    aircraft_geometry['wing_flap_type2_position'] = 0
    aircraft_geometry['slats_position'] = 1
    aircraft_geometry['slots_number'] = 2
    aircraft_geometry['main_landing_gear_position'] = 1 
    aircraft_geometry['main_landing_gear_position'] = 1
    aircraft_geometry['altitude_retracted'] = 0
    aircraft_geometry['delta_ISA_retracted'] = 0

    engine_parameters = {}
    engine_parameters['throttle_position'] = 1
    engine['fan_rotation'] = 4952
    engine['compressor_rotation'] = 14950

    runaway_parameters = {}
    runaway_parameters['mu_roll'] = 0.03
    runaway_parameters['mu_brake'] = 0.3

    noise_parameters = {}
    noise_parameters['relative_humidity'] = 70
    noise_parameters['landing_lateral_distance_mic'] = 1
    noise_parameters['sideline_lateral_distance_mic'] = 450
    noise_parameters['takeoff_lateral_distance_mic'] = 1
    noise_parameters['landing_longitudinal_distance_mic'] = 2000
    noise_parameters['sideline_longitudinal_distance_mic'] = 0
    noise_parameters['takeoff_longitudinal_distance_mic'] = 6500

    takeoff_noise, sideline_noise, landing_noise = aircraft_noise(takeoff_parameters, landing_parameters,aircraft_parameters,aircraft_geometry,engine_parameters,runaway_parameters,noise_parameters,vehicle)

    takeoff_noise = 0
    sideline_noise = 0
    landing_noise = 0

    return takeoff_noise, sideline_noise, landing_noise

# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================

wing['area'] = 72
aircraft['maximum_takeoff_weight'] = 25579
aircraft['CL_maximum_landing'] = 2.8517
aircraft['CL_maximum_takeoff'] = 2.2517

engine['fan_pressure_ratio'] = 1.6
engine['compressor_pressure_ratio'] = 27
engine['bypass'] = 4
engine['fan_diameter'] = 1
engine['turbine_inlet_temperature'] = 1410

noise_calculation(vehicle)