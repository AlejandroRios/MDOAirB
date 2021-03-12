"""
File name : Mission function
Author    : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : September/2020
Last edit : January/2021
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This function performs the mission analysis of the aircraft and computes the DOC.
Inputs:
    - Vehicle dictionary
Outputs:
    - Direct operational cost (DOC)
TODO's:
    -
"""

#  [120, 8.636673441923826, 0.29650319000289793, 18, -4, 0.37975827133924966, 5.65832918409639, 1.6822333661974933, 30, 1465, 1.6, 78, 5, 2162, 41000, 0.78, 1, 1, 1, 1]
# =============================================================================
# IMPORTS
# =============================================================================
import numpy as np
from datetime import datetime
import math

from framework.Attributes.Airspeed.airspeed import (V_cas_to_mach,
                                                    crossover_altitude,
                                                    mach_to_V_cas)
from framework.Attributes.Atmosphere.atmosphere_ISA_deviation import \
    atmosphere_ISA_deviation
# from framework.baseline_aircraft_parameters import *
from framework.Economics.crew_salary import crew_salary
from framework.Economics.direct_operational_cost import direct_operational_cost
from framework.Performance.Analysis.climb_integration import climb_integration
from framework.Performance.Analysis.cruise_performance import \
    cruise_performance
from framework.Performance.Analysis.descent_integration import \
    descent_integration
from framework.Performance.Analysis.maximum_range_cruise import \
    maximum_range_mach
from framework.Performance.Analysis.mission_altitude import (maximum_altitude,
                                                             optimum_altitude)
from framework.Sizing.performance_constraints import (regulated_landing_weight,
                                                      regulated_takeoff_weight)

from framework.Performance.Engine.engine_performance import turbofan

from framework.Weights.weights import aircraft_empty_weight
from framework.Performance.Mission.reserve_fuel import reserve_fuel
from framework.utilities.logger import get_logger
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
log = get_logger(__file__.split('.')[0])


global GRAVITY
GRAVITY = 9.80665
gallon_to_liter = 3.7852
feet_to_nautical_miles = 0.000164579

def mission(mission_range,vehicle):
    start_time = datetime.now()
    log.info('---- Start DOC mission function ----')

    performance = vehicle['performance']

    tolerance = 100

    aircraft = vehicle['aircraft']
    engine = vehicle['engine']
    wing = vehicle['wing']

    airport_departure = vehicle['airport_departure']
    airport_destination = vehicle['airport_destination']

    operations = vehicle['operations']
    performance = vehicle['performance']


    # [kg]
    max_zero_fuel_weight = aircraft['maximum_zero_fuel_weight']
    # [kg]
    operational_empty_weight = aircraft['operational_empty_weight']
    passenger_capacity_initial = aircraft['passenger_capacity']
    engines_number = aircraft['number_of_engines']
    max_engine_thrust = engine['maximum_thrust']
    
    reference_load_factor = 0.85

    heading = 0

    # Operations and certification parameters:
    buffet_margin = 1.3  # [g]
    residual_rate_of_climb = 300  # [ft/min]
    ceiling = 41000  # [ft] UPDATE INPUT!!!!!!!!!
    descent_altitude = 1500
    # Network and mission parameters
    holding_time = 30  # [min]
    fuel_density = 0.81  # [kg/l]
    fuel_price_per_kg = 1.0  # [per kg]
    fuel_price = (fuel_price_per_kg/fuel_density)*gallon_to_liter
    time_between_overhaul = 2500  # [hr]
    taxi_fuel_flow_reference = 5  # [kg/min]
    contingency_fuel_percent = 0.1 
    min_cruise_time = 3  # [min]
    go_around_allowance = 300

    # Initial flight speed schedule
    climb_V_cas = 280
    mach_climb = 0.78
    cruise_V_cas = 310
    descent_V_cas = 310
    mach_descent = 0.78

    delta_ISA = 0

    captain_salary, first_officer_salary, flight_attendant_salary = crew_salary(
        1000)

    regulated_takeoff_mass = regulated_takeoff_weight(vehicle)
    regulated_landing_mass = regulated_landing_weight(vehicle)

    max_takeoff_mass = aircraft['maximum_takeoff_weight'] 
    max_landing_mass = aircraft['maximum_landing_weight']

    takeoff_allowance_mass = 200*max_takeoff_mass/22000
    approach_allowance_mass = 100*max_takeoff_mass/22000
    average_taxi_in_time = 5
    average_taxi_out_time = 10

    payload = round(
        aircraft['passenger_capacity']
        * operations['passenger_mass']
        * reference_load_factor
    )


    initial_altitude = airport_departure['elevation']

    f = 0
    while f == 0:
        step = 500
        out = 0

        while out == 0:

            # Maximum altitude calculation
            max_altitude, rate_of_climb = maximum_altitude(
                vehicle,
                initial_altitude,
                ceiling,
                max_takeoff_mass,
                climb_V_cas,
                mach_climb,
                delta_ISA
            )
            # Optimal altitude calculation
            optim_altitude, rate_of_climb, _ = optimum_altitude(
                vehicle,
                initial_altitude,
                ceiling,
                max_takeoff_mass,
                climb_V_cas,
                mach_climb,
                delta_ISA
            )
            # Maximum altitude with minimum cruise time check
            g_climb = 4/1000
            g_descent = 3/1000
            K1 = g_climb + g_descent
            # Minimum distance at cruise stage
            Dmin = 10*operations['mach_cruise']*min_cruise_time

            K2 = (
                mission_range
                - Dmin
                + g_climb*(airport_departure['elevation'] + 1500)
                + g_descent*(airport_destination['elevation'] + 1500)
            )
            max_altitude_check = K2/K1

            if max_altitude_check > ceiling:
                max_altitude_check = ceiling

            if max_altitude > max_altitude_check:
                max_altitude = max_altitude_check

            if optim_altitude < max_altitude:
                final_altitude = optim_altitude
            else:
                final_altitude = max_altitude

            'TODO: this should be replaced for information from ADS-B'
            # Check for next lower feasible RVSN FK check according to
            # present heading
            final_altitude = 1000*(math.floor(final_altitude/1000))

            flight_level = final_altitude/100
            odd_flight_level = [
                90, 110, 130, 150, 170, 190, 210, 230, 250, 270, 290, 310, 330,
                350, 370, 390, 410, 430, 450, 470, 490, 510
            ]

            even_flight_level = [
                80, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320,
                340, 360, 380, 400, 420, 440, 460, 480, 500, 520
            ]

            if (heading > 0 and heading <= 180):
                flight_level = min(
                    odd_flight_level, key=lambda x: abs(x-flight_level)
                )
                final_altitude = flight_level*100
            elif (heading > 180 and heading <= 360):
                flight_level = min(
                    even_flight_level, key=lambda x: abs(x-flight_level)
                )
                final_altitude = flight_level*100

            # Initial climb fuel estimation
            initial_altitude = initial_altitude + 1500
            _, _, total_burned_fuel0, _ = climb_integration(
                max_takeoff_mass,
                mach_climb,
                climb_V_cas,
                delta_ISA,
                final_altitude,
                initial_altitude,
                vehicle
            )

            # Calculate best cruise mach
            mass_at_top_of_climb = max_takeoff_mass - total_burned_fuel0
            operations['mach_cruise'] = maximum_range_mach(
                mass_at_top_of_climb,
                final_altitude,
                delta_ISA,
                vehicle
            )
            mach_climb = operations['mach_cruise']
            mach_descent = operations['mach_cruise']

            # Recalculate climb with new mach
            final_distance, total_climb_time, total_burned_fuel, final_altitude = climb_integration(
                max_takeoff_mass,
                mach_climb,
                climb_V_cas,
                delta_ISA,
                final_altitude,
                initial_altitude,
                vehicle
            )

            delta = total_burned_fuel0 - total_burned_fuel

            if delta < tolerance:
                out = 1

        mass_at_top_of_climb = max_takeoff_mass - total_burned_fuel

        initial_cruise_altitude = final_altitude

        distance_climb = final_distance*feet_to_nautical_miles

        distance_cruise = mission_range  - distance_climb

        altitude = initial_cruise_altitude
        flag = 1

        while flag == 1:

            transition_altitude = crossover_altitude(
                operations['mach_cruise'],
                cruise_V_cas,
                delta_ISA
            )
            _, _, _, _, _, rho_ISA, _, _ = atmosphere_ISA_deviation(
                initial_cruise_altitude,
                delta_ISA
            )

            if altitude <= 10000:
                mach = V_cas_to_mach(250, altitude, delta_ISA)

            if (altitude > 10000 and altitude <= transition_altitude):
                mach = V_cas_to_mach(cruise_V_cas, altitude, delta_ISA)

            if altitude > transition_altitude:
                mach = operations['mach_cruise']

            # Breguet calculation type for cruise performance
            total_cruise_time, final_cruise_mass = cruise_performance(
                altitude,
                delta_ISA,
                mach,
                mass_at_top_of_climb,
                distance_cruise,
                vehicle
            )

            final_cruise_altitude = altitude

            # Type of descent: 1 = full calculation | 2 = no descent computed
            type_of_descent = 1

            if type_of_descent == 1:

                # Recalculate climb with new mach
                final_distance, total_descent_time, total_burned_fuel, final_altitude = descent_integration(
                    final_cruise_mass,
                    mach_descent,
                    descent_V_cas,
                    delta_ISA,
                    descent_altitude,
                    final_cruise_altitude,
                    vehicle
                )
                distance_descent = final_distance*feet_to_nautical_miles
                distance_mission = distance_climb + distance_cruise + distance_descent
                distance_error = np.abs(mission_range -distance_mission)

                if distance_error <= 1.0:
                    flag = 0
                else:
                    distance_cruise = distance_cruise - distance_error

            if type_of_descent == 2:
                flag = 0
                total_burned_fuel = 0
                final_distance = 0
                total_decent_time = 0
                total_burned_fuel = 0
                final_altitude = 0

        final_mission_mass = final_cruise_mass - total_burned_fuel
        total_mission_burned_fuel = max_takeoff_mass - final_mission_mass
        total_mission_flight_time = total_climb_time + \
            total_cruise_time + total_descent_time
        total_mission_distance = distance_mission

        # Reserve fuel
        reserve_fuel_calculation_type = 0  # 0 if simplified computation | 1 if full computation
        contingency_fuel = contingency_fuel_percent*final_mission_mass

        landing_weight = max_takeoff_mass - total_mission_burned_fuel

        if reserve_fuel_calculation_type == 0:
            reserve_fuel_calculated = reserve_fuel(landing_weight, operations['alternative_airport_distance'], holding_time, delta_ISA,)
            final_reserve_fuel = reserve_fuel_calculated + contingency_fuel
        else:
            fuel_mass_alterative_airport = mission_alternative(vehicle,landing_weight)
            fuel_mass_holding = holding_fuel(altitude, delta_ISA, holding_time, vehicle)
            final_reserve_fuel =fuel_mass_alterative_airport + fuel_mass_holding + contingency_fuel
            

        # Rule of three to estimate fuel flow during taxi
        taxi_fuel_flow = taxi_fuel_flow_reference*max_takeoff_mass/22000
        taxi_in_fuel = average_taxi_in_time*taxi_fuel_flow
        takeoff_fuel = total_mission_burned_fuel + final_reserve_fuel + takeoff_allowance_mass + taxi_in_fuel
        taxi_out_fuel = average_taxi_out_time*taxi_fuel_flow
        total_fuel_on_board = takeoff_fuel + taxi_out_fuel
        remaining_fuel = takeoff_fuel - total_mission_burned_fuel - \
            approach_allowance_mass - taxi_in_fuel

        # Payload range envelope check

        MTOW_ZFW = max_zero_fuel_weight + total_fuel_on_board
        MTOW_LW = max_landing_mass + total_mission_burned_fuel

        delta_1 = max_takeoff_mass - MTOW_ZFW
        delta_2 = total_fuel_on_board - wing['fuel_capacity']
        delta_3 = max_takeoff_mass - MTOW_LW

        extra = (max_takeoff_mass - operational_empty_weight -
                 payload) - takeoff_fuel[0]
        delta = max([delta_1, delta_2, delta_3, extra])

        if delta > tolerance:
            max_takeoff_mass = max_takeoff_mass-delta
        else:
            # Payload reduction if restricted
            max_takeoff_mass = min(
                [max_takeoff_mass, MTOW_ZFW, MTOW_LW])
            payload_calculation = max_takeoff_mass - \
                takeoff_fuel - operational_empty_weight
            if payload_calculation > payload:
                payload = payload
            else:
                payload = payload_calculation

            f = 1

        passenger_capacity = np.round(payload/operations['passenger_mass'])
        load_factor = passenger_capacity/passenger_capacity_initial*100

    # DOC calculation
    fuel_mass = total_mission_burned_fuel + \
        (average_taxi_out_time + average_taxi_in_time)*taxi_fuel_flow
        
    DOC = direct_operational_cost(
        time_between_overhaul,
        total_mission_flight_time,
        fuel_mass,
        operational_empty_weight,
        total_mission_distance,
        max_engine_thrust,
        engines_number,
        0.35*operational_empty_weight,
        max_takeoff_mass)


    log.info('---- End DOC mission function ----')
    end_time = datetime.now()
    log.info('DOC mission execution time: {}'.format(end_time - start_time))

    return(DOC)

# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================


# DOC = mission(400)
# print(DOC)
