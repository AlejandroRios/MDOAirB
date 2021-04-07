"""
File name : Network profit function
Author    : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : July 2020
Last edit : February 2021
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This module calculates the network profit following the following steps:
        - Vehicle sizing and checks (airplane_sizing)
        - Revenue calculation (reveneu)
        - Direct operational cost calculation (mission)
        - Profit calculation (network_optimization)

Inputs:
    - Optimization variables (array x)
    - Mutable dictionary with aircraft, perfomance, operations and airports
    departure and destiny information
Outputs:
    - Profit wich is the objective function
TODO's:
    -

"""
# =============================================================================
# IMPORTS
# =============================================================================
from framework.Performance.Mission.mission import mission
from framework.Network.network_optimization import network_optimization
from framework.Economics.revenue import revenue
from framework.Sizing.airplane_sizing_check import airplane_sizing
import pandas as pd
import pickle
import numpy as np
import csv
from datetime import datetime

from framework.utilities.logger import get_logger
from framework.utilities.output import write_optimal_results, write_kml_results


# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
log = get_logger(__file__.split('.')[0])

def objective_function(x, vehicle):
    
    log.info('==== Start network profit module ====')
    start_time = datetime.now()

    # Try running profit calculation. If error appears during run profit = 0
# try:
    # =============================================================================
    # Airplane sizing and checks
    status, vehicle = airplane_sizing(x, vehicle)

    performance = vehicle['performance']
    airport_departure = vehicle['airport_departure']
    airport_destination = vehicle['airport_destination']
    data_airports = pd.read_csv("Database/Airports/airports.csv")
    # =============================================================================
    # If airplane pass checks, status = 0, else status = 1 and profit = 0
    if status == 0:
        log.info('Aircraft passed sizing and checks status: {}'.format(status))

        market_share = 0.1

        # Load origin-destination distance matrix [nm]
        distances_db = pd.read_csv('Database/Distance/distance.csv')
        distances_db = (distances_db.T)
        distances = distances_db.to_dict()  # Convert to dictionaty

        # Load daily demand matrix and multiply by market share (10%)
        demand_db = pd.read_csv('Database//Demand/demand.csv')
        demand_db = round(market_share*(demand_db.T))
        demand = demand_db.to_dict()

        pax_capacity = x[11]  # Passenger capacity

        # Airports:
        # ["FRA", "LHR", "CDG", "AMS",
        #          "MAD", "BCN", "FCO","DUB","VIE","ZRH"]
        departures = ['CD1', 'CD2', 'CD3']
        arrivals = ['CD1', 'CD2', 'CD3']

        # =============================================================================
        log.info('---- Start DOC calculation ----')
        # The DOC is estimated for each city pair and stored in the DOC dictionary
        city_matrix_size = len(departures)*len(arrivals)
        DOC_ik = {}
        fuel_mass = np.zeros((len(departures),len(arrivals)))
        total_mission_flight_time = np.zeros((len(departures),len(arrivals)))
        mach = np.zeros((len(departures),len(arrivals)))
        passenger_capacity = np.zeros((len(departures),len(arrivals)))

        for i in range(len(departures)):
            DOC_ik[departures[i]] = {}

            for k in range(len(arrivals)):
                if (i != k) and (distances[departures[i]][arrivals[k]] <= x[13]):
                    airport_departure['elevation'] = data_airports.loc[data_airports['APT2']
                                                                    == departures[i], 'ELEV'].iloc[0]
                    airport_destination['elevation'] = data_airports.loc[data_airports['APT2']
                                                                        == arrivals[k], 'ELEV'].iloc[0]
                    airport_departure['takeoff_field_length'] = data_airports.loc[data_airports['APT2']
                                                                                == departures[i], 'TORA'].iloc[0]
                    airport_destination['takeoff_field_length'] = data_airports.loc[data_airports['APT2']
                                                                                    == arrivals[k], 'TORA'].iloc[0]
                    mission_range = distances[departures[i]][arrivals[k]]
                    fuel_mass[i][k], total_mission_flight_time[i][k],DOC,mach[i][k],passenger_capacity[i][k] = mission(mission_range,vehicle)

                    DOC_ik[departures[i]][arrivals[k]] = int(DOC*distances[departures[i]][arrivals[k]])                       
                    # print(DOC_ik[(i, k)])
                else:
                    DOC_ik[departures[i]][arrivals[k]] = 0
                    fuel_mass[i][k] = 0
                    total_mission_flight_time[i][k] = 0
                    mach[i][k] = 0
                    passenger_capacity[i][k] = 0

                city_matrix_size = city_matrix_size - 1
                print('INFO >>>> city pairs remaining to finish DOC matrix fill: ',city_matrix_size)

        # np.save('Database/DOC/DOC.npy',DOC_ik)

        with open('Database/DOC/DOC.csv', 'w') as f:
            for key in DOC_ik.keys():
                f.write("%s,%s\n"%(key,DOC_ik[key]))
                

        log.info('Aircraft DOC matrix: {}'.format(DOC_ik))
        # =============================================================================
        log.info('---- Start Network Optimization ----')
        # Network optimization that maximizes the network profit
        profit, vehicle = network_optimization(
            arrivals, departures, distances, demand, DOC_ik, pax_capacity, vehicle)

        log.info('Network profit [$USD]: {}'.format(profit))
        # =============================================================================

        # average_cruise_mach = np.mean(mach)
        # total_passenger_capacity = np.sum(passenger_capacity)
        # total_distance_capacity = np.sum(total_distance_capacity)
        # total_fuel = np.sum(fuel_mass)
        # total_C02 = total_fuel*3.15
        # CO2_coeff = 3.15*total_fuel/(total_passenger_capacity*total_distance_capacity*1.852)

        write_optimal_results(profit, DOC_ik, vehicle)
        write_kml_results(arrivals, departures, profit, vehicle)

    else:
        profit = 0
        log.info(
            'Aircraft did not pass sizing and checks, profit: {}'.format(profit))
# except:

#     profit = 0
#     log.info('Exception ocurred during calculations')
#     log.info('Aircraft not passed sizing and checks, profit: {}'.format(profit))

    end_time = datetime.now()
    log.info('Network profit excecution time: {}'.format(end_time - start_time))
    log.info('==== End network profit module ====')

    return float(profit)



# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
from framework.Database.Aircrafts.baseline_aircraft_parameters import *

#   0   1   2   3    4   5   6   7   8    9   10   11  12   13   14  
# x = [72, 77, 35, 19, -3, 33, 40, 10, 27, 1410, 16, 120, 6, 2280, 41000, 78, 1, 1, 1, 1]
# x = [9.700e+01,9.900e+01,4.400e+01,1.800e+01,-2.000e+00,3.200e+01, 4.800e+01,1.400e+01,3.000e+01,1.462e+03,1.700e+01,6.000e+01, 6.000e+00,1.525e+03,41000, 78, 1, 1, 1, 1] # Prifit ok
# x = [7.300e+01,8.600e+01,2.900e+01,1.600e+01,-5.000e+00,3.400e+01, 4.600e+01,2.000e+01,2.700e+01,1.372e+03,1.800e+01,1.160e+02, 4.000e+00,2.425e+03,41000, 78, 1, 1, 1, 1] # Failed to climb in 50 min
# x = [1.210e+02,9.600e+01,4.100e+01,2.600e+01,-3.000e+00,3.600e+01, 6.200e+01,1.800e+01,2.900e+01,1.478e+03,1.800e+01,6.800e+01, 5.000e+00,1.975e+03,41000, 78, 1, 1, 1, 1] # Failed to climb in 50 min
# x = [7.900e+01,9.400e+01,3.100e+01,2.000e+01,-4.000e+00,3.700e+01, 5.600e+01,1.000e+01,2.900e+01,1.448e+03,1.600e+01,8.200e+01, 5.000e+00,1.825e+03,41000, 78, 1, 1, 1, 1]  # No profit flag fuel
# x = [1.270e+02,7.600e+01,3.600e+01,2.800e+01,-4.000e+00,3.800e+01, 6.000e+01,1.800e+01,3.000e+01,1.432e+03,1.700e+01,8.800e+01, 5.000e+00,1.225e+03,41000, 78, 1, 1, 1, 1] # Prifit ok
# x = [1.150e+02,8.400e+01,4.900e+01,3.200e+01,-2.000e+00,3.600e+01, 5.000e+01,1.400e+01,2.800e+01,1.492e+03,1.900e+01,1.100e+02, 4.000e+00,1.375e+03,41000, 78, 1, 1, 1, 1] # Prifit ok
# x = [1.090e+02,8.100e+01,2.600e+01,2.400e+01,-5.000e+00,4.000e+01, 5.200e+01,1.600e+01,2.700e+01,1.402e+03,1.400e+01,7.400e+01, 4.000e+00,2.125e+03,41000, 78, 1, 1, 1, 1] # No profit flag fuel
# x = [9.100e+01,8.900e+01,3.400e+01,3.000e+01,-3.000e+00,3.900e+01, 6.400e+01,1.200e+01,2.800e+01,1.358e+03,2.000e+01,9.600e+01, 5.000e+00,1.675e+03,41000, 78, 1, 1, 1, 1]  # No profit flag fuel | errors in noise the problem is related to the engine model - Exit gas speed is calculated wrong for certain inputs
# x = [8.500e+01,9.100e+01,3.900e+01,3.400e+01,-3.000e+00,3.300e+01, 5.800e+01,1.200e+01,2.800e+01,1.418e+03,1.600e+01,1.020e+02, 6.000e+00,2.275e+03,41000, 78, 1, 1, 1, 1]  # No profit flag fuel
x = [1.030e+02,7.900e+01,4.600e+01,2.200e+01,-4.000e+00,3.500e+01, 5.400e+01,1.600e+01,2.900e+01,1.388e+03,1.500e+01,5.400e+01, 6.000e+00,1.075e+03,41000, 78, 1, 1, 1, 1] # Prifit ok

x = [int(x) for x in x]
print(x)
start_time = datetime.now()

result = objective_function(x, vehicle)

end_time = datetime.now()
print(result)
print('objective function time: {}'.format(end_time - start_time))
