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
import sys
import pickle
import numpy as np
import csv
from datetime import datetime

from framework.utilities.logger import get_logger
from framework.utilities.output import write_optimal_results, write_kml_results, write_bad_results, write_newtork_results

from framework.Attributes.Geo.bearing import calculate_bearing
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
log = get_logger(__file__.split('.')[0])

def objective_function_0(x, vehicle):

    log.info('==== Start network profit module ====')
    start_time = datetime.now()

    # Try running profit calculation. If error appears during run profit = 0
    try:
        # =============================================================================
        # Airplane sizing and checks
    # try:
        status, vehicle = airplane_sizing(x, vehicle)
    # except:
    #     log.error(">>>>>>>>>> Error at <<<<<<<<<<<< airplane_sizing", exc_info = True)

        # Save

        # np.save('Database/Aircrafts/baseline_EMB.npy', vehicle) 


        results = vehicle['results']
        performance = vehicle['performance']
        operations = vehicle['operations']
        airport_departure = vehicle['airport_departure']
        airport_destination = vehicle['airport_destination']
        aircraft = vehicle['aircraft']
        data_airports = pd.read_csv("Database/Airports/airports.csv")
        # =============================================================================
        # If airplane pass checks, status = 0, else status = 1 and profit = 0
        if status == 0:
            log.info('Aircraft passed sizing and checks status: {}'.format(status))

            market_share = operations['market_share']

            # Load origin-destination distance matrix [nm]
            distances_db = pd.read_csv('Database/Distance/distance.csv')
            distances_db = distances_db.T
            distances = distances_db.to_dict()  # Convert to dictionaty

            # Load daily demand matrix and multiply by market share (10%)
            demand_db = pd.read_csv('Database/Demand/demand.csv')
            demand_db = round(market_share*(demand_db.T))
            demand = demand_db.to_dict()

            # Load daily demand matrix and multiply by market share (10%)
            active_airports_db = pd.read_csv('Database/Demand/switch_matrix_full.csv')
            active_airports_db = active_airports_db.T
            active_airports = active_airports_db .to_dict()

            pax_capacity = x[11]  # Passenger capacity

            # Airports:
            # ["FRA", "LHR", "CDG", "AMS",
            #          "MAD", "BCN", "FCO","DUB","VIE","ZRH"]
            departures = ['CD1', 'CD2', 'CD3', 'CD4',
                    'CD5', 'CD6', 'CD7', 'CD8', 'CD9', 'CD10']
            arrivals = ['CD1', 'CD2', 'CD3', 'CD4',
                    'CD5', 'CD6', 'CD7', 'CD8', 'CD9', 'CD10']

            results['nodes_number'] = len(data_airports)


            demand = {}
            for i in range(len(departures)):
                demand[departures[i]] = {}
                for k in range(len(arrivals)):
                    if (i != k) and (active_airports[departures[i]][arrivals[k]] == 1):
                        demand[departures[i]][arrivals[k]] = demand0[departures[i]][arrivals[k]] 
                    else:
                        demand[departures[i]][arrivals[k]] = 0
            

            # departures = ['CD1', 'CD2', 'CD3', 'CD4']
            # arrivals = ['CD1', 'CD2', 'CD3', 'CD4']

            # =============================================================================
            log.info('---- Start DOC calculation ----')
            # The DOC is estimated for each city pair and stored in the DOC dictionary
            city_matrix_size = len(departures)*len(arrivals)
            DOC_ik = {}
            DOC_nd = {}
            fuel_mass = {}
            total_mission_flight_time = {}
            mach = {}
            passenger_capacity = {}
            SAR = {}

            for i in range(len(departures)):

                DOC_ik[departures[i]] = {}
                DOC_nd[departures[i]] = {}
                fuel_mass[departures[i]] = {}
                total_mission_flight_time[departures[i]] = {}
                mach[departures[i]] = {}
                passenger_capacity[departures[i]] = {}
                SAR[departures[i]] = {}

                for k in range(len(arrivals)):
                    if (i != k) and (distances[departures[i]][arrivals[k]] <= x[13]):

                        # Update information about orign-destination pair airports:

                        # Elevation:
                        airport_departure['elevation'] = data_airports.loc[data_airports['APT2']
                                                                        == departures[i], 'ELEV'].iloc[0]
                        airport_destination['elevation'] = data_airports.loc[data_airports['APT2']
                                                                            == arrivals[k], 'ELEV'].iloc[0]
                        # Field length:
                        airport_departure['takeoff_field_length'] = data_airports.loc[data_airports['APT2']
                                                                                    == departures[i], 'TORA'].iloc[0]
                        airport_destination['takeoff_field_length'] = data_airports.loc[data_airports['APT2']
                                                                                        == arrivals[k], 'TORA'].iloc[0]
                        # Average delay:
                        airport_departure['avg_delay'] = data_airports.loc[data_airports['APT2']
                                                                                        == arrivals[i], 'AVD'].iloc[0]
                        airport_destination['avg_delay'] = data_airports.loc[data_airports['APT2']
                                                                                        == arrivals[k], 'AVA'].iloc[0]
                        
                        # Delta ISA
                        airport_departure['delta_ISA'] = data_airports.loc[data_airports['APT2']
                                                                                        == arrivals[i], 'TREF'].iloc[0]
                        airport_destination['delta_ISA'] = data_airports.loc[data_airports['APT2']
                                                                                        == arrivals[k], 'TREF'].iloc[0]

                        # Heading                                                          
                        bearing = calculate_bearing((data_airports['LAT'][i],data_airports['LON'][i]),(data_airports['LAT'][k],data_airports['LON'][k]))
                        heading = round(bearing - (data_airports['DMG'][i] + data_airports['DMG'][k])/2)
                        if heading < 0:
                            heading = heading + 360

                        # Calculate DOC and mission parameters for origin-destination airports pair:                        
                        mission_range = distances[departures[i]][arrivals[k]]
                        fuel_mass[departures[i]][arrivals[k]], total_mission_flight_time[departures[i]][arrivals[k]], DOC,mach[departures[i]][arrivals[k]],passenger_capacity[departures[i]][arrivals[k]], SAR[departures[i]][arrivals[k]] = mission(mission_range,heading,vehicle)
                        DOC_nd[departures[i]][arrivals[k]] = DOC
                        DOC_ik[departures[i]][arrivals[k]] = int(DOC*distances[departures[i]][arrivals[k]])                       
                        # print(DOC_ik[(i, k)])
                    else:
                        DOC_nd[departures[i]][arrivals[k]] = 0
                        if (i == k):
                            DOC_ik[departures[i]][arrivals[k]] = 0
                        else:
                            DOC_ik[departures[i]][arrivals[k]] = 1e10

                        fuel_mass[departures[i]][arrivals[k]]  = 0
                        total_mission_flight_time[departures[i]][arrivals[k]]  = 0
                        mach[departures[i]][arrivals[k]]  = 0
                        passenger_capacity[departures[i]][arrivals[k]]  = 0
                        SAR[departures[i]][arrivals[k]] = 0

                    city_matrix_size = city_matrix_size - 1
                    print('INFO >>>> city pairs remaining to finish DOC matrix fill: ',city_matrix_size)

            with open('Database/DOC/DOC.csv', 'w') as f:
                for key in DOC_ik.keys():
                    f.write("%s,%s\n"%(key,DOC_ik[key]))
                    

            log.info('Aircraft DOC matrix: {}'.format(DOC_ik))
            # =============================================================================
            log.info('---- Start Network Optimization ----')
            # Network optimization that maximizes the network profit
        # try:
            profit, vehicle, kpi_df1, kpi_df2 = network_optimization(
                    arrivals, departures, distances, demand, DOC_ik, pax_capacity, vehicle)
        # except:
        #     log.error(">>>>>>>>>> Error at <<<<<<<<<<<< network_optimization", exc_info = True)

            log.info('Network profit [$USD]: {}'.format(profit))
            # =============================================================================

            def flatten_dict(dd, separator ='_', prefix =''):
                return { prefix + separator + k if prefix else k : v
                        for kk, vv in dd.items()
                        for k, v in flatten_dict(vv, separator, kk).items()
                        } if isinstance(dd, dict) else { prefix : dd }

        # try:
            mach_flatt = flatten_dict(mach)
            mach_df =  pd.DataFrame.from_dict(mach_flatt,orient="index",columns=['mach'])
            passenger_capacity_flatt = flatten_dict(passenger_capacity)
            passenger_capacity_df =  pd.DataFrame.from_dict(passenger_capacity_flatt,orient="index",columns=['pax_num'])
            fuel_used_flatt = flatten_dict(fuel_mass)
            fuel_used_df =  pd.DataFrame.from_dict(fuel_used_flatt,orient="index",columns=['fuel'])
            mission_time_flatt = flatten_dict(total_mission_flight_time)
            mission_time_df =  pd.DataFrame.from_dict(mission_time_flatt,orient="index",columns=['time'])
            DOC_nd_flatt = flatten_dict(DOC_nd)
            DOC_nd_df =  pd.DataFrame.from_dict(DOC_nd_flatt,orient="index",columns=['DOC_nd'])
            SAR_flatt = flatten_dict(SAR)
            SAR_df =  pd.DataFrame.from_dict(SAR_flatt,orient="index",columns=['SAR'])

            kpi_df2['mach'] = mach_df['mach'].values
            kpi_df2['pax_num'] = passenger_capacity_df['pax_num'].values
            kpi_df2['fuel'] = fuel_used_df['fuel'].values
            kpi_df2['time'] = mission_time_df['time'].values
            kpi_df2['DOC_nd'] = DOC_nd_df['DOC_nd'].values
            kpi_df2['SAR'] = SAR_df['SAR'].values
        
            # Number of active nodes
            kpi_df2['active_arcs'] = np.where(kpi_df2["aircraft_number"] > 0, 1, 0)
            results['arcs_number'] = kpi_df2['active_arcs'].sum()

            # Number of aircraft
            kpi_df2['aircraft_number'] = kpi_df2['aircraft_number'].fillna(0)
            
            # Average cruise mach
            kpi_df2['mach_tot_aircraft'] = kpi_df2['aircraft_number']*kpi_df2['mach']

            # Total fuel
            kpi_df2['total_fuel'] = kpi_df2['aircraft_number']*kpi_df2['fuel']
            
            # total CEMV
            kpi_df2['total_CEMV'] =kpi_df2['aircraft_number']*((1/kpi_df2['SAR'])*(1/(aircraft['wetted_area']**0.24)))

            # Total distance
            kpi_df2['total_distance'] = kpi_df2['aircraft_number']*kpi_df2['distances']

            # Total pax
            kpi_df2['total_pax'] = kpi_df2['aircraft_number']*kpi_df2['pax_num']

            # Total cost
            kpi_df2['total_cost'] = 2*kpi_df2['aircraft_number']*kpi_df2['doc']

            results['network_density'] = results['arcs_number']/(results['nodes_number']*results['nodes_number']-results['nodes_number'])

            kpi_df2['total_time'] = kpi_df2['aircraft_number']*kpi_df2['time']
        # except:
            # log.error(">>>>>>>>>> Error at <<<<<<<<<<<< writting dataframes", exc_info = True)

        # try:
            write_optimal_results(profit, DOC_ik, vehicle, kpi_df2)
        # except:
        #     log.error(">>>>>>>>>> Error at <<<<<<<<<<<< write_optimal_results", exc_info = True)

        # try:
            write_kml_results(arrivals, departures, profit, vehicle)
        # except:
        #     log.error(">>>>>>>>>> Error at <<<<<<<<<<<< write_kml_results", exc_info = True)

        # try:
            write_newtork_results(profit,kpi_df1,kpi_df2)
        # except:
        #     log.error(">>>>>>>>>> Error at <<<<<<<<<<<< write_newtork_results", exc_info = True)

        else:
            profit = 0
            log.info(
                'Aircraft did not pass sizing and checks, profit: {}'.format(profit))

            
    except:

        log.error(">>>>>>>>>> Error at <<<<<<<<<<<< objective_function", exc_info = True)
        error = sys.exc_info()[0]
        profit = 0
        log.info('Exception ocurred during calculations')
        log.info('Aircraft not passed sizing and checks, profit: {}'.format(profit))
        
    # try:
        write_bad_results(x,error)
    # except:
        log.error(">>>>>>>>>> Error at <<<<<<<<<<<< write_bad_results", exc_info = True)
    
    else:
        print("Final individual results is:", profit)
    finally:
        print("Executing finally clause")
    end_time = datetime.now()
    log.info('Network profit excecution time: {}'.format(end_time - start_time))
    log.info('==== End network profit module ====')

    # vehicle.clear()

    return profit




def objective_function_1(x, vehicle):

    log.info('==== Start network profit module ====')
    start_time = datetime.now()

    # Try running profit calculation. If error appears during run profit = 0
    try:
        # =============================================================================
        # Airplane sizing and checks
    # try:
        status, vehicle = airplane_sizing(x, vehicle)
        # status = 0
    # except:
    #     log.error(">>>>>>>>>> Error at <<<<<<<<<<<< airplane_sizing", exc_info = True)

        # Save

        # np.save('Database/Aircrafts/baseline_EMB.npy', vehicle) 

        results = vehicle['results']
        performance = vehicle['performance']
        operations = vehicle['operations']
        airport_departure = vehicle['airport_departure']
        airport_destination = vehicle['airport_destination']
        aircraft = vehicle['aircraft']
        data_airports = pd.read_csv("Database/Airports/airports.csv")
        # =============================================================================
        # If airplane pass checks, status = 0, else status = 1 and profit = 0
        if status == 0:
            log.info('Aircraft passed sizing and checks status: {}'.format(status))

            market_share = operations['market_share']

            # Load origin-destination distance matrix [nm]
            distances_db = pd.read_csv('Database/Distance/distance.csv')
            distances_db = distances_db.T
            distances = distances_db.to_dict()  # Convert to dictionaty

            # Load daily demand matrix and multiply by market share (10%)
            demand_db = pd.read_csv('Database/Demand/demand.csv')
            demand_db = round(market_share*(demand_db.T))
            demand0 = demand_db.to_dict()

            # Load daily demand matrix and multiply by market share (10%)
            active_airports_db = pd.read_csv('Database/Demand/switch_matrix.csv')
            active_airports_db = active_airports_db.T
            active_airports = active_airports_db .to_dict()

            pax_capacity = x[11]  # Passenger capacity


 

            # Airports:
            # ["FRA", "LHR", "CDG", "AMS",
            #          "MAD", "BCN", "FCO","DUB","VIE","ZRH"]
            departures = ['CD1', 'CD2', 'CD3', 'CD4',
                    'CD5', 'CD6', 'CD7', 'CD8', 'CD9', 'CD10']
            arrivals = ['CD1', 'CD2', 'CD3', 'CD4',
                    'CD5', 'CD6', 'CD7', 'CD8', 'CD9', 'CD10']

            results['nodes_number'] = len(data_airports)

            
            demand = {}
            for i in range(len(departures)):
                demand[departures[i]] = {}
                for k in range(len(arrivals)):
                    if (i != k) and (active_airports[departures[i]][arrivals[k]] == 1):
                        demand[departures[i]][arrivals[k]] = demand0[departures[i]][arrivals[k]] 
                    else:
                        demand[departures[i]][arrivals[k]] = 0

            # departures = ['CD1', 'CD2', 'CD3', 'CD4']
            # arrivals = ['CD1', 'CD2', 'CD3', 'CD4']

            # =============================================================================
            log.info('---- Start DOC calculation ----')
            # The DOC is estimated for each city pair and stored in the DOC dictionary
            city_matrix_size = len(departures)*len(arrivals)
            DOC_ik = {}
            DOC_nd = {}
            fuel_mass = {}
            total_mission_flight_time = {}
            mach = {}
            passenger_capacity = {}
            SAR = {}

            for i in range(len(departures)):

                DOC_ik[departures[i]] = {}
                DOC_nd[departures[i]] = {}
                fuel_mass[departures[i]] = {}
                total_mission_flight_time[departures[i]] = {}
                mach[departures[i]] = {}
                passenger_capacity[departures[i]] = {}
                SAR[departures[i]] = {}

                for k in range(len(arrivals)):
                    if (i != k) and (distances[departures[i]][arrivals[k]] <= x[13]) and (active_airports[departures[i]][arrivals[k]] == 1):

                        # Update information about orign-destination pair airports:

                        # Elevation:
                        airport_departure['elevation'] = data_airports.loc[data_airports['APT2']
                                                                        == departures[i], 'ELEV'].iloc[0]
                        airport_destination['elevation'] = data_airports.loc[data_airports['APT2']
                                                                            == arrivals[k], 'ELEV'].iloc[0]
                        # Field length:
                        airport_departure['takeoff_field_length'] = data_airports.loc[data_airports['APT2']
                                                                                    == departures[i], 'TORA'].iloc[0]
                        airport_destination['takeoff_field_length'] = data_airports.loc[data_airports['APT2']
                                                                                        == arrivals[k], 'TORA'].iloc[0]
                        # Average delay:
                        airport_departure['avg_delay'] = data_airports.loc[data_airports['APT2']
                                                                                        == arrivals[i], 'AVD'].iloc[0]
                        airport_destination['avg_delay'] = data_airports.loc[data_airports['APT2']
                                                                                        == arrivals[k], 'AVA'].iloc[0]
                        
                        # Delta ISA
                        airport_departure['delta_ISA'] = data_airports.loc[data_airports['APT2']
                                                                                        == arrivals[i], 'TREF'].iloc[0]
                        airport_destination['delta_ISA'] = data_airports.loc[data_airports['APT2']
                                                                                        == arrivals[k], 'TREF'].iloc[0]

                        # Heading                                                          
                        bearing = calculate_bearing((data_airports['LAT'][i],data_airports['LON'][i]),(data_airports['LAT'][k],data_airports['LON'][k]))
                        heading = round(bearing - (data_airports['DMG'][i] + data_airports['DMG'][k])/2)
                        if heading < 0:
                            heading = heading + 360

                        # Calculate DOC and mission parameters for origin-destination airports pair:                        
                        mission_range = distances[departures[i]][arrivals[k]]
                        fuel_mass[departures[i]][arrivals[k]], total_mission_flight_time[departures[i]][arrivals[k]], DOC,mach[departures[i]][arrivals[k]],passenger_capacity[departures[i]][arrivals[k]], SAR[departures[i]][arrivals[k]] = mission(mission_range,heading,vehicle)
                        DOC_nd[departures[i]][arrivals[k]] = DOC
                        DOC_ik[departures[i]][arrivals[k]] = int(DOC*distances[departures[i]][arrivals[k]])                       
                        # print(DOC_ik[(i, k)])
                    else:
                        DOC_nd[departures[i]][arrivals[k]] = 0
                        if (i == k):
                            DOC_ik[departures[i]][arrivals[k]] = 0
                        else:
                            DOC_ik[departures[i]][arrivals[k]] = 1e10

                        fuel_mass[departures[i]][arrivals[k]]  = 0
                        total_mission_flight_time[departures[i]][arrivals[k]]  = 0
                        mach[departures[i]][arrivals[k]]  = 0
                        passenger_capacity[departures[i]][arrivals[k]]  = 0
                        SAR[departures[i]][arrivals[k]] = 0

                    city_matrix_size = city_matrix_size - 1
                    print('INFO >>>> city pairs remaining to finish DOC matrix fill: ',city_matrix_size)

            with open('Database/DOC/DOC.csv', 'w') as f:
                for key in DOC_ik.keys():
                    f.write("%s,%s\n"%(key,DOC_ik[key]))
                    

            log.info('Aircraft DOC matrix: {}'.format(DOC_ik))
            # =============================================================================
            log.info('---- Start Network Optimization ----')
            # Network optimization that maximizes the network profit
        # try:
            profit, vehicle, kpi_df1, kpi_df2 = network_optimization(
                    arrivals, departures, distances, demand, DOC_ik, pax_capacity, vehicle)
        # except:
        #     log.error(">>>>>>>>>> Error at <<<<<<<<<<<< network_optimization", exc_info = True)

            log.info('Network profit [$USD]: {}'.format(profit))
            # =============================================================================

            def flatten_dict(dd, separator ='_', prefix =''):
                return { prefix + separator + k if prefix else k : v
                        for kk, vv in dd.items()
                        for k, v in flatten_dict(vv, separator, kk).items()
                        } if isinstance(dd, dict) else { prefix : dd }

        # try:
            mach_flatt = flatten_dict(mach)
            mach_df =  pd.DataFrame.from_dict(mach_flatt,orient="index",columns=['mach'])
            passenger_capacity_flatt = flatten_dict(passenger_capacity)
            passenger_capacity_df =  pd.DataFrame.from_dict(passenger_capacity_flatt,orient="index",columns=['pax_num'])
            fuel_used_flatt = flatten_dict(fuel_mass)
            fuel_used_df =  pd.DataFrame.from_dict(fuel_used_flatt,orient="index",columns=['fuel'])
            mission_time_flatt = flatten_dict(total_mission_flight_time)
            mission_time_df =  pd.DataFrame.from_dict(mission_time_flatt,orient="index",columns=['time'])
            DOC_nd_flatt = flatten_dict(DOC_nd)
            DOC_nd_df =  pd.DataFrame.from_dict(DOC_nd_flatt,orient="index",columns=['DOC_nd'])
            SAR_flatt = flatten_dict(SAR)
            SAR_df =  pd.DataFrame.from_dict(SAR_flatt,orient="index",columns=['SAR'])

            kpi_df2['mach'] = mach_df['mach'].values
            kpi_df2['pax_num'] = passenger_capacity_df['pax_num'].values
            kpi_df2['fuel'] = fuel_used_df['fuel'].values
            kpi_df2['time'] = mission_time_df['time'].values
            kpi_df2['DOC_nd'] = DOC_nd_df['DOC_nd'].values
            kpi_df2['SAR'] = SAR_df['SAR'].values
        
            # Number of active nodes
            kpi_df2['active_arcs'] = np.where(kpi_df2["aircraft_number"] > 0, 1, 0)
            results['arcs_number'] = kpi_df2['active_arcs'].sum()

            # Number of aircraft
            kpi_df2['aircraft_number'] = kpi_df2['aircraft_number'].fillna(0)
            
            # Average cruise mach
            kpi_df2['mach_tot_aircraft'] = kpi_df2['aircraft_number']*kpi_df2['mach']

            # Total fuel
            kpi_df2['total_fuel'] = kpi_df2['aircraft_number']*kpi_df2['fuel']
            
            # total CEMV
            kpi_df2['total_CEMV'] =kpi_df2['aircraft_number']*((1/kpi_df2['SAR'])*(1/(aircraft['wetted_area']**0.24)))

            # Total distance
            kpi_df2['total_distance'] = kpi_df2['aircraft_number']*kpi_df2['distances']

            # Total pax
            kpi_df2['total_pax'] = kpi_df2['aircraft_number']*kpi_df2['pax_num']

            # Total cost
            kpi_df2['total_cost'] = 2*kpi_df2['aircraft_number']*kpi_df2['doc']

            results['network_density'] = results['arcs_number']/(results['nodes_number']*results['nodes_number']-results['nodes_number'])

            kpi_df2['total_time'] = kpi_df2['aircraft_number']*kpi_df2['time']
        # except:
            # log.error(">>>>>>>>>> Error at <<<<<<<<<<<< writting dataframes", exc_info = True)

        # try:
            write_optimal_results(profit, DOC_ik, vehicle, kpi_df2)
        # except:
        #     log.error(">>>>>>>>>> Error at <<<<<<<<<<<< write_optimal_results", exc_info = True)

        # try:
            write_kml_results(arrivals, departures, profit, vehicle)
        # except:
        #     log.error(">>>>>>>>>> Error at <<<<<<<<<<<< write_kml_results", exc_info = True)

        # try:
            write_newtork_results(profit,kpi_df1,kpi_df2)
        # except:
        #     log.error(">>>>>>>>>> Error at <<<<<<<<<<<< write_newtork_results", exc_info = True)

        else:
            profit = 0
            log.info(
                'Aircraft did not pass sizing and checks, profit: {}'.format(profit))

            
    except:

        log.error(">>>>>>>>>> Error at <<<<<<<<<<<< objective_function", exc_info = True)
        error = sys.exc_info()[0]
        profit = 0
        log.info('Exception ocurred during calculations')
        log.info('Aircraft not passed sizing and checks, profit: {}'.format(profit))
        
    # try:
        write_bad_results(x,error)
    # except:
        log.error(">>>>>>>>>> Error at <<<<<<<<<<<< write_bad_results", exc_info = True)
    
    else:
        print("Final individual results is:", profit)
    finally:
        print("Executing finally clause")
    end_time = datetime.now()
    log.info('Network profit excecution time: {}'.format(end_time - start_time))
    log.info('==== End network profit module ====')

    # vehicle.clear()

    return profit

def objective_function(x, vehicle):
    operations = vehicle['operations']

    if operations['computation_mode'] == 0:
        profit = objective_function_0(x, vehicle)
    elif operations['computation_mode'] == 1:
        profit = objective_function_1(x, vehicle)

    return profit


# =============================================================================
# TEST
# =============================================================================
# global NN_induced, NN_wave, NN_cd0, NN_CL, num_Alejandro
# num_Alejandro = 100000000000000000000000
# global NN_induced, NN_wave, NN_cd0, NN_CL


# from framework.Database.Aircrafts.baseline_aircraft_parameters import initialize_aircraft_parameters

# # # x = [130, 8.204561481970153, 0.3229876327660606, 31, -4, 0.3896951781733875, 4.826332970409506, 1.0650795018081771, 27, 1485, 1.6, 101, 4, 2185, 41000, 0.78, 1, 1, 1, 1]
# # # # x = [73, 8.210260198894748, 0.34131954092766925, 28, -5, 0.32042307969643524, 5.000456116634125, 1.337333818504011, 27, 1442, 1.6, 106, 6, 1979, 41000, 0.78, 1, 1, 1, 1]
# # # # x = [106, 9.208279852593964, 0.4714790814543369, 16, -3, 0.34987438995033143, 6.420120321538892, 1.7349297171205607, 29, 1461, 1.6, 74, 6, 1079, 41000, 0.78, 1, 1, 1, 1]

# # print(result)
# # x =[0, 77, 35, 19, -3, 33, 63, 17, 29, 1396, 25, 120, 6, 2280, 41000, 78]

# # result = objective_function(x, vehicle)

# # x = [103, 81, 40, 16, -4, 34, 59, 14, 29, 1370, 18, 114, 6, 1118]


# # x = [9.700e+01,9.900e+01,4.400e+01,1.800e+01,-2.000e+00,3.200e+01, 4.800e+01,1.400e+01,3.000e+01,1.462e+03,1.700e+01,6.000e+01, 6.000e+00,1.525e+03]
# # # x = [7.300e+01,8.600e+01,2.900e+01,1.600e+01,-5.000e+00,3.400e+01, 4.600e+01,2.000e+01,2.700e+01,1.372e+03,1.800e+01,1.160e+02, 4.000e+00,2.425e+03]
# # # x = [1.210e+02,9.600e+01,4.100e+01,2.600e+01,-3.000e+00,3.600e+01, 6.200e+01,1.800e+01,2.900e+01,1.478e+03,1.800e+01,6.800e+01, 5.000e+00,1.975e+03]
# # # x = [7.900e+01,9.400e+01,3.100e+01,2.000e+01,-4.000e+00,3.700e+01, 5.600e+01,1.000e+01,2.900e+01,1.448e+03,1.600e+01,8.200e+01, 5.000e+00,1.825e+03]
# # # x = [1.270e+02,7.600e+01,3.600e+01,2.800e+01,-4.000e+00,3.800e+01, 6.000e+01,1.800e+01,3.000e+01,1.432e+03,1.700e+01,8.800e+01, 5.000e+00,1.225e+03]
# # # x = [1.150e+02,8.400e+01,4.900e+01,3.200e+01,-2.000e+00,3.600e+01, 5.000e+01,1.400e+01,2.800e+01,1.492e+03,1.900e+01,1.100e+02, 4.000e+00,1.375e+03]
# # # x = [1.090e+02,8.100e+01,2.600e+01,2.400e+01,-5.000e+00,4.000e+01, 5.200e+01,1.600e+01,2.700e+01,1.402e+03,1.400e+01,7.400e+01, 4.000e+00,2.125e+03]
# # # x = [9.100e+01,8.900e+01,3.400e+01,3.000e+01,-3.000e+00,3.900e+01, 6.400e+01,1.200e+01,2.800e+01,1.358e+03,2.000e+01,9.600e+01, 5.000e+00,1.675e+03]
# # # x = [8.500e+01,9.100e+01,3.900e+01,3.400e+01,-3.000e+00,3.300e+01, 5.800e+01,1.200e+01,2.800e+01,1.418e+03,1.600e+01,1.020e+02, 6.000e+00,2.275e+03]
# # # x = [1.030e+02,7.900e+01,4.600e+01,2.200e+01,-4.000e+00,3.500e+01, 5.400e+01,1.600e+01,2.900e+01,1.388e+03,1.500e+01,5.400e+01, 6.000e+00,1.075e+03]

# # x = [1.150e+02,8.400e+01,4.900e+01,3.200e+01,-2.000e+00,3.600e+01, 5.000e+01,1.400e+01,2.800e+01,1.492e+03,1.900e+01,1.100e+02, 4.000e+00,1.375e+03,41000, 78, 1, 1, 1, 1] # Prifit ok
# # x =  [127, 82, 46, 22, -2, 44, 48, 21, 27, 1358, 22,  92, 5, 2875, 41200, 82, 1, 1, 1, 1]
# # x =  [115, 84, 49, 32, -2, 36, 50, 14, 28, 1492, 19, 110, 4, 1375, 41000, 78, 1, 1, 1, 1] #good one
# x =  [72, 86, 28, 26, -5, 34, 50, 13, 28, 1450, 14, 70, 4, 1600, 41000, 78, 1, 1, 1, 1] # Baseline
# # x = [int(x) for x in x]
# # print(x)

# # x = [76, 118, 46, 23, -3, 33, 55, 19, 30, 1357, 18, 86, 6, 2412, 42260, 79, 1, 1, 1, 1]
# # x = [91, 108, 50, 29, -3, 34, 52, 12, 27, 1366, 19, 204, 4, 1812, 39260, 80, 1, 1, 1, 1]
# vehicle = initialize_aircraft_parameters()

# # x =[98,78,31,16,-4,40,61,20,28,1418,17,98,4,2005,41000,78,1,1,1,1]
# start_time = datetime.now()

# result = objective_function(x, vehicle)

# end_time = datetime.now()
# print(result)
# print('objective function time: {}'.format(end_time - start_time))

