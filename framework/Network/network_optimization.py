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

def network_optimization(arrivals, departures, distances, demand, active_airports, doc0, pax_capacity, vehicle):
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

    # Define minimization problem
    # prob = LpProblem("Network", LpMaximize)
    prob = LpProblem("Network", LpMinimize)

    pax_number = int(operations['reference_load_factor']*pax_capacity)
    average_ticket_price = operations['average_ticket_price']

    distances_list = []
    for i in departures:
        for j in arrivals:
            if i != j and i < j:
                distances_list.append(distances[i][j])
    for i in departures:
        for j in arrivals:
            if i != j and i > j:
                distances_list.append(distances[i][j])

    demand_list = []
    for i in departures:
        for j in arrivals:
            if i != j and i < j:
                demand_list.append(demand[i][j])
    for i in departures:
        for j in arrivals:
            if i != j and i > j:
                demand_list.append(demand[i][j])

    demand_sum = sum(demand_list)

    switch_list = []
    for i in departures:
        for j in arrivals:
            if i != j and i < j:
                switch_list.append(active_airports[i][j])
    for i in departures:
        for j in arrivals:
            if i != j and i > j:
                switch_list.append(active_airports[i][j])

    docs_list = []
    for i in departures:
        for j in arrivals:
            if i != j and i < j:
                docs_list.append(doc0[i][j])
    for i in departures:
        for j in arrivals:
            if i != j and i > j:
                docs_list.append(doc0[i][j])

    froms_list = []
    for i in range(len(departures)):
        for j in range(len(arrivals)):
            if i != j and i < j:
                froms_list.append(i)

    for i in range(len(arrivals)):
        for j in range(len(departures)):
            if i != j and i > j:
                froms_list.append(i)
    # print(froms_list)
    tos_list = []
    for i in range(len(departures)):
        for j in range(len(arrivals)):
            if i != j and i < j:
                tos_list.append(j)

    for i in range(len(arrivals)):
        for j in range(len(departures)):
            if i != j and i > j:
                tos_list.append(j)

    arcs = list(range(len(froms_list)))
    planes = {'P1': {'w': pax_number}}

    avg_capacity = pax_number
    avg_vel = 400
    avg_vel = [avg_vel]*len(froms_list)
    avg_grnd_time = 0.5
    time_allowed = 13
    allowed_planes = [round(13/((distances_list[i]/avg_vel[i])+avg_grnd_time)) for i in range(len(arcs))]

    nodes = list(range(len(departures)*2))

    demand_aux = []
    supply_aux = []
    for i in departures:
        aux1 = [demand[i][j] for j in arrivals if i != j and i > j ]
        demand_aux.append(sum(aux1))
        aux2 = [demand[i][j] for j in arrivals if i != j and i < j ]
        supply_aux.append(sum(aux2))

    sup_dem_ij = [x - y for x, y in zip(demand_aux, supply_aux)]
    sup_dem_ji = [x - y for x, y in zip(supply_aux, demand_aux)]

    prob = LpProblem("NetOptMin", LpMinimize)
    # prob = LpProblem("NetOptMax", LpMaximize)

    flow = LpVariable.dicts("flow",(arcs),0,None,LpInteger)
    aircrafts = LpVariable.dicts("aircrafts",(arcs),0,10,LpInteger)

    prob += lpSum([aircrafts[i]*docs_list[i] for i in range(len(arcs))])
    # prob += lpSum([flow[i]*average_ticket_price for i in range(len(arcs))]) - lpSum([aircrafts[i]*docs_list[i] for i in range(len(arcs))])
    # prob += lpSum([demand_list[i]*distances_list[i]*((flow[i]*average_ticket_price)/(flow[i]*distances_list[i])) for i in range(len(arcs))])  - lpSum([aircrafts[i]*docs_list[i] for i in range(len(arcs))])


    prob += lpSum([flow[i] for i in range(len(arcs))]) == demand_sum

    for i in range(0,len(nodes)//2):
            prob += lpSum(flow[j] for j in range(0,len(arcs)//2) if tos_list[j] == i) - lpSum(flow[j] for j in range(0,len(arcs)//2) if froms_list[j] == i) == sup_dem_ij[i]

    for i in range(0,len(nodes)//2):
            prob += lpSum(flow[j] for j in range(len(arcs)//2,len(arcs)) if tos_list[j] == i) - lpSum(flow[j] for j in range(len(arcs)//2,len(arcs)) if froms_list[j] == i) == sup_dem_ji[i]
            
    for i in arcs:
        prob += flow[i] <= aircrafts[i]*avg_capacity



    # =============================================================================
    # Solve linear programming problem (Network optimization)
    # =============================================================================
    log.info('==== Start PuLP optimization ====')
    # prob.solve(GLPK(timeLimit=60*5, msg = 0))
    prob.solve(COIN_CMD(timeLimit=60*5))

    log.info('==== Start PuLP optimization ====')
    # print('Problem solution:',value(prob.objective))

    # for v in prob.variables():
    #     print(v.name, "=", v.varValue)

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
        if variable_name.find('aircrafts') != -1:
            list_airplanes.append(v.varValue)
            # print(v.name, "=", v.varValue)
        if variable_name.find('flow') != -1:
            # print(v.name, "=", v.varValue)
            list_of_pax.append(v.varValue)

    # print('flow',sum(list_of_pax))

    # Post processing
    min_capacity = 0.5

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

    list_size = len(departures)**2 - len(departures)
    fraction = np.zeros((len(departures),len(departures)))
    idx = 0
    while idx<list_size/2:
        for i in range(len(departures)):
            for j in range(len(departures)):
                if j>i:
                    fraction[i][j] = list_of_pax[idx]
                    idx = idx+1
    while idx<list_size:
        for i in range(len(departures)):
            for j in range(len(departures)):
                if j<i:
                    fraction[i][j] = list_of_pax[idx]
                    idx = idx+1

    print('Flow matrix:',fraction)

    fraction = fraction/planes['P1']['w']

    fraction_1 = np.floor(fraction)
    fraction_2 = fraction-fraction_1

    fraction_1_list = []
    for i in range(len(departures)):
        for j in range(len(arrivals)):
            if i != j and i < j:
                fraction_1_list.append(fraction_1[i][j])
    for i in range(len(departures)):
        for j in range(len(arrivals)):
            if i != j and i > j:
                fraction_1_list.append(fraction_1[i][j])

    fraction_2_list = []
    for i in range(len(departures)):
        for j in range(len(arrivals)):
            if i != j and i < j:
                fraction_2_list.append(fraction_2[i][j])
    for i in range(len(departures)):
        for j in range(len(arrivals)):
            if i != j and i > j:
                fraction_2_list.append(fraction_2[i][j])

    revenue_1_list = []
    for i in range(len(fraction_1_list)):
        if (list_of_pax[i] <= 0 or fraction_1_list[i] <= 0):
            revenue_1_list.append(0)
        else:
            revenue_1_list.append(demand_list[i]*distances_list[i]*(list_of_pax[i]*fraction_1_list[i]*average_ticket_price)/(list_of_pax[i]*fraction_1_list[i]*distances_list[i]))
            

    revenue_1_list = [0 if x != x else x for x in revenue_1_list]

    revenue_2_list = []
    for i in range(len(fraction_2_list)):
        if (list_of_pax[i] <= 0 or fraction_2_list[i] <= 0):
            revenue_2_list.append(0)
        else:
            revenue_2_list.append(demand_list[i]*distances_list[i]*(list_of_pax[i]*fraction_2_list[i]*average_ticket_price)/(list_of_pax[i]*fraction_2_list[i]*distances_list[i]))
    revenue_2_list = [0 if x != x else x for x in revenue_2_list]

    revenue_tot2 = [x + y for x, y in zip(revenue_1_list,revenue_2_list)]
    revenue_tot2 = sum(revenue_tot2)

    revenue_1 = (fraction_1*pax_number)*average_ticket_price
    revenue_2 = np.zeros((len(arrivals),len(arrivals)))
    for i in range(len(arrivals)):
        for j in range(len(departures)):
            if fraction_2[i][j] > min_capacity:
                revenue_2[i][j] = fraction_2[i][j]*pax_number*average_ticket_price
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

    print('Aircraft matrix:',list_of_airplanes_processed)

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

    print('margin',profit/revenue_tot)
    print('profit',profit)


    pax_number_flatt = list_pax_processed.flatten()
    
    pax_number_df = pd.DataFrame({'pax_number':pax_number_flatt})
    kpi_df1 = pd.DataFrame()
    # print(pax_number_df)
    kpi_df1['pax_number'] = pax_number_df['pax_number'].values
    # print(kpi_df1["pax_number"])

    # kpi_df1.drop(columns=["variable_object"], inplace=True)
    kpi_df1.to_csv("Test/optimization_solution01.csv")

    ############################################################################################
    def restructure_data(aux_mat,n):
        aux_mat = np.reshape(aux_mat, (n,n-1))
        new_mat = np.zeros((n,n))
        for i in range(n):
            for j in range(n):
                if i == j:
                    new_mat[i][j] = 0
                elif j<=i:
                    new_mat[i][j] = aux_mat[i][j]
                else:
                    new_mat[i][j] = aux_mat[i][j-1]
        return new_mat

    n = len(arrivals)

    # aircrafts_aux = np.reshape(aircrafts, (n,n-1))

    kpi_df2 = pd.DataFrame.from_dict(aircrafts, orient="index", 
                                    columns = ["variable_object"])
    # kpi_df2.idx =  pd.MultiIndex.from_tuples(kpi_df2.idx, 
    #                             names=["origin", "destination"])
    kpi_df2.reset_index(inplace=True)

    kpi_df2["aircraft_number"] =  kpi_df2["variable_object"].apply(lambda item: item.varValue)

    kpi_df2.drop(columns=["variable_object"], inplace=True)


    distances_flatt = flatten_dict(distances)
    # doc_flatt = flatten_dict(DOC)
    demand_flatt = flatten_dict(demand)
    revenue_flatt = revenue_mat.flatten()
    doc_flatt = DOC_proccessed.flatten()

    doc_df = pd.DataFrame({'doc':doc_flatt})
    revenue_df = pd.DataFrame({'revenue':revenue_flatt})


    distance_df =  pd.DataFrame.from_dict(distances_flatt,orient="index",columns=['distances'])
    # doc_df =  pd.DataFrame.from_dict(doc_flatt,orient="idx",columns=['doc'])
    demand_df =  pd.DataFrame.from_dict(demand_flatt,orient="index",columns=['demand'])
    # revenue_df =  pd.DataFrame.from_dict(revenue_flatt,orient="idx",columns=['revenue'])

    kpi_df2['distances'] = distances_list
    kpi_df2['doc'] = docs_list
    kpi_df2['demand'] = demand_list
    # kpi_df2['revenue'] = revenue_df['revenue'].values
    
    kpi_df2['active_arcs'] = np.where(kpi_df2["aircraft_number"] > 0, 1, 0)
    X = kpi_df2['active_arcs'].to_numpy()
    X = restructure_data(X,n)

    Distances = kpi_df2['distances'].to_numpy()
    Distances = restructure_data(Distances,n)

    Demand = kpi_df2['demand'].to_numpy()
    Demand= restructure_data(Demand,n)

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

    results['number_of_frequencies'] = np.sum(list_of_airplanes_processed)

    log.info('==== End network optimization module ====')
    return profit, vehicle, kpi_df1, kpi_df2


def network_optimization_fix(arrivals, departures, distances, demand, active_airports, doc0, pax_capacity, vehicle):
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

    distances_list = []
    for i in departures:
        for j in arrivals:
            if i != j:
                distances_list.append(distances[i][j])


    demand_list = []
    for i in departures:
        for j in arrivals:
            if i != j:
                demand_list.append(demand[i][j])


    demand_sum = sum(demand_list)

    switch_list = []
    for i in departures:
        for j in arrivals:
            if i != j:
                switch_list.append(active_airports[i][j])


    docs_list = []
    for i in departures:
        for j in arrivals:
            if i != j and i < j:
                docs_list.append(doc0[i][j])
    for i in departures:
        for j in arrivals:
            if i != j and i > j:
                docs_list.append(doc0[i][j])

    froms_list = []
    for i in range(len(departures)):
        for j in range(len(arrivals)):
            if i != j:
                froms_list.append(i)

    # print(froms_list)
    tos_list = []
    for i in range(len(departures)):
        for j in range(len(arrivals)):
            if i != json:
                tos_list.append(j)



    arcs = list(range(len(froms_list)))
    planes = {'P1': {'w': pax_number}}

    avg_capacity = pax_number
    avg_vel = 400
    avg_vel = [avg_vel]*len(froms_list)
    avg_grnd_time = 0.5
    time_allowed = 13
    allowed_planes = [round(13/((distances_list[i]/avg_vel[i])+avg_grnd_time)) for i in range(len(arcs))]

    nodes = list(range(len(departures)*2))

    aircrafts = [demand_list[i]/pax_number for i in range(len(arcs))]
    # aircrafts = pax_number
    list_of_pax = [aircrafts[i]*pax_number for i in range(len(arcs))]

    # =============================================================================
    # Solve linear programming problem (Network optimization)
    # =============================================================================
    def restructure_data(aux_mat,n):
        aux_mat = np.reshape(aux_mat, (n,n-1))
        new_mat = np.zeros((n,n))
        for i in range(n):
            for j in range(n):
                if i == j:
                    new_mat[i][j] = 0
                elif j<=i:
                    new_mat[i][j] = aux_mat[i][j]
                else:
                    new_mat[i][j] = aux_mat[i][j-1]
        return new_mat

    n = len(arrivals)

    # Post processing
    min_capacity = 0.5

    def flatten_dict(dd, separator ='_', prefix =''):
        return { prefix + separator + k if prefix else k : v
                for kk, vv in dd.items()
                for k, v in flatten_dict(vv, separator, kk).items()
                } if isinstance(dd, dict) else { prefix : dd }

    fraction = restructure_data(list_of_pax,n)

    fraction = fraction/planes['P1']['w']

    fraction_1 = np.floor(fraction)
    fraction_2 = fraction-fraction_1

    fraction_1_list = []
    for i in range(len(departures)):
        for j in range(len(arrivals)):
            if i != j:
                fraction_1_list.append(fraction_1[i][j])

    fraction_2_list = []
    for i in range(len(departures)):
        for j in range(len(arrivals)):
            if i != j:
                fraction_2_list.append(fraction_2[i][j])

    revenue_1_list = []
    for i in range(len(fraction_1_list)):
        if (list_of_pax[i] <= 0 or fraction_1_list[i] <= 0):
            revenue_1_list.append(0)
        else:
            revenue_1_list.append(demand_list[i]*distances_list[i]*(list_of_pax[i]*fraction_1_list[i]*average_ticket_price)/(list_of_pax[i]*fraction_1_list[i]*distances_list[i]))
            

    revenue_1_list = [0 if x != x else x for x in revenue_1_list]

    revenue_2_list = []
    for i in range(len(fraction_2_list)):
        if (list_of_pax[i] <= 0 or fraction_2_list[i] <= 0):
            revenue_2_list.append(0)
        else:
            revenue_2_list.append(demand_list[i]*distances_list[i]*(list_of_pax[i]*fraction_2_list[i]*average_ticket_price)/(list_of_pax[i]*fraction_2_list[i]*distances_list[i]))
    revenue_2_list = [0 if x != x else x for x in revenue_2_list]


     

    revenue_tot2 = [x + y for x, y in zip(revenue_1_list,revenue_2_list)]
    revenue_tot2 = sum(revenue_tot2)

    revenue_1 = (fraction_1*pax_number)*average_ticket_price
    revenue_2 = np.zeros((len(arrivals),len(arrivals)))
    for i in range(len(arrivals)):
        for j in range(len(departures)):
            if fraction_2[i][j] > min_capacity:
                revenue_2[i][j] = fraction_2[i][j]*pax_number*average_ticket_price
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

    print('margin',profit/revenue_tot)
    print('profit',profit)


    pax_number_flatt = list_pax_processed.flatten()
    
    pax_number_df = pd.DataFrame({'pax_number':pax_number_flatt})
    kpi_df1 = pd.DataFrame()
    # print(pax_number_df)
    kpi_df1['pax_number'] = pax_number_df['pax_number'].values
    # print(kpi_df1["pax_number"])

    # kpi_df1.drop(columns=["variable_object"], inplace=True)
    kpi_df1.to_csv("Test/optimization_solution01.csv")

    ############################################################################################
    def restructure_data(aux_mat,n):
        aux_mat = np.reshape(aux_mat, (n,n-1))
        new_mat = np.zeros((n,n))
        for i in range(n):
            for j in range(n):
                if i == j:
                    new_mat[i][j] = 0
                elif j<=i:
                    new_mat[i][j] = aux_mat[i][j]
                else:
                    new_mat[i][j] = aux_mat[i][j-1]
        return new_mat

    n = len(arrivals)

    kpi_df2 = pd.DataFrame(aircrafts, columns = ["aircraft_number"])

    distances_flatt = flatten_dict(distances)
    # doc_flatt = flatten_dict(DOC)
    demand_flatt = flatten_dict(demand)
    revenue_flatt = revenue_mat.flatten()
    doc_flatt = DOC_proccessed.flatten()

    doc_df = pd.DataFrame({'doc':doc_flatt})
    revenue_df = pd.DataFrame({'revenue':revenue_flatt})


    distance_df =  pd.DataFrame.from_dict(distances_flatt,orient="idx",columns=['distances'])
    # doc_df =  pd.DataFrame.from_dict(doc_flatt,orient="idx",columns=['doc'])
    demand_df =  pd.DataFrame.from_dict(demand_flatt,orient="idx",columns=['demand'])
    # revenue_df =  pd.DataFrame.from_dict(revenue_flatt,orient="idx",columns=['revenue'])

    kpi_df2['distances'] = distances_list
    kpi_df2['doc'] = docs_list
    kpi_df2['demand'] = demand_list
    # kpi_df2['revenue'] = revenue_df['revenue'].values
    
    kpi_df2['active_arcs'] = np.where(kpi_df2["aircraft_number"] > 0, 1, 0)
    X = kpi_df2['active_arcs'].to_numpy()
    X = restructure_data(X,n)

    Distances = kpi_df2['distances'].to_numpy()
    Distances = restructure_data(Distances,n)

    Demand = kpi_df2['demand'].to_numpy()
    Demand= restructure_data(Demand,n)


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
from framework.Database.Aircrafts.baseline_aircraft_parameters import initialize_aircraft_parameters

vehicle = initialize_aircraft_parameters()
operations = vehicle['operations']
departures = ["FRA", "LHR", "CDG", "AMS",
                     "MAD", "BCN", "FCO","DUB","VIE","ZRH"]
arrivals = ["FRA", "LHR", "CDG", "AMS",
                     "MAD", "BCN", "FCO","DUB","VIE","ZRH"]

# departures = ['CD0', 'CD1', 'CD2', 'CD3',
#                 'CD4']
# arrivals = ['CD0', 'CD1', 'CD2', 'CD3',
#             'CD4']


# Load origin-destination distance matrix [nm]
distances_db = pd.read_csv('Database/Distance/distance.csv')
distances_db = (distances_db)
distances = distances_db.to_dict()  # Convert to dictionaty

market_share = operations['market_share']
# # Load dai
demand_db= pd.read_csv('Database/Demand/demand.csv')
demand_db= round(market_share*(demand_db.T))
demand = demand_db.to_dict()

df3 = pd.read_csv('Database/DOC/DOC_test5.csv')
df3 = (df3.T)
doc0 = df3.to_dict()

active_airports_db = pd.read_csv('Database/Demand/switch_matrix_full.csv')
active_airports_db = active_airports_db
active_airports = active_airports_db .to_dict()


demand_in = {}
for i in range(len(departures)):
    demand_in[departures[i]] = {}
    for k in range(len(arrivals)):
        if i != k:
            demand_in[departures[i]][arrivals[k]] = demand[departures[i]][arrivals[k]]*active_airports[departures[i]][arrivals[k]]
        else:
            demand_in[departures[i]][arrivals[k]] =  demand[departures[i]][arrivals[k]]*active_airports[departures[i]][arrivals[k]]
pax_capacity = 144



network_optimization(arrivals, departures, distances, demand_in, active_airports, doc0, pax_capacity, vehicle)