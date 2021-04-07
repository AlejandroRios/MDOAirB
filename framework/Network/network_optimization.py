"""
File name : Network optimization function
Author    : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : June 2020
Last edit : January 2021
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This function performs the network optimization using linear programming
    algorithm (1-stop model)
Inputs:
    - Distance matrix
    - Demand matrix
    - DOC matrix
    - Pax capacity
Outputs:
    - Network Profit [USD]
    - Route frequencies 
TODO's:
    -
"""
# =============================================================================
# IMPORTS
# =============================================================================
from collections import defaultdict
import numpy as np
from pulp import *
import pandas as pd
import csv
import sys 
from framework.Economics.revenue import revenue
from framework.utilities.logger import get_logger
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
log = get_logger(__file__.split('.')[0])

def network_optimization(arrivals, departures, distances, demand, doc0, pax_capacity, vehicle):
    log.info('==== Start network optimization module ====')
    # Definition of cities to be considered as departure_airport, first stop, final airport
    departure_airport = departures
    first_stop_airport = arrivals
    final_airport = departures

    operations = vehicle['operations']

    # doc0 = np.load('Database/DOC/DOC.npy',allow_pickle=True)
    # doc0 = doc0.tolist() 

    DOC = {}
    for i in departures:
        for k in arrivals:
            if i != k:
                DOC[(i, k)] = np.round(doc0[i][k])
            else:
                DOC[(i, k)] = np.round(doc0[i][k])

    # DOC = doc0


    results = vehicle['results']
    # print(DOC)
    # Define minimization problem
    prob = LpProblem("Network", LpMaximize)

    pax_number = int(operations['load_factor']*pax_capacity)
    revenue_ik = defaultdict(dict)
    for i in departure_airport:
        for k in first_stop_airport:
            if i != k:
                revenue_ik[(i, k)] = round(
                    revenue(demand[i][k], distances[i][k], pax_capacity, pax_number))
            else:
                revenue_ik[(i, k)] = 0

    #print(revenue_ik)

    planes = {'P1': {'w': pax_number}}
    # =============================================================================
    # Decision variables definition
    # =============================================================================
    # Number of airplanes of a given type flying (i, k):
    nika = LpVariable.dicts('nika', [(i, k) for i in departure_airport
                                     for k in first_stop_airport],
                            0, None, LpInteger)

    # Number of passengers transported from route (i, j, k)
    xijk = LpVariable.dicts('numPac',
                            [(i, j, k) for i in departure_airport
                             for j in final_airport
                             for k in first_stop_airport],
                            0, None, LpInteger)

    # Route capacity:
    '''
    Route capacity (i, k) defined as the sum of the number of aircraft type P flying the route (i,k) by the pax capacity of the aicraft P
    '''
    G = {}
    for i in departure_airport:
        for k in first_stop_airport:
            G[(i, k)] = nika[(i, k)]*planes['P1']['w']

    # =============================================================================
    # Objective function
    # =============================================================================

    prob += lpSum(revenue_ik) - lpSum(nika[(i, k)]*2*DOC[(i, k)]
                                         for i in departure_airport for k in first_stop_airport if i != k)
    # =============================================================================
    # Constraints
    # =============================================================================
    # Demand constraint
    for i in departure_airport:
        for j in final_airport:
            for k in first_stop_airport:
                if i != j:
                    prob += lpSum(xijk[(i, j, k)]
                                     for k in first_stop_airport) == demand[i][j]

    # Capacity constraint I
    for i in departure_airport:
        for j in final_airport:
            for k in first_stop_airport:
                if i != k:
                    prob += lpSum(xijk[(i, j, k)]
                                     for j in final_airport) <= G[(i, k)]

    # Capacity constraint II
    for i in departure_airport:
        for j in final_airport:
            for k in first_stop_airport:
                if k != j:
                    prob += lpSum(xijk[(i, j, k)]
                                     for i in departure_airport) <= G[(j, k)]

    # =============================================================================
    # Solve linear programming problem (Network optimization)
    # =============================================================================
    log.info('==== Start PuLP optimization ====')
    prob.solve(GLPK(timeLimit=60*3, msg = 0))
    log.info('Network optimization status: {}'.format(LpStatus[prob.status]))
    try:
        condition = LpStatus[prob.status]
        if condition != 'Optimal':
            raise ValueError('Optimal network solution NOT found')
    except (ValueError, IndexError):
        exit('Could not complete network optimization')

    list_airplanes = []
    list_of_pax = []
    for v in prob.variables():
        variable_name = v.name
        if variable_name.find('nika') != -1:
            list_airplanes.append(v.varValue)
            # print(v.name, "=", v.varValue)
        if variable_name.find('numPac') != -1:
            # print(v.name, "=", v.varValue)
            list_of_pax.append(v.varValue)
    
    results['aircrafts_used']= sum(list_airplanes)
    results['covered_demand'] = sum(list_of_pax)

    airplanes_ik = {}
    n = 0
    for i in departures:
        for k in arrivals:
            if i != k:
                # print(list_airplanes[n])
                airplanes_ik[(i,k)] = list_airplanes[n] 
                n = n+1
            else:
                airplanes_ik[(i,k)] = 0

    list_airplanes_db = pd.DataFrame(list_airplanes)
    list_airplanes_db.to_csv('Database/Network/frequencies.csv')
    
    np.save('Database/Network/frequencies.npy', airplanes_ik) 


    list_of_pax_db = pd.DataFrame(list_of_pax)
    list_of_pax_db.to_csv('Database/Network/pax.csv')

    results = vehicle['results']
    profit = value(prob.objective)
    
    results['profit'] = profit


    log.info('==== End network optimization module ====')
    return profit, vehicle


# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
# # Load origin-destination distance matrix [nm]
# distances_db = pd.read_csv('Database/Distance/distance.csv')
# distances_db = (distances_db.T)
# distances = distances_db.to_dict()  # Convert to dictionaty

# # Load daily demand matrix and multiply by market share (10%)
# demand_db = pd.read_csv('Database//Demand/demand.csv')
# demand_db = round(market_share*(demand_db.T))
# demand = demand_db.to_dict()
# from framework.Database.Aircrafts.baseline_aircraft_parameters import *

# departures = ['CD1', 'CD2', 'CD3', 'CD4',
#                 'CD5', 'CD6', 'CD7', 'CD8', 'CD9', 'CD10']
# arrivals = ['CD1', 'CD2', 'CD3', 'CD4',
#             'CD5', 'CD6', 'CD7', 'CD8', 'CD9', 'CD10']

# Load origin-destination distance matrix [nm]
# distances_db = pd.read_csv('Database/Distance/distance.csv')
# distances_db = (distances_db.T)
# distances = distances_db.to_dict()  # Convert to dictionaty

# market_share = 0.1
# # Load dai
# demand_db= pd.read_csv('Database/Demand/demand.csv')
# demand_db= round(market_share*(demand_db.T))
# demand = demand_db.to_dict()

# df3 = pd.read_csv('Database/DOC/doc2.csv')
# df3 = (df3.T)
# doc0 = df3.to_dict()

# DOC = {}
# for i in departures:
#     for k in arrivals:
#         if i != k:
#             DOC[(i, k)] = np.round(doc0[i][k])
#         else:
#             DOC[(i, k)] = np.round(doc0[i][k])

# DOC = np.load('Database/DOC/DOC.npy',allow_pickle=True)
# DOC = DOC.tolist() 
# print(DOC)
# pax_capacity = 101

# network_optimization(arrivals, departures, distances, demand, DOC, pax_capacity,vehicle)


