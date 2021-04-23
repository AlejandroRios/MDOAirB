"""
File name : Optimization function
Author    : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : Dezember 2020
Last edit : February 2021
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil
Description:
    - This function configurate the genetic algorithm for the aircraft and
    network optimization. 
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
import random
import numpy as np
import os
import subprocess
import linecache

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

from bokeh.io import push_notebook, show, output_notebook
from bokeh.layouts import row
from bokeh.plotting import figure
from framework.Optimization.objective_function import objective_function
from framework.Database.Aircrafts.baseline_aircraft_parameters import *

import multiprocessing
from smt.sampling_methods import LHS
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
p = figure()

# Declare the kind of optimization (min or max)
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
# Define the individual list
creator.create("Individual", list, fitness=creator.FitnessMax)

IND_SIZE = 20 # Define the number of optimization variables

# Definition of all the atributes (design variables), their type and range
toolbox = base.Toolbox()
toolbox.register("attr_wing_surface", random.randint, 72, 130)  # [0] 
toolbox.register("attr_aspect_ratio", random.randint, 75, 100)  # [1] - real range 7.5 to 10
toolbox.register("attr_taper_ratio", random.randint, 25, 50)  # [2] - real range 0.25 to 0.5
toolbox.register("attr_wing_sweep", random.randint, 15, 30)  # [3]
toolbox.register("attr_twist_angle", random.randint, -5, -2)  # [4]
toolbox.register("attr_kink_position", random.randint, 25, 40)  # [5] - real range 0.32 to 0.4
toolbox.register("attr_engine_bypass_ratio", random.randint, 45, 65)  # [6] - real range 4.5 to 6.5
toolbox.register("attr_engine_fan_diameter", random.randint, 10, 20)  # [7] - real range 1 to 2
toolbox.register("attr_engine_overall_pressure_ratio", random.randint, 27, 30)  # [8]
toolbox.register("attr_engine_inlet_turbine_temperature",
                 random.randint, 1350, 1500)  # [9] 1350 1500
toolbox.register("attr_engine_fan_pressure_ratio", random.randint, 14, 20)  # [10] - real range 1.4 to 2.5
toolbox.register("attr_pax_number", random.randint, 50, 120)  # [11]
toolbox.register("attr_number_of_seat_abreast", random.randint, 4, 6)  # [12]
toolbox.register("attr_aircraft_range", random.randint, 1000, 2500)  # [13]
toolbox.register("attr_engine_design_point_pressure",
                 random.randint, 41000, 41000)  # [14]
toolbox.register("attr_engine_design_point_mach", random.randint, 78, 78)  # [15] - real range 0.78 to 0.78
toolbox.register("attr_engine_position", random.randint, 1, 1)  # [16]
toolbox.register("attr_winglet_presence", random.randint, 1, 1)  # [17]
toolbox.register("attr_slat_presense", random.randint, 1, 1)  # [18]
toolbox.register("attr_horizontal_tail_position", random.randint, 1, 1)  # [19]

toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.attr_wing_surface, toolbox.attr_aspect_ratio, toolbox.attr_taper_ratio, toolbox.attr_wing_sweep, toolbox.attr_twist_angle, toolbox.attr_kink_position,
                  toolbox.attr_engine_bypass_ratio, toolbox.attr_engine_fan_diameter, toolbox.attr_engine_overall_pressure_ratio, toolbox.attr_engine_inlet_turbine_temperature,
                  toolbox.attr_engine_fan_pressure_ratio, toolbox.attr_pax_number, toolbox.attr_number_of_seat_abreast, toolbox.attr_aircraft_range, toolbox.attr_engine_design_point_pressure,
                  toolbox.attr_engine_design_point_mach, toolbox.attr_engine_position, toolbox.attr_winglet_presence, toolbox.attr_slat_presense, toolbox.attr_horizontal_tail_position),
                 n=1)
# toolbox.register("individual", tools.initCycle, creator.Individual,
#                  (toolbox.attr_wing_surface, toolbox.attr_aspect_ratio, toolbox.attr_taper_ratio, toolbox.attr_wing_sweep, toolbox.attr_twist_angle, toolbox.attr_kink_position,
#                   toolbox.attr_engine_bypass_ratio, toolbox.attr_engine_fan_diameter, toolbox.attr_engine_overall_pressure_ratio, toolbox.attr_engine_inlet_turbine_temperature,
#                   toolbox.attr_engine_fan_pressure_ratio, toolbox.attr_pax_number, toolbox.attr_number_of_seat_abreast, toolbox.attr_aircraft_range),
#                  n=1)


# Definition of lower and upper bounds
lower_bounds = [72,   75, 25, 15, -5, 25, 45, 10, 27, 1350, 14, 50, 4,  1000,41000, 78, 1, 1, 1, 1]
upper_bounds = [130, 100, 50, 35, -2, 40, 65, 20, 30, 1500, 20, 120, 6, 2500,41000, 72, 1, 1, 1, 1]
# lower_bounds = [72,   75, 25, 15, -5, 32, 45, 10, 27, 1350, 14, 70, 4,  1000, 39000, 78, 1, 1, 1, 1]
# upper_bounds = [130, 120, 50, 30, -2, 45, 65, 25, 30, 1500, 25, 220, 6, 3500, 43000, 82, 1, 1, 1, 1]

# Declaration of the objective function (network profit)
def obj_function(individual):
    # This function takes as inputs the current individual (vector of design variavbles) and
    # a predefined dictionary with pre-stored information of the vehicle (aircraft)
    net_profit = objective_function(individual, vehicle)
    return net_profit,


def initPopulation(pcls, ind_init, file):    
    return pcls(ind_init(c) for c in file)

# xlimits = np.array([[70, 130], [75, 100],[25, 50],[15,35],[-5,-2],[25,40],[45,65],[10,20],[27,30],[1350,1500],[14,20],[50,120],[4,6],[1000,2500],[41000,41000],[78,78],[1,1],[1,1],[1,1],[1,1]])
# # xlimits = np.array([[70, 130], [75, 120],[25, 50],[15,30],[-5,-2],[32,45],[45,65],[10,25],[27,30],[1350,1500],[14,25],[70,220],[4,6],[1000,3500],[39000,43000],[78,82],[1,1],[1,1],[1,1],[1,1]])
# sampling = LHS(xlimits=xlimits)

# # Indnicate number of individuals by generation
# num = 50
# Initial_population = sampling(num)
# Initial_population =  [[round(y) for y in x] for x in Initial_population]
# Initial_population = [[round(y) for y in x] for x in Initial_population]
# population_Functions used in guess
# Initial_population = [[9.700e+01,9.900e+01,4.400e+01,1.800e+01,-2.000e+00,3.200e+01, 4.800e+01,1.400e+01,3.000e+01,1.462e+03,1.700e+01,6.000e+01, 6.000e+00,1.525e+03],
#                       [7.300e+01,8.600e+01,2.900e+01,1.600e+01,-5.000e+00,3.400e+01, 4.600e+01,2.000e+01,2.700e+01,1.372e+03,1.800e+01,1.160e+02, 4.000e+00,2.425e+03],
#                       [1.210e+02,9.600e+01,4.100e+01,2.600e+01,-3.000e+00,3.600e+01, 6.200e+01,1.800e+01,2.900e+01,1.478e+03,1.800e+01,6.800e+01, 5.000e+00,1.975e+03],
#                       [7.900e+01,9.400e+01,3.100e+01,2.000e+01,-4.000e+00,3.700e+01, 5.600e+01,1.000e+01,2.900e+01,1.448e+03,1.600e+01,8.200e+01, 5.000e+00,1.825e+03],
#                       [1.270e+02,7.600e+01,3.600e+01,2.800e+01,-4.000e+00,3.800e+01, 6.000e+01,1.800e+01,3.000e+01,1.432e+03,1.700e+01,8.800e+01, 5.000e+00,1.225e+03],
#                       [1.150e+02,8.400e+01,4.900e+01,3.200e+01,-2.000e+00,3.600e+01, 5.000e+01,1.400e+01,2.800e+01,1.492e+03,1.900e+01,1.100e+02, 4.000e+00,1.375e+03],
#                       [1.090e+02,8.100e+01,2.600e+01,2.400e+01,-5.000e+00,4.000e+01, 5.200e+01,1.600e+01,2.700e+01,1.402e+03,1.400e+01,7.400e+01, 4.000e+00,2.125e+03],
#                       [9.100e+01,8.900e+01,3.400e+01,3.000e+01,-3.000e+00,3.900e+01, 6.400e+01,1.200e+01,2.800e+01,1.358e+03,2.000e+01,9.600e+01, 5.000e+00,1.675e+03],
#                       [8.500e+01,9.100e+01,3.900e+01,3.400e+01,-3.000e+00,3.300e+01, 5.800e+01,1.200e+01,2.800e+01,1.418e+03,1.600e+01,1.020e+02, 6.000e+00,2.275e+03],
#                       [1.030e+02,7.900e+01,4.600e+01,2.200e+01,-4.000e+00,3.500e+01, 5.400e+01,1.600e+01,2.900e+01,1.388e+03,1.500e+01,5.400e+01, 6.000e+00,1.075e+03]]

# Initial_population = [[115,  84, 49, 32, -2, 36, 50, 14, 28, 1492, 19, 110, 4, 1375, 41000, 78, 1, 1, 1, 1], 
#                       [73,   95, 49, 25, -2, 33, 54, 12, 30, 1432, 16, 122, 4, 2375, 42400, 80, 1, 1, 1, 1], 
#                       [91,  109, 26, 17, -4, 39, 56, 15, 30, 1462, 24, 182, 5, 1875, 39200, 79, 1, 1, 1, 1], 
#                       [85,   91, 29, 20, -5, 40, 50, 20, 28, 1402, 17, 198, 6, 3375, 40800, 80, 1, 1, 1, 1], 
#                       [115,  77, 41, 23, -5, 34, 64, 23, 28, 1448, 20, 168, 4, 2625, 42800, 78, 1, 1, 1, 1], 
#                       [109, 100, 44, 26, -3, 43, 60, 17, 29, 1372, 21, 138, 6, 2125, 40000, 79, 1, 1, 1, 1], 
#                       [79,   86, 36, 29, -3, 35, 46, 24, 27, 1492, 23, 108, 6, 3125, 41600, 81, 1, 1, 1, 1], 
#                       [121, 104, 34, 16, -4, 37, 62, 18, 29, 1478, 15, 152, 4, 1625, 42000, 81, 1, 1, 1, 1], 
#                       [103, 113, 31, 19, -3, 38, 52, 11, 28, 1388, 19,  78, 5, 1125, 39600, 79, 1, 1, 1, 1], 
#                       [127,  82, 46, 22, -2, 44, 48, 21, 27, 1358, 22,  92, 5, 2875, 41200, 82, 1, 1, 1, 1]]

Initial_population = [[72, 91, 30, 33, -4, 31, 45, 13, 28, 1382, 17, 88, 5, 1885, 41000, 78, 1, 1, 1, 1], [73, 94, 42, 16, -4, 34, 63, 14, 28, 1384, 18, 111, 5, 2425, 41000, 78, 1, 1, 1, 1], [98, 78, 31, 16, -4, 40, 61, 20, 28, 1418, 17, 98, 4, 2005, 41000, 78, 1, 1, 1, 1], [90, 90, 49, 33, -2, 34, 48, 16, 29, 1394, 16, 105, 4, 1285, 41000, 78, 1, 1, 1, 1], [75, 92, 41, 23, -4, 30, 53, 18, 29, 1460, 17, 51, 5, 1315, 41000, 78, 1, 1, 1, 1], 
[80, 85, 37, 34, -3, 27, 52, 14, 28, 1498, 17, 87, 6, 1615, 41000, 78, 1, 1, 1, 1], [127, 89, 42, 20, -3, 27, 58, 14, 28, 1466, 18, 107, 6, 1735, 41000, 78, 1, 1, 1, 1], [123, 87, 31, 32, -3, 32, 60, 15, 30, 1442, 17, 108, 5, 1555, 41000, 78, 1, 1, 1, 1], [121, 98, 45, 24, -4, 38, 
51, 10, 27, 1414, 19, 72, 5, 1525, 41000, 78, 1, 1, 1, 1], [116, 75, 34, 16, -5, 29, 48, 16, 28, 1478, 19, 70, 5, 1945, 41000, 78, 1, 1, 1, 1], [102, 78, 39, 17, -4, 36, 47, 16, 27, 1364, 19, 77, 5, 1465, 41000, 78, 1, 1, 1, 1], [83, 90, 33, 20, -2, 33, 50, 10, 29, 1448, 19, 62, 4, 1225, 41000, 78, 1, 1, 1, 1], [84, 95, 39, 28, -3, 25, 60, 18, 27, 1444, 18, 101, 4, 2275, 41000, 78, 1, 1, 1, 1], [126, 99, 49, 28, -3, 25, 63, 20, 29, 1366, 16, 104, 6, 1435, 41000, 78, 1, 1, 1, 1], [114, 92, 30, 26, -3, 37, 52, 16, 27, 1400, 15, 102, 5, 2395, 41000, 78, 1, 1, 1, 1], [129, 95, 47, 25, -4, 39, 65, 20, 29, 1484, 15, 79, 4, 1045, 41000, 78, 1, 1, 1, 1], [77, 88, 40, 15, -3, 28, 50, 13, 29, 1480, 15, 73, 5, 1375, 41000, 78, 1, 1, 1, 1], [117, 77, 43, 22, -3, 37, 61, 15, 29, 1358, 20, 68, 5, 1645, 41000, 78, 1, 1, 1, 1], [125, 93, 27, 35, -3, 
30, 56, 11, 28, 1390, 18, 69, 5, 1495, 41000, 78, 1, 1, 1, 1], [119, 96, 36, 19, -3, 35, 49, 12, 28, 1402, 20, 90, 6, 1105, 41000, 78, 1, 1, 
1, 1], [115, 93, 27, 29, -4, 40, 59, 17, 29, 1492, 19, 82, 5, 2455, 41000, 78, 1, 1, 1, 1], [89, 80, 28, 21, -3, 36, 64, 19, 29, 1486, 20, 76, 5, 2155, 41000, 78, 1, 1, 1, 1], [85, 83, 46, 19, -5, 39, 60, 10, 29, 1450, 18, 116, 5, 2485, 41000, 78, 1, 1, 1, 1], [93, 94, 29, 32, -2, 
32, 53, 13, 30, 1490, 17, 115, 5, 2095, 41000, 78, 1, 1, 1, 1], [74, 91, 34, 24, -4, 33, 64, 12, 27, 1454, 20, 55, 4, 1345, 41000, 78, 1, 1, 
1, 1], [113, 97, 33, 17, -3, 37, 54, 11, 30, 1436, 16, 63, 6, 1915, 41000, 78, 1, 1, 1, 1], [122, 77, 44, 27, -4, 38, 46, 14, 28, 1412, 15, 84, 4, 2065, 41000, 78, 1, 1, 1, 1], [111, 86, 29, 18, -3, 39, 58, 12, 28, 1406, 16, 114, 4, 1675, 41000, 78, 1, 1, 1, 1], [96, 81, 43, 30, -4, 31, 46, 12, 28, 1456, 15, 74, 5, 1855, 41000, 78, 1, 1, 1, 1], [79, 100, 26, 31, -4, 31, 55, 14, 27, 1426, 16, 93, 4, 1075, 41000, 78, 1, 1, 1, 1], [110, 99, 38, 30, -4, 28, 59, 17, 28, 1432, 14, 118, 6, 1015, 41000, 78, 1, 1, 1, 1], [103, 82, 44, 22, -2, 28, 54, 18, 27, 1438, 16, 96, 6, 1405, 41000, 78, 1, 1, 1, 1], [99, 98, 35, 34, -5, 34, 57, 19, 29, 1420, 17, 110, 6, 2305, 41000, 78, 1, 1, 1, 1], [97, 82, 47, 26, 
-5, 35, 49, 19, 29, 1430, 18, 80, 5, 1165, 41000, 78, 1, 1, 1, 1], [109, 81, 37, 21, -3, 27, 62, 11, 30, 1462, 15, 86, 5, 2185, 41000, 78, 1, 1, 1, 1], [81, 88, 48, 28, -5, 35, 57, 17, 29, 1408, 15, 66, 6, 2215, 41000, 78, 1, 1, 1, 1], [71, 87, 48, 30, -2, 26, 46, 18, 29, 1496, 15, 119, 4, 1255, 41000, 78, 1, 1, 1, 1], [95, 89, 32, 20, -5, 34, 56, 16, 29, 1378, 17, 58, 4, 1135, 41000, 78, 1, 1, 1, 1], [108, 85, 45, 31, 
-2, 29, 48, 18, 28, 1472, 18, 52, 5, 2245, 41000, 78, 1, 1, 1, 1], [107, 76, 32, 23, -5, 31, 52, 11, 30, 1396, 19, 59, 5, 1795, 41000, 78, 1, 1, 1, 1], [128, 79, 46, 18, -4, 37, 47, 12, 28, 1372, 18, 91, 6, 1585, 41000, 78, 1, 1, 1, 1], [105, 80, 25, 25, -4, 30, 58, 13, 28, 1388, 19, 54, 5, 2125, 41000, 78, 1, 1, 1, 1], [92, 83, 41, 32, -4, 38, 55, 12, 29, 1354, 14, 112, 4, 1975, 41000, 78, 1, 1, 1, 1], [78, 86, 26, 18, -4, 33, 62, 18, 30, 1468, 16, 83, 4, 2035, 41000, 78, 1, 1, 1, 1], [104, 84, 35, 29, -2, 28, 64, 15, 27, 1474, 14, 56, 5, 1825, 41000, 78, 1, 1, 1, 1], [101, 97, 38, 34, -5, 26, 56, 14, 28, 1360, 14, 94, 5, 2365, 41000, 78, 1, 1, 1, 1], [86, 76, 28, 22, -3, 36, 51, 17, 30, 1376, 18, 65, 5, 1195, 41000, 78, 1, 1, 1, 1], [91, 84, 40, 24, -3, 32, 62, 16, 29, 1424, 16, 100, 6, 2335, 41000, 78, 1, 1, 1, 1], [120, 79, 50, 27, -2, 26, 50, 19, 28, 1352, 16, 60, 6, 1765, 41000, 78, 1, 1, 1, 1], [87, 96, 36, 26, -3, 29, 54, 15, 30, 1370, 19, 97, 6, 1705, 41000, 78, 1, 1, 1, 1]]

              
# Initial_population = [[round(y) for y in x] for x in Initial_population]
# print(Initial_population)

# Genetic algoritgm configuration
# toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", obj_function)
toolbox.register('mate', tools.cxTwoPoint)
toolbox.register("mutate", tools.mutUniformInt,low =lower_bounds,up=upper_bounds,indpb=0.05)
toolbox.register("select", tools.selNSGA2)
toolbox.register("population_guess", initPopulation, list, creator.Individual, Initial_population)

# toolbox.decorate("evaluate", tools.DeltaPenalty(feaseGeom, [1.0, ]))

if __name__ == '__main__':

    random.seed(62)
    # Process Pool of 4 workers
    pool = multiprocessing.Pool(processes=8)
    toolbox.register("map", pool.map)

    

    # pop = toolbox.population(n=10)
    pop = toolbox.population_guess()
    hof = tools.HallOfFame(2)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    logbooks = list()

    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.3, mutpb=0.2, ngen=30, 
                        stats=stats, halloffame=hof)

    pool.close()

    # Save results to txt files
    with open("Database/Results/Optimization/optim_statistics.txt", "w") as file:
        file.write(str(log))

    with open("Database/Results/Optimization/optim_population.txt", "w") as file:
        file.write(str(pop))

    with open("Database/Results/Optimization/optim_hall_of_fame.txt", "w") as file:
        file.write(str(hof))
    

    best = hof.items[0]
    
    print("Best Solution = ", best)
    print("Best Score = ", best.fitness.values[0])


    # print('# =============================================================================######################')
    # print('Score:', best.fitness.values[0])
    # print('# =============================================================================######################')
    # =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================