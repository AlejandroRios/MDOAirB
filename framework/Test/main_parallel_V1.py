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
import json
import jsonschema
import linecache
import multiprocessing
import numpy as np
import os
import random
import subprocess

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

from bokeh.io import push_notebook, show, output_notebook
from bokeh.layouts import row
from bokeh.plotting import figure

from framework.Database.Aircrafts.baseline_aircraft_parameters import vehicle
from framework.Optimization.objective_function import objective_function

from jsonschema import validate
from smt.sampling_methods import LHS
# =============================================================================
# CLASSES
# =============================================================================

class DesignVariablesError(Exception):
	def __init__(self, message):
		self.message = f"Read Design variables issue: {message}"
		super().__init__(self.message)

class FixedParametersError(Exception):
	def __init__(self, message):
		self.message = f"Fixed parameters issue: {message}"
		super().__init__(self.message)

# =============================================================================
# FUNCTIONS
# =============================================================================
DESIGN_VARIABLES_SCHEMA = 'framework/JsonSchema/Design_Variables_Limits.schema.json'
DESIGN_VARIABLES_PATH = 'framework/Database/Custom_Inputs/Design_Variables_Limits.json'

FIXED_PARAMETERS_SCHEMA = 'framework/JsonSchema/Fixed_Parameters.schema.json'
FIXED_PARAMETERS_PATH = 'framework/Database/Custom_Inputs/Fixed_Parameters.json'

def CheckDesignVariables(data):
	for key in data:
		if (data[key]["lower_band"] > data[key]["upper_band"]):
			raise DesignVariablesError(f'Lower band {data[key]["lower_band"]} is greater than upper band {data[key]["upper_band"]} for {key}')

def ReadJsonFile(schema_path, file_path, design_error_class, custom_check_function = None):
	try:

		with open(schema_path) as f:
			schema = json.load(f)

		with open(file_path) as f:
			data = json.load(f)

		validate(instance=data, schema=schema)

		if (custom_check_function != None):
			custom_check_function(data)
		
	except OSError as os_error:
		raise design_error_class(f"{os_error.strerror} [{os_error.filename}]")
	except json.JSONDecodeError as dec_error:
		raise design_error_class(f"{dec_error.msg} [line {dec_error.lineno} column {dec_error.colno} (char {dec_error.pos})]")
	except jsonschema.exceptions.SchemaError:
		raise design_error_class(f"There is an error with the schema")
	except jsonschema.exceptions.ValidationError as val_error:
		path_error = ""
		for path in val_error.path:
			if (path_error):
				path_error += "."
			path_error += path
		raise design_error_class(f"{val_error.message} in path [{path_error}]")

	return data

def UpdateVehicle(vehicle, fixed_parameters):
	for key in fixed_parameters:
		if (key in vehicle):
			vehicle[key].update(fixed_parameters[key])

def RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, attr_name, key, min, max):
	if (key in design_variables):
		min = design_variables[key]["lower_band"]
		max = design_variables[key]["upper_band"]

	toolbox.register(attr_name, random.randint, min, max)
	lower_bounds.append(min)
	upper_bounds.append(max)

def RegisterVariables(toolbox, design_variables):
	# Init of lower and upper bounds
	lower_bounds = []
	upper_bounds = []



	# Register variables
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_wing_surface", "wing_surface", 72, 130)  # [0] 
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_aspect_ratio", "aspect_ratio", 75, 120)  # [1] - real range 7.5 to 10
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_taper_ratio", "taper_ratio", 25, 50)  # [2] - real range 0.25 to 0.5
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_wing_sweep", "wing_sweep", 15, 30)  # [3]
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_twist_angle", "twist_angle", -5, -2)  # [4]
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_kink_position", "kink_position", 32, 45)  # [5] - real range 0.32 to 0.4
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_engine_bypass_ratio", "engine_bypass_ratio", 45, 65)  # [6] - real range 4.5 to 6.5
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_engine_fan_diameter", "engine_fan_diameter", 10, 25)  # [7] - real range 1 to 2
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_engine_overall_pressure_ratio", "engine_overall_pressure_ratio", 27, 30)  # [8]
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_engine_inlet_turbine_temperature", "engine_inlet_turbine_temperature", 1350, 1500)  # [9] 1350 1500
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_engine_fan_pressure_ratio", "engine_fan_pressure_ratio", 14, 25)  # [10] - real range 1.4 to 2.5
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_pax_number", "pax_number", 70, 220)  # [11]
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_number_of_seat_abreast", "number_of_seat_abreast", 4, 6)  # [12]
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_aircraft_range", "aircraft_range", 1000, 3500)  # [13]
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_engine_design_point_pressure", "engine_design_point_pressure", 39000, 43000)  # [14]
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_engine_design_point_mach", "engine_design_point_mach", 78, 82)  # [15] - real range 0.78 to 0.78
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_engine_position", "engine_position", 1, 1)  # [16]
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_winglet_presence", "winglet_presence", 1, 1)  # [17]
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_slat_presense", "slat_presence", 1, 1)  # [18]
	RegisterVariable(toolbox, lower_bounds, upper_bounds, design_variables, "attr_horizontal_tail_position", "horizontal_tail_position", 1, 1)  # [19]

	toolbox.register("individual", tools.initCycle, creator.Individual,
		(toolbox.attr_wing_surface, toolbox.attr_aspect_ratio, toolbox.attr_taper_ratio, toolbox.attr_wing_sweep, toolbox.attr_twist_angle, toolbox.attr_kink_position,
		toolbox.attr_engine_bypass_ratio, toolbox.attr_engine_fan_diameter, toolbox.attr_engine_overall_pressure_ratio, toolbox.attr_engine_inlet_turbine_temperature,
		toolbox.attr_engine_fan_pressure_ratio, toolbox.attr_pax_number, toolbox.attr_number_of_seat_abreast, toolbox.attr_aircraft_range, toolbox.attr_engine_design_point_pressure,
		toolbox.attr_engine_design_point_mach, toolbox.attr_engine_position, toolbox.attr_winglet_presence, toolbox.attr_slat_presense, toolbox.attr_horizontal_tail_position),
		n=1)

	return lower_bounds, upper_bounds


# Definition of lower and upper bounds
# old
lower_bounds = [72,   75, 25, 15, -5, 32, 45, 10, 27, 1350, 14, 50, 4, 1000, 41000, 78, 1, 1, 1, 1]
upper_bounds = [130, 100, 50, 35, -2, 40, 65, 20, 30, 1500, 20, 120, 6, 2500, 41000, 78, 1, 1, 1, 1]
# new
# lower_bounds = [72,   75, 25, 15, -5, 32, 45, 10, 27, 1350, 14, 70, 4, 1000, 39000, 78, 1, 1, 1, 1]
# upper_bounds = [130, 120, 50, 30, -2, 45, 65, 25, 30, 1500, 25, 220, 6, 3500, 43000, 82, 1, 1, 1, 1]

# Declaration of the objective function (network profit)
def obj_function(individual):
    # This function takes as inputs the current individual (vector of design variavbles) and
    # a predefined dictionary with pre-stored information of the vehicle (aircraft)
    net_profit = objective_function(individual, vehicle)
    return net_profit,


def initPopulation(pcls, ind_init, file):    
    return pcls(ind_init(c) for c in file)

# old
xlimits = np.array([[70, 130], [75, 100],[25, 50],[15,35],[-5,-2],[32,40],[45,65],[10,20],[27,30],[1350,1500],[14,20],[50,120],[4,6],[1000,2500],[41000,41000],[78,78],[1,1],[1,1],[1,1],[1,1]])

# new
# xlimits = np.array([[70, 130], [75, 120],[25, 50],[15,30],[-5,-2],[32,45],[45,65],[10,25],[27,30],[1350,1500],[14,25],[70,220],[4,6],[1000,3500],[39000,43000],[78,82],[1,1],[1,1],[1,1],[1,1]])

sampling = LHS(xlimits=xlimits)

# Indnicate number of individuals by generation
num = 50
Initial_population = sampling(num)
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
              
Initial_population = [[round(y) for y in x] for x in Initial_population]

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
    pool = multiprocessing.Pool(processes=6)
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
