from framework.Performance.Analysis.climb_integration import climb_integration
import numpy as np
from datetime import datetime
import math
from scipy.integrate import solve_ivp
from framework.Database.Aircrafts.baseline_aircraft_parameters import initialize_aircraft_parameters
from framework.Attributes.Airspeed.airspeed import V_cas_to_mach, mach_to_V_cas, crossover_altitude
from framework.Attributes.Atmosphere.atmosphere_ISA_deviation import atmosphere_ISA_deviation
from framework.Performance.Analysis.climb_acceleration import acceleration_to_250
from framework.Performance.Engine.engine_performance import turbofan
from framework.Performance.Analysis.climb_to_altitude import rate_of_climb_calculation

def climb_integrator(initial_block_distance, initial_block_altitude, initial_block_mass, initial_block_time, final_block_altitude, climb_V_cas, mach_climb, delta_ISA, vehicle):
   
    Tsim = initial_block_time + 40
    stop_condition.terminal = True

    stop_criteria = final_block_altitude
    sol = solve_ivp(climb, [initial_block_time, Tsim], [initial_block_distance, initial_block_altitude, initial_block_mass],
            events = stop_condition, method='LSODA',args = (climb_V_cas, mach_climb, delta_ISA, vehicle,stop_criteria), dense_output=True)

    distance = sol.y[0]
    altitude = sol.y[1]
    mass = sol.y[2]
    time = sol.t

    final_block_distance = distance[-1]
    final_block_altitude = altitude[-1]
    final_block_mass = mass[-1]
    final_block_time = time[-1]
    return final_block_distance, final_block_altitude, final_block_mass, final_block_time

def stop_condition(time, state, climb_V_cas, mach_climb, delta_ISA, vehicle,stop_criteria):
    H = state[1]
    return 0 if H>stop_criteria else 1

def climb(time, state, climb_V_cas, mach_climb, delta_ISA, vehicle,stop_criteria):

    aircraft = vehicle['aircraft']

    distance = state[0]
    altitude = state[1]
    mass = state[2]

    # if altitude > final_block_altitude:
    #     return
    _, _, _, _, _, rho_ISA, _, _ = atmosphere_ISA_deviation(altitude, delta_ISA)
    throttle_position = 0.95

    if climb_V_cas > 0:
        mach = V_cas_to_mach(climb_V_cas, altitude, delta_ISA)
    else:
        mach = mach_climb

    thrust_force, fuel_flow, vehicle = turbofan(
        altitude, mach, throttle_position, vehicle)  # force [N], fuel flow [kg/hr]
    thrust_to_weight = aircraft['number_of_engines'] * \
        thrust_force/(mass*GRAVITY)
    rate_of_climb, V_tas, climb_path_angle = rate_of_climb_calculation(
        thrust_to_weight, altitude, delta_ISA, mach, mass, vehicle)
    # if rate_of_climb < 300:
    #     print('rate of climb violated!')

    x_dot = (V_tas*101.269)*np.cos(climb_path_angle)  # ft/min
    h_dot = (V_tas*101.269)*np.sin(climb_path_angle)  # ft/min
    W_dot = -2*fuel_flow*kghr_to_kgmin  # kg/min
    # time_dot = h_dot
    dout = [x_dot, h_dot, W_dot]
    return dout

global GRAVITY
GRAVITY = 9.8067
kghr_to_kgmin = 0.01667
kghr_to_kgsec = 0.000277778
feet_to_nautical_miles = 0.000164579

vehicle = initialize_aircraft_parameters()

altitude_vec = np.array([1500, 3488, 7819, 15733, 20969, 23480, 25700, 27108, 28605, 32000])
speed_vec = np.array([154,251,275,361,392,405,428,436,437])


initial_block_mass = 40000
initial_block_distance = 0
initial_block_time = 0
climb_V_cas = 250
mach_climb = 0.6
delta_ISA = 0

transition_altitude = crossover_altitude(
    mach_climb, climb_V_cas, delta_ISA)


distance_vec = []
time_vec = []
mass_vec = []

for i in range(len(altitude_vec)-1):

    initial_block_altitude = altitude_vec[i]
    final_block_altitude = altitude_vec[i+1]

    distance_vec.append(initial_block_distance)
    mass_vec.append(initial_block_mass)
    time_vec.append(initial_block_time)
    if initial_block_altitude <= transition_altitude:
        final_block_distance, final_block_altitude, final_block_mass, final_block_time = climb_integrator(
                    initial_block_distance, initial_block_altitude, initial_block_mass, initial_block_time, final_block_altitude, climb_V_cas, 0, delta_ISA, vehicle)
    else:
        final_block_distance, final_block_altitude, final_block_mass, final_block_time = climb_integrator(
            initial_block_distance, initial_block_altitude, initial_block_mass, initial_block_time, final_block_altitude, 0, mach_climb, delta_ISA, vehicle)

    initial_block_distance = final_block_distance
    initial_block_altitude = final_block_altitude
    initial_block_mass = final_block_mass
    initial_block_time = final_block_time

final_distance = distance_vec[-1] 
final_time = time_vec[-1]
final_mass = mass_vec[0] - mass_vec[-1]
final_altitude = altitude_vec[-1]

print('final distance: \n',final_distance)
print('final time: \n',final_time)
print('final burned fuel: \n',final_mass)
print('final altitude: \n',final_altitude)

print('distances: \n',distance_vec)
print('time: \n',time_vec)
print('mass: \n',mass_vec)
print('altitude: \n',altitude_vec)




