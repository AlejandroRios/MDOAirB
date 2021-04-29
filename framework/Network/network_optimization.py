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

    # DOC = doc0


    results = vehicle['results']
    # print(DOC)
    # Define minimization problem
    # prob = LpProblem("Network", LpMaximize)
    prob = LpProblem("Network", LpMinimize)

    pax_number = int(operations['reference_load_factor']*pax_capacity)
    average_ticket_price = operations['average_ticket_price']

    revenue_ik = {}
    for i in range(len(departure_airport)):
        revenue_ik[departure_airport[i]] = {}
        for k in range(len(first_stop_airport)):
            if (i != k) and (active_airports[departure_airport[i]][first_stop_airport[k]] == 1):
                revenue_ik[departure_airport[i]][first_stop_airport[k]] = round(
                    revenue(demand[departure_airport[i]][first_stop_airport[k]], distances[departure_airport[i]][first_stop_airport[k]], pax_capacity, pax_number, average_ticket_price))
            else:
                revenue_ik[departure_airport[i]][first_stop_airport[k]] = 0

    revenue_ik2 ={}
    for i in departures:
        for k in arrivals:
            if i != k:
                revenue_ik2[(i, k)] = np.round(revenue_ik[i][k])
            else:
                revenue_ik2[(i, k)] = np.round(revenue_ik[i][k])    

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
                            [(i,k,j) for i in departure_airport
                             for k in first_stop_airport
                             for j in final_airport],
                            0, None, LpInteger)

    # Route capacity:
    '''
    Route capacity (i, k) defined as the sum of the number of aircraft type P flying the route (i,k) by the pax capacity of the aicraft P
    '''
    # G = {}
    # for i in departure_airport:
    #     for k in first_stop_airport:
    #         G[(i, k)] = nika[(i, k)]*planes['P1']['w']

    # =============================================================================
    # Objective function
    # =============================================================================

    # prob += lpSum(revenue_ik) - lpSum(nika[(i, k)]*DOC[(i, k)]
    #                                      for i in departure_airport for k in first_stop_airport if i != k)


    # prob += lpSum(revenue_ik2[(i, k)] - nika[(i, k)]*DOC[(i, k)]
    #                                      for i in departure_airport for k in first_stop_airport if i != k)

    # prob += lpSum((planes['P1']['w']*average_ticket_price) - (nika[(i, k)]*DOC[(i, k)])
    #                                      for i in departure_airport for k in first_stop_airport if i != k)

    prob += lpSum(nika[(i, k)]*DOC[(i, k)] for i in departure_airport for k in first_stop_airport if i != k)
    # =============================================================================
    # Constraints
    # =============================================================================
    # Demand constraint
    for i in departure_airport:
        for k in first_stop_airport:
            for j in final_airport:
                if i != j:
                    prob += lpSum(xijk[(i, j, k)]
                                     for k in first_stop_airport) == demand[i][j]

    # Capacity constraint I
    for i in departure_airport:
        for k in first_stop_airport:
            for j in final_airport:
                if i != k:
                    prob += lpSum(xijk[(i, k, j)]
                                     for j in final_airport) <= nika[(i, k)]*planes['P1']['w']

    # Capacity constraint II
    
    for i in departure_airport:
        for k in first_stop_airport:
            for j in final_airport:
            
                if k != j:
                    prob += lpSum(xijk[(j,k,i)]
                                     for i in departure_airport) <= nika[(j, k)]*planes['P1']['w']
    # =============================================================================
    # Solve linear programming problem (Network optimization)
    # =============================================================================
    log.info('==== Start PuLP optimization ====')
    # prob.solve(GLPK(timeLimit=60*5, msg = 0))
    prob.solve(GLPK(timeLimit=60*5, msg = 0))
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
        if variable_name.find('pax_num') != -1:
            # print(v.name, "=", v.varValue)
            list_of_pax.append(v.varValue)

    list_of_pax = [i for i in list_of_pax if i != 0]

    # Post processing
    min_capacity = 0.5*planes['P1']['w']

    def flatten_dict(dd, separator ='_', prefix =''):
        return { prefix + separator + k if prefix else k : v
                for kk, vv in dd.items()
                for k, v in flatten_dict(vv, separator, kk).items()
                } if isinstance(dd, dict) else { prefix : dd }


    idx = 0
    fraction = np.zeros((len(arrivals),len(arrivals)))
    for i in range(len(arrivals)):
        for j in range(len(departures)):
            if i==j:
                fraction[i][j] = 0
            else:
                fraction[i][j] = list_of_pax[idx]
                idx = idx+1

    fraction = fraction/planes['P1']['w']

    fraction_1 = np.floor(fraction)
    fraction_2 = fraction-fraction_1

    revenue_1 = (fraction_1*planes['P1']['w'])*average_ticket_price
    revenue_2 = np.zeros((len(arrivals),len(arrivals)))
    for i in range(len(arrivals)):
        for j in range(len(departures)):
            if fraction_2[i][j] > min_capacity:
                revenue_2[i][j] = fraction_2[i][j]*average_ticket_price*planes['P1']['w']
            else:
                revenue_2[i][j] = 0

    revenue_mat = revenue_1+revenue_2
    revenue_tot = np.sum(revenue_mat)

    idx = 0
    list_of_airplanes_processed = np.zeros((len(arrivals),len(arrivals)))
    for i in range(len(arrivals)):
        for j in range(len(departures)):
            if fraction_2[i][j] > min_capacity:
                fracction_aux = 1
            else:
                fracction_aux = 0
            list_of_airplanes_processed[i][j]= fraction_1[i][j]+fracction_aux


    DOCmat =  np.zeros((len(arrivals),len(arrivals)))
    for i in range(len(departures)):
        for j in range(len(arrivals)):
            if i != k:
                DOCmat[i][j] = np.round(doc0[arrivals[i]][departures[j]])
            else:
                DOCmat[i][j] = 0


    DOC_proccessed = np.zeros((len(arrivals),len(arrivals)))
    for i in range(len(arrivals)):
        for j in range(len(departures)):
            DOC_proccessed[i][j] = DOCmat[i][j]*list_of_airplanes_processed[i][j]

    list_pax_processed = np.zeros((len(arrivals),len(arrivals)))
    for i in range(len(arrivals)):
        for j in range(len(departures)):
            if fraction_2[i][j] > min_capacity:
                fracction_aux = fraction_2[i][j] 
            else:
                fracction_aux = 0

            list_pax_processed[i][j] = fraction_1[i][j]*planes['P1']['w'] + fracction_aux*planes['P1']['w']


    results['aircrafts_used']= np.sum(list_of_airplanes_processed)
    results['covered_demand'] = np.sum(list_pax_processed)
    results['total_revenue'] = revenue_tot
    airplanes_ik = {}
    n = 0
    for i in range(len(departures)):
        airplanes_ik[departures[i]] = {}
        for k in range(len(arrivals)):
            # print(list_airplanes[n])
            airplanes_ik[(departures[i],arrivals[k])] = list_of_airplanes_processed[i][k]


    list_airplanes_db = pd.DataFrame(list_of_airplanes_processed)
    list_airplanes_db.to_csv('Database/Network/frequencies.csv')

    airplanes_flatt = flatten_dict(airplanes_ik)
    
    np.save('Database/Network/frequencies.npy', airplanes_flatt) 

    list_of_pax_db = pd.DataFrame(list_pax_processed)

    list_of_pax_db = list_of_pax_db.loc[~(list_of_pax_db==0).all(axis=1)]
    # print(list_of_pax)

    list_of_pax_db.to_csv('Database/Network/pax.csv')

    DOC_tot = np.sum(DOC_proccessed)

    
    profit = np.int(1.0*revenue_tot - 1.2*DOC_tot)

    results['profit'] = np.round(profit)
    results['total_cost'] = np.round(DOC_tot)

    # kpi_df1 = pd.DataFrame.from_dict(xijk, orient="index", 
    #                             columns = ["variable_object"])
    # kpi_df1.index =  pd.MultiIndex.from_tuples(kpi_df1.index, 
    #                             names=["column_i", "column_j", "column_k"])
    # kpi_df1.reset_index(inplace=True)

    pax_number_flatt = list_pax_processed.flatten()
    
    pax_number_df = pd.DataFrame({'pax_number':pax_number_flatt})
    kpi_df1 = pd.DataFrame()
    # print(pax_number_df)
    kpi_df1['pax_number'] = pax_number_df['pax_number'].values
    # print(kpi_df1["pax_number"])

    # kpi_df1.drop(columns=["variable_object"], inplace=True)
    kpi_df1.to_csv("Test/optimization_solution01.csv")

    ############################################################################################
    kpi_df2 = pd.DataFrame.from_dict(nika, orient="index", 
                                    columns = ["variable_object"])
    kpi_df2.index =  pd.MultiIndex.from_tuples(kpi_df2.index, 
                                names=["origin", "destination"])
    kpi_df2.reset_index(inplace=True)

    kpi_df2["aircraft_number"] =  kpi_df2["variable_object"].apply(lambda item: item.varValue)

    kpi_df2.drop(columns=["variable_object"], inplace=True)


    
    # print(distances)

    # distances_flatt = flatten_dict(distances)
    # doc_flatt = flatten_dict(DOC)
    # demand_flatt = flatten_dict(demand)
    # revenue_flatt = flatten_dict(revenue_ik)

    distances_flatt = flatten_dict(distances)
    # doc_flatt = flatten_dict(DOC)
    demand_flatt = flatten_dict(demand)
    revenue_flatt = revenue_mat.flatten()
    doc_flatt = DOC_proccessed.flatten()

    doc_df = pd.DataFrame({'doc':doc_flatt})
    revenue_df = pd.DataFrame({'revenue':revenue_flatt})


    distance_df =  pd.DataFrame.from_dict(distances_flatt,orient="index",columns=['distances'])
    # doc_df =  pd.DataFrame.from_dict(doc_flatt,orient="index",columns=['doc'])
    demand_df =  pd.DataFrame.from_dict(demand_flatt,orient="index",columns=['demand'])
    # revenue_df =  pd.DataFrame.from_dict(revenue_flatt,orient="index",columns=['revenue'])

    kpi_df2['distances'] = distance_df['distances'].values
    kpi_df2['doc'] = doc_df['doc'].values
    kpi_df2['demand'] = demand_df['demand'].values
    kpi_df2['revenue'] = revenue_df['revenue'].values

    n = len(arrivals)

    kpi_df2['active_arcs'] = np.where(kpi_df2["aircraft_number"] > 0, 1, 0)
    X = kpi_df2['active_arcs'].to_numpy()
    X = np.reshape(X, (n,n))

    Distances = kpi_df2['distances'].to_numpy()
    Distances = np.reshape(Distances, (n,n))

    Demand = kpi_df2['demand'].to_numpy()
    Demand = np.reshape(Demand, (n,n))


    N = 0
    for i,j in np.ndindex(X.shape):
        if X[i,j] == 1:
            N = N+1

    DON = np.zeros(n)
    for i in range(n):
        DON[i] = 0
        for j in range(n):
            if i != n:
                if X[i,j] == 1:
                    DON[i] = DON[i]+1
    
    results['avg_degree_nodes'] = np.mean(DON)

    R = 500
    C = np.zeros(n)
    for i in range(n):
        CON =0
        MAXCON = 0
        for j in range(n):
            if i != j:
                if Distances[i,j] <= R:
                    MAXCON = MAXCON + 1
                    if X[i,j] == 1:
                        CON = CON+1
        if MAXCON>0:
            C[i] = CON/MAXCON
        else:
            C[i] = 0

    results['average_clustering'] = np.mean(C)


    LF = np.ones((n,n))
    FREQ = X

    # NPAX = np.zeros((n,n))
    # for i in range(n):
    #     for j in range(n):
    #         if (i==j or X[i,j]==0):
    #             f = 0
    #             NPAX[i,j] = 0
    #             FREQ[i,j] = 0
    #         else:
    #             NPAX[i,j] = np.round(pax_number)
    #             f = round(Demand[i,j]/NPAX[i,j])
    #             FREQ[i,j] = f

    results['number_of_frequencies'] = np.sum(list_of_airplanes_processed)


    


    log.info('==== End network optimization module ====')
    return profit, vehicle, kpi_df1, kpi_df2


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
# from framework.Database.Aircrafts.baseline_aircraft_parameters import initialize_aircraft_parameters

# vehicle = initialize_aircraft_parameters()
# operations = vehicle['operations']
# departures = ['CD1', 'CD2', 'CD3', 'CD4',
#                 'CD5', 'CD6', 'CD7', 'CD8', 'CD9', 'CD10']
# arrivals = ['CD1', 'CD2', 'CD3', 'CD4',
#             'CD5', 'CD6', 'CD7', 'CD8', 'CD9', 'CD10']

# # departures = ['CD1', 'CD2', 'CD3', 'CD4',
# #                 'CD5']
# # arrivals = ['CD1', 'CD2', 'CD3', 'CD4',
# #             'CD5']

# # Load origin-destination distance matrix [nm]
# distances_db = pd.read_csv('Database/Distance/distance.csv')
# distances_db = (distances_db)
# distances = distances_db.to_dict()  # Convert to dictionaty

# market_share = operations['market_share']
# # # Load dai
# demand_db= pd.read_csv('Database/Demand/demand.csv')
# demand_db= round(market_share*(demand_db))
# demand = demand_db.to_dict()

# df3 = pd.read_csv('Database/DOC/DOC_test2.csv')
# df3 = (df3)
# doc0 = df3.to_dict()

# active_airports_db = pd.read_csv('Database/Demand/switch_matrix_full.csv')
# active_airports_db = active_airports_db
# active_airports = active_airports_db .to_dict()

# DOC = {}
# for i in departures:
#     for k in arrivals:
#         if i != k:
#             DOC[(i, k)] = np.round(doc0[i][k])
#         else:
#             DOC[(i, k)] = np.round(doc0[i][k])


# Demand = {}

# for i in departures:
#     for k in arrivals:
#         if i != k:
#             Demand[(i, k)] = np.round(demand[i][k])
#         else:
#             Demand[(i, k)] = 100000000

# # DOC = np.load('Database/DOC/DOC.npy',allow_pickle=True)
# # DOC = DOC.tolist() 
# # print(DOC)
# pax_capacity = 130

# print(network_optimization(arrivals, departures, distances, demand,active_airports, doc0, pax_capacity, vehicle))

# # # print(Demand)


