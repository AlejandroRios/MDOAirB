"""
File name : Climb integration
Author    : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : November/2020
Last edit : November/2020
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    -
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
import numpy as np
from scipy.integrate import odeint
from scipy.integrate import ode
import matplotlib.pyplot as plt

from framework.Attributes.Airspeed.airspeed import V_cas_to_mach, mach_to_V_cas, crossover_altitude
from framework.Attributes.Atmosphere.atmosphere_ISA_deviation import atmosphere_ISA_deviation
from framework.Performance.Engine.engine_performance import turbofan
from framework.Performance.Analysis.climb_to_altitude import rate_of_climb_calculation
from framework.baseline_aircraft import baseline_aircraft

# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
global GRAVITY
GRAVITY = 9.8067


def climb_integration(mass, mach_climb, climb_V_cas, delta_ISA, final_altitude, initial_altitude, vehicle):

    rate_of_climb = 500

    time_climb1 = 0
    time_climb2 = 0
    time_climb3 = 0

    transition_altitude = crossover_altitude(
        mach_climb, climb_V_cas, delta_ISA)

    time = 0
    distance = 0
    fuel1 = 0
    fuel2 = 0
    fuel3 = 0

    if final_altitude >= transition_altitude:
        flag1 = 1
        flag2 = 1
        flag3 = 1

    if (final_altitude >= 10000 and final_altitude < transition_altitude):
        flag1 = 1
        flag2 = 1
        flag3 = 0

    if final_altitude < 10000:
        flag1 = 1
        flag2 = 0
        flag3 = 0

    total_burned_fuel = []
    total_climb_time = []

    throttle_position = 0.95
    # aircraft_data = baseline_aircraft()

    if flag1 == 1:

        # Climb to 10000 ft with 250 KCAS
        if final_altitude <= 11000:
            final_block_altitude = final_altitude
        else:
            final_block_altitude = 11000

        initial_block_distance = 0
        initial_block_altitude = 0
        initial_block_mass = mass
        initial_block_time = 0

        final_block_distance, final_block_altitude, final_block_mass, final_block_time = climb_integrator(
            initial_block_distance, initial_block_altitude, initial_block_mass, initial_block_time, final_block_altitude, climb_V_cas, mach_climb, delta_ISA, vehicle)

        burned_fuel = initial_block_mass - final_block_mass
        climb_time = final_block_time - initial_block_time
        total_burned_fuel.append(burned_fuel)
        total_climb_time.append(climb_time)

    if flag2 == 1:

        initial_block_distance = final_block_distance
        initial_block_altitude = final_block_altitude
        initial_block_mass = final_block_mass
        initial_block_time = final_block_time

        final_block_altitude = transition_altitude

        final_block_distance, final_block_altitude, final_block_mass, final_block_time = climb_integrator(
            initial_block_distance, initial_block_altitude, initial_block_mass, initial_block_time, final_block_altitude, climb_V_cas, mach_climb, delta_ISA, vehicle)

        burned_fuel = initial_block_mass - final_block_mass
        climb_time = final_block_time - initial_block_time
        total_burned_fuel.append(burned_fuel)
        total_climb_time.append(climb_time)
        # plt.plot(time_interval, state[:, 1])

    if flag3 == 1:

        initial_block_distance = final_block_distance
        initial_block_altitude = final_block_altitude
        initial_block_mass = final_block_mass
        initial_block_time = final_block_time

        final_block_altitude = final_altitude

        final_block_distance, final_block_altitude, final_block_mass, final_block_time = climb_integrator(
            initial_block_distance, initial_block_altitude, initial_block_mass, initial_block_time, final_block_altitude, 0, mach_climb, delta_ISA, vehicle)

        burned_fuel = initial_block_mass - final_block_mass

        climb_time = final_block_time - initial_block_time
        total_burned_fuel.append(burned_fuel)
        total_climb_time.append(climb_time)

    final_altitude = final_block_altitude

    final_distance = final_block_distance
    total_burned_fuel = sum(total_burned_fuel)
    total_climb_time = sum(total_climb_time)

    return final_distance, total_climb_time, total_burned_fuel, final_altitude


def climb_integrator(initial_block_distance, initial_block_altitude, initial_block_mass, initial_block_time, final_block_altitude, climb_V_cas, mach_climb, delta_ISA, vehicle):
    t0 = initial_block_time
    z0 = [initial_block_distance, initial_block_altitude, initial_block_mass]
    solver = ode(climb)
    solver.set_integrator('dopri5')
    solver.set_f_params(climb_V_cas, mach_climb, delta_ISA, vehicle)
    solver.set_initial_value(z0, t0)

    t0 = initial_block_time
    t1 = 80
    # N = 50
    t = np.linspace(t0, t1, 80)
    N = len(t)
    sol = np.empty((N, 3))
    sol[0] = z0
    times = np.empty((N, 1))

    # Repeatedly call the `integrate` method to advance the
    # solution to time t[k], and save the solution in sol[k].
    k = 1

    while solver.successful() and solver.y[1] <= final_block_altitude:
        solver.integrate(t[k])
        sol[k] = solver.y
        times[k] = solver.t
        k += 1

    distance = sol[0:k, 0]
    altitude = sol[0:k, 1]
    mass = sol[0:k, 2]
    time = times[0:k]

    final_block_distance = distance[-1]
    final_block_altitude = altitude[-1]
    final_block_mass = mass[-1]
    final_block_time = time[-1]
    return final_block_distance, final_block_altitude, final_block_mass, final_block_time


def climb(time, state, climb_V_cas, mach_climb, delta_ISA, vehicle):

    aircraft = vehicle['aircraft']
    
    distance = state[0]
    altitude = state[1]
    mass = state[2]
    _, _, _, _, _, rho_ISA, _ = atmosphere_ISA_deviation(altitude, delta_ISA)
    throttle_position = 1.0

    if climb_V_cas > 0:
        mach = V_cas_to_mach(climb_V_cas, altitude, delta_ISA)
    else:
        mach = mach_climb

    thrust_force, fuel_flow = turbofan(
        altitude, mach, throttle_position, vehicle)  # force [N], fuel flow [kg/hr]
    thrust_to_weight = aircraft['number_of_engines'] *thrust_force/(mass*GRAVITY)
    rate_of_climb, V_tas, climb_path_angle = rate_of_climb_calculation(
        thrust_to_weight, altitude, delta_ISA, mach, mass, vehicle)
    # if rate_of_climb < 300:
    #     print('rate of climb violated!')

    x_dot = (V_tas*101.269)*np.cos(climb_path_angle)  # ft/min
    h_dot = rate_of_climb  # ft/min
    W_dot = -2*fuel_flow*0.01667  # kg/min
    time_dot = h_dot
    dout = np.array([x_dot, h_dot, W_dot])

    dout = dout.reshape(3, )

    return dout
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================



# mass = 43112
# mach_climb = 0.78
# climb_V_cas = 280
# delta_ISA = 0
# final_altitude = 39000
# initial_altitude = 0
# print(climb_integration(mass, mach_climb, climb_V_cas, delta_ISA, final_altitude, initial_altitude))
# print(state)
