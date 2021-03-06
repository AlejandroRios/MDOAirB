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
from datetime import datetime

from framework.utilities.logger import get_logger
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
log = get_logger(__file__.split('.')[0])
log.info('==== Start network profit module ====')


def network_profit(x, vehicle):

    start_time = datetime.now()

    # Try running profit calculation. If error appears during run profit = 0
    try:
        # =============================================================================
        # Airplane sizing and checks
        status, vehicle = airplane_sizing(x, vehicle)
        performance = vehicle['performance']
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
            departures = ['CD1', 'CD2', 'CD3', 'CD4',
                            'CD5', 'CD6', 'CD7', 'CD8', 'CD9', 'CD10']
            arrivals = ['CD1', 'CD2', 'CD3', 'CD4',
                        'CD5', 'CD6', 'CD7', 'CD8', 'CD9', 'CD10']
            # =============================================================================
            log.info('---- Start DOC calculation ----')
            # The DOC is estimated for each city pair and stored in the DOC dictionary
            DOC_ik = {}
            for i in departures:
                for k in arrivals:
                    if (i != k) and (distances[i][k] <= x[13]):
                        performance['range'] = distances[i][k]
                        DOC_ik[(i, k)] = float(
                            mission(vehicle))*distances[i][k]
                        # print(DOC_ik[(i, k)])
                    else:
                        DOC_ik[(i, k)] = 0
            log.info('Aircraft DOC matrix: {}'.format(DOC_ik))
            # =============================================================================
            log.info('---- Start Network Optimization ----')
            # Network optimization that maximizes the network profit
            profit = network_optimization(
                distances, demand, DOC_ik, pax_capacity)
            log.info('Network profit [$USD]: {}'.format(profit))
            # =============================================================================

        else:
            profit = 0
            log.info(
                'Aircraft did not pass sizing and checks, profit: {}'.format(profit))
    except:

        profit = 0
        log.info('Exception ocurred during calculations')
        log.info('Aircraft not passed sizing and checks, profit: {}'.format(profit))

    end_time = datetime.now()
    log.info('Network profit excecution time: {}'.format(end_time - start_time))

    return float(profit)

log.info('==== End network profit module ====')
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
# global NN_induced, NN_wave, NN_cd0, NN_CL, num_Alejandro
# num_Alejandro = 100000000000000000000000
# global NN_induced, NN_wave, NN_cd0, NN_CL
# from framework.baseline_aircraft_parameters import *

# x = [117, 8.204561481970153, 0.3229876327660606, 31, -4, 0.3896951781733875, 4.826332970409506, 1.0650795018081771, 27, 1485, 1.6, 101, 4, 2185, 41000, 0.78, 1, 1, 1, 1]
# # x = [73, 8.210260198894748, 0.34131954092766925, 28, -5, 0.32042307969643524, 5.000456116634125, 1.337333818504011, 27, 1442, 1.6, 106, 6, 1979, 41000, 0.78, 1, 1, 1, 1]
# x = [106, 9.208279852593964, 0.4714790814543369, 16, -3, 0.34987438995033143, 6.420120321538892, 1.7349297171205607, 29, 1461, 1.6, 74, 6, 1079, 41000, 0.78, 1, 1, 1, 1]
# result = network_profit(x,vehicle)
# print(result)
