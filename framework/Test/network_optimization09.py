"""
File name : Network optimization function
Authors   : Alejandro Rios
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
# from coinor.pulp import *
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

def network_optimization(arrivals, departures, distances, demand,active_airports, doc0, pax_capacity, vehicle):
    log.info('==== Start network optimization module ====')
    # Definition of cities to be considered as departure_airport, first stop, final airport
    departure_airport = departures
    first_stop_airport = arrivals
    final_airport = departures
    operations = vehicle['operations']
    results = vehicle['results']
    # doc0 = np.load('Database/DOC/DOC.npy',allow_pickle=True)
    # doc0 = doc0.tolist() 

    DOC = {}
    for i in departures:
        for k in arrivals:
            if i != k:
                DOC[(i, k)] = np.round(doc0[i][k])
            else:
                DOC[(i, k)] = np.round(doc0[i][k])

    results = vehicle['results']
    # print(DOC)
    # Define minimization problem
    # prob = LpProblem("Network", LpMaximize)
    prob = LpProblem("Network", LpMinimize)

    pax_number = int(operations['reference_load_factor']*pax_capacity)
    average_ticket_price = operations['average_ticket_price']

    planes = {'P1': {'w': pax_number}}
    # =============================================================================
    # Decision variables definition
    # =============================================================================
    # Number of airplanes of a given type flying (i, k):
    nika = LpVariable.dicts('nika', [(i, k) for i in departure_airport
                                     for k in first_stop_airport],
                            0, None, LpInteger)

    # Number of passengers transported from route (i, j, k)
    xijk = LpVariable.dicts('pax_num',
                            [(i,j) for i in departure_airport
                             for j in final_airport],
                            0, None, LpInteger)

    # Route capacity:
    '''
    Route capacity (i, k) defined as the sum of the number of aircraft type P flying the route (i,k) by the pax capacity of the aicraft P
    '''

    prob += lpSum(nika[(i, k)]*DOC[(i, k)] for i in departure_airport for k in first_stop_airport if i != k)
    # =============================================================================
    # Constraints
    # =============================================================================
    # Demand constraint
    for i in departure_airport:
        for j in final_airport:
                if i != j:
                    # print(xijk[(i, j)] == demand[i][j])
                    prob += xijk[(i, j)] == demand[i][j]


    for i in departure_airport:
        prob += (lpSum(xijk[(i,j)] for j in departure_airport if ((i != j) and (departure_airport.index(i) < final_airport.index(j)))) 
                <=lpSum( nika[(i, j)]*planes['P1']['w'] for j in departure_airport if ((i != j) and (departure_airport.index(i) < final_airport.index(j)))))

    # Capacity constraint II
    for i in departure_airport:
        prob += (lpSum(xijk[(i,j)] for j in departure_airport if ((i != j) and (departure_airport.index(i) > final_airport.index(j)))) 
                <=lpSum( nika[(i, j)]*planes['P1']['w'] for j in departure_airport if ((i != j) and (departure_airport.index(i) > final_airport.index(j)))))
    # =============================================================================
    # Solve linear programming problem (Network optimization)
    # =============================================================================
    log.info('==== Start PuLP optimization ====')
    # prob.solve(GLPK(timeLimit=60*1, msg = 0))
    prob.solve(COIN_CMD())
    log.info('Network optimization status: {}'.format(LpStatus[prob.status]))
    try:
        condition = LpStatus[prob.status]
        if condition != 'Optimal':
            raise ValueError('Optimal network solution NOT found')
    except (ValueError, IndexError):
        exit('Could not complete network optimization')

    print(value(prob.objective))

    list_airplanes = []
    list_of_pax = []
    for v in prob.variables():
        variable_name = v.name
        if variable_name.find('nika') != -1:
            list_airplanes.append(v.varValue)
            # print(v.name, "=", v.varValue)
        if variable_name.find('pax_num') != -1:
            # print(v.name, "=", v.varValue)
            list_of_pax.append(v.varValue)

    list_of_pax = [i for i in list_of_pax if i != 0]

    # Post processing
    min_capacity = 0.5*planes['P1']['w']


    log.info('==== End network optimization module ====')
    return 


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
from framework.Database.Aircrafts.baseline_aircraft_parameters import initialize_aircraft_parameters

vehicle = initialize_aircraft_parameters()
operations = vehicle['operations']
# departures = ['CD0', 'CD1', 'CD2', 'CD3',
#                 'CD4', 'CD5', 'CD6', 'CD7', 'CD8', 'CD9']
# arrivals = ['CD0', 'CD1', 'CD2', 'CD3',
#             'CD4', 'CD5', 'CD6', 'CD7', 'CD8', 'CD9']
# arrivals = ['CD0', 'CD1', 'CD2', 'CD3',
#             'CD4', 'CD5', 'CD6', 'CD7', 'CD8', 'CD9']

departures = ['CD0', 'CD1', 'CD2', 'CD3',
                'CD4']
arrivals = ['CD0', 'CD1', 'CD2', 'CD3',
            'CD4']

# Load origin-destination distance matrix [nm]
distances_db = pd.read_csv('Database/Distance/distance.csv')
distances_db = (distances_db)
distances = distances_db.to_dict()  # Convert to dictionaty

market_share = operations['market_share']
# # Load dai
demand_db= pd.read_csv('Database/Demand/demand.csv')
demand_db= round(market_share*(demand_db.T))
demand = demand_db.to_dict()

df3 = pd.read_csv('Database/DOC/DOC_test2.csv')
df3 = (df3.T)
doc0 = df3.to_dict()

active_airports_db = pd.read_csv('Database/Demand/switch_matrix_full.csv')
active_airports_db = active_airports_db
active_airports = active_airports_db .to_dict()

DOC = {}
for i in departures:
    for k in arrivals:
        if i != k:
            DOC[(i, k)] = np.round(doc0[i][k])
        else:
            DOC[(i, k)] = np.round(doc0[i][k])


Demand = {}

for i in departures:
    for k in arrivals:
        if i != k:
            Demand[(i, k)] = np.round(demand[i][k])
        else:
            Demand[(i, k)] = 100000000

# DOC = np.load('Database/DOC/DOC.npy',allow_pickle=True)
# DOC = DOC.tolist() 
# print(DOC)
pax_capacity = 130

print(network_optimization(arrivals, departures, distances, demand,active_airports, doc0, pax_capacity, vehicle))

# # print(Demand)


