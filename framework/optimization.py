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
from deap import base
from deap import creator
from deap import tools
from deap import algorithms
from bokeh.io import push_notebook, show, output_notebook
from bokeh.layouts import row
from bokeh.plotting import figure
from framework.Economics.network_profit import network_profit
from framework.baseline_aircraft_parameters import *
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

IND_SIZE = 20  # Define the number of optimization variables

# Definition of all the atributes (design variables), their type and range
toolbox = base.Toolbox()
toolbox.register("attr_wing_surface", random.randint, 72, 130)
toolbox.register("attr_aspect_ratio", random.uniform, 7.5, 10)
toolbox.register("attr_taper_ratio", random.uniform, 0.25, 0.5)
toolbox.register("attr_wing_sweep", random.randint, 15, 35)
toolbox.register("attr_twist_angle", random.randint, -5, -2)
toolbox.register("attr_kink_position", random.uniform, 0.32, 0.40)
toolbox.register("attr_engine_bypass_ratio", random.uniform, 4.5, 6.5)
toolbox.register("attr_engine_fan_diameter", random.uniform, 1, 2)
toolbox.register("attr_engine_overall_pressure_ratio", random.randint, 27, 30)
toolbox.register("attr_engine_inlet_turbine_temperature",
                 random.randint, 1350, 1500)
toolbox.register("attr_engine_fan_pressure_ratio", random.uniform, 1.6, 1.6)
toolbox.register("attr_pax_number", random.randint, 50, 120)
toolbox.register("attr_number_of_seat_abreast", random.randint, 4, 6)
toolbox.register("attr_aircraft_range", random.randint, 1000, 2500)
toolbox.register("attr_engine_design_point_pressure",
                 random.randint, 41000, 41000)
toolbox.register("attr_engine_design_point_mach", random.uniform, 0.78, 0.78)
toolbox.register("attr_engine_position", random.randint, 1, 1)
toolbox.register("attr_winglet_presence", random.randint, 1, 1)
toolbox.register("attr_slat_presense", random.randint, 1, 1)
toolbox.register("attr_horizontal_tail_position", random.randint, 1, 1)

toolbox.register("individual", tools.initCycle, creator.Individual,
                 (toolbox.attr_wing_surface, toolbox.attr_aspect_ratio, toolbox.attr_taper_ratio, toolbox.attr_wing_sweep, toolbox.attr_twist_angle, toolbox.attr_kink_position,
                  toolbox.attr_engine_bypass_ratio, toolbox.attr_engine_fan_diameter, toolbox.attr_engine_overall_pressure_ratio, toolbox.attr_engine_inlet_turbine_temperature,
                  toolbox.attr_engine_fan_pressure_ratio, toolbox.attr_pax_number, toolbox.attr_number_of_seat_abreast, toolbox.attr_aircraft_range, toolbox.attr_engine_design_point_pressure,
                  toolbox.attr_engine_design_point_mach, toolbox.attr_engine_position, toolbox.attr_winglet_presence, toolbox.attr_slat_presense, toolbox.attr_horizontal_tail_position),
                 n=1)

# Genetic algoritgm configuration
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=2)

# Declaration of the objective function (network profit)


def objective_function(individual):
    # This function takes as inputs the current individual (vector of design variavbles) and
    # a predefined dictionary with pre-stored information of the vehicle (aircraft)
    net_profit = network_profit(individual, vehicle)
    return [net_profit, ]

# Declarate the limits for feasible individuals


def feaseGeom(x):
    wing_surface = x[0]
    aspect_ratio = x[1]
    taper_ratio = x[2]
    wing_sweep = x[3]
    twist_angle = x[4]
    kink_position = x[5]
    engine_bypass_ratio = x[6]
    engine_fan_diameter = x[7]
    engine_overall_pressure_ratio = x[8]
    engine_inlet_turbine_temperature = x[9]
    engine_fan_pressure_ratio = x[10]
    pax_number = x[11]
    number_of_seat_abreast = x[12]
    aircraft_range = x[13]
    engine_design_point_pressure = x[14]
    engine_design_point_mach = x[15]
    engine_position = x[16]
    winglet_presence = x[17]
    slat_precense = x[18]
    horizontal_tail_position = x[19]

    if ((wing_surface >= 72 and wing_surface <= 130) and (aspect_ratio >= 7.5 and aspect_ratio <= 10) and (taper_ratio >= 0.25 and taper_ratio <= 0.5) and (wing_sweep >= 15 and wing_sweep <= 35) and (twist_angle >= -5 and twist_angle <= -2) and
        (kink_position >= 0.32 and kink_position <= 0.4) and (engine_bypass_ratio >= 4.5 and engine_bypass_ratio <= 6.5) and (engine_fan_diameter >= 1.0 and engine_fan_diameter <= 2.0) and (engine_overall_pressure_ratio >= 25 and engine_overall_pressure_ratio <= 30) and
        (engine_inlet_turbine_temperature >= 1350 and engine_inlet_turbine_temperature <= 1500) and (engine_fan_pressure_ratio >= 1.4 and engine_fan_pressure_ratio <= 2.5) and (pax_number >= 70 and pax_number <= 120) and (number_of_seat_abreast >= 4 and number_of_seat_abreast <= 6) and
        (aircraft_range >= 1000 and aircraft_range <= 2500) and (engine_design_point_pressure >= 41000 and engine_design_point_pressure <= 41000) and (engine_design_point_mach >= 0.78 and engine_design_point_mach <= 0.78) and (engine_position >= 1 and engine_position <= 1) and (winglet_presence >= 1 and winglet_presence <= 1) and
            (slat_precense >= 1 and slat_precense <= 1) and (horizontal_tail_position >= 1 and horizontal_tail_position <= 1)):

        return True
    return False


toolbox.register("evaluate", objective_function)
toolbox.decorate("evaluate", tools.DeltaPenalty(feaseGeom, [1.0, ]))

# The main function that defines the genetic algorithm run


def main():
    pop = toolbox.population(n=5)  # Number of individuals by generation
    hof = tools.HallOfFame(5)  # Hall of fame of top 4 individuals
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=10,
                                   stats=stats, halloffame=hof, verbose=True)
    return [pop, log, hof]


# Run main function
[pop, log, hof] = main()

# Plot the results
p.line(log.select("gen"), log.select("avg"))
show(p)

best = hof.items[0]
print()
print("Best Solution = ", best)
print("Best Score = ", best.fitness.values[0])
print(hof[0])
print(hof[1])
print(hof[2])
print(hof[3])
print(hof[4])

print('# =============================================================================######################')
print('Score:', best.fitness.values[0])
print('# =============================================================================######################')
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
