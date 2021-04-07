"""
File name : Baseline aircraft
Author    : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : September/2020
Last edit : September/2020
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This function descrive baseline aircraft properties which are used to test other modules
Inputs:
    -
Outputs:
    - 
TODO's:
"""
# =============================================================================
# IMPORTS
# =============================================================================
import numpy as np
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================

lbf_to_N = 4.448
kg_to_N = 9.80665

aircraft = {}

aircraft['aerodynamic_centers_arm_wing_horizontal'] = 0
aircraft['after_center_of_gravity_xposition'] = 0
aircraft['xCG'] = 0
aircraft['yCG'] = 0
aircraft['zCG'] = 0
aircraft['CG_position'] = np.array(
    [aircraft['xCG'], aircraft['yCG'], aircraft['zCG']]).transpose()
aircraft['CL_maximum_clean'] = 1.65
aircraft['CL_maximum_landing'] = 2.0
aircraft['CL_maximum_takeoff'] = 2.20
aircraft['CD0_landing'] = 0
aircraft['crew_number'] = 5
aircraft['fixed_equipment_weight'] = 0
aircraft['forward_center_of_gravity_xposition'] = 0
aircraft['Ixx'] = 821466
aircraft['Iyy'] = 3343669
aircraft['Izz'] = 4056813
aircraft['Ixy'] = 0
aircraft['Ixz'] = 178919
aircraft['Iyz'] = 0
aircraft['inertia_matrix'] = np.array([[aircraft['Ixx'], -aircraft['Ixy'], -aircraft['Ixz']],
                                       [-aircraft['Ixy'],
                                        aircraft['Iyy'], -aircraft['Iyz']],
                                       [-aircraft['Ixz'], -aircraft['Iyz'], aircraft['Izz']]])

aircraft['maximum_takeoff_weight'] = 60000
aircraft['maximum_landing_weight'] = 60000
aircraft['maximum_zero_fuel_weight'] = 31700 
aircraft['maximum_fuel_capacity'] = 9428
aircraft['number_of_engines'] = 2
aircraft['neutral_point_xposition'] = 0
aircraft['operational_empty_weight'] = 21800
aircraft['payload_weight'] = 5000
aircraft['passenger_capacity'] = 78
aircraft['power_plant_weight'] = 0
aircraft['static_margin'] = 0.15
aircraft['structural_weight'] = 0
aircraft['slat_presence'] = 1
aircraft['spoiler_presence'] = 1
aircraft['wetted_area'] = 589.7500  # [m2]
aircraft['winglet_presence'] = 0
aircraft['year_of_technology'] = 2017

wing = {}
wing['position'] = 1
wing['leading_edge_xposition'] = 0
wing['area'] = 100
wing['aspect_ratio'] = 12  # Fokker = 8.43
wing['span'] = 30.3579
wing['semi_span'] = 0
wing['taper_ratio'] = 0.38
wing['sweep_c_4'] = 22.6  # [deg]
wing['sweep_leading_edge'] = 22.6  # [deg]
wing['sweep_c_2'] = 22.6  # [deg]
wing['dihedral'] = 3  # [deg]
wing['root_incidence'] = 2  # [deg]
wing['kink_incidence'] = 0  # [deg]
wing['tip_incidence'] = -2.5  # [deg]
wing['twist'] = 0

wing['semi_span_kink'] = 0.34
wing['leading_edge_radius'] = [0.0153, 0.0150, 0.0150]
wing['thickness_ratio'] = [0.12, 0.12, 0.12]
wing['thickness_line_angle_trailing_edge'] = [-0.0799, -0.1025, -0.1553]
wing['maximum_thickness_chordwise_position'] = [0.3738, 0.3585, 0.3590]
wing['camber_line_angle_leading_edge'] = [0.0787, -0.0295, 0.1000]
wing['camber_line_angle_trailing_edge'] = [-0.0549, -0.2101, -0.0258]
wing['maximum_camber'] = [-0.0004, 0.0185, 0.0104]
wing['camber_at_maximum_thickness_chordwise_position'] = [-0.0006, 0.0028, 0.0109]
wing['maximum_camber_chordwise_position'] = [0.6188, 0.7870, 0.5567]
wing['thickness_to_chord_average_ratio'] = 0.11
wing['trunnion_xposition'] = 0
wing['trunnion_length'] = 0
wing['rear_spar_ref'] = 0.75
# yc_trunnion
wing['tank_center_of_gravity_xposition'] = 0
wing['fuel_capacity'] = 0  # [kg]
wing['center_of_gravity_xposition'] = 0
wing['root_thickness'] = 0

wing['root_chord_yposition'] = 0
wing['kink_chord_yposition'] = 0

wing['center_chord'] = 3.53
wing['root_chord'] = 3.53
wing['kink_chord'] = 3.53
wing['tip_chord'] = 3.53
wing['pylon_position_chord'] = 0
wing['engine_position_chord'] = 0


wing['mean_aerodynamic_chord'] = 3.53
wing['wetted_area'] = 168.6500  # [m2]

wing['flap_deflection_takeoff'] = 35  # [deg]
wing['flap_deflection_landing'] = 45  # [deg]
wing['flap_span'] = 0.75
wing['flap_area'] = 0
wing['flap_chord'] = 0
wing['flap_slots_number'] = 2

wing['slat_span'] = 0.75
wing['slat_area'] = 0
wing['slat_chord'] = 0
wing['slat_slots_number'] = 1

wing['mean_aerodynamic_chord_yposition'] = 0
wing['weight'] = 0
wing['mean_thickness'] = 0.11


wing['aerodynamic_center_xposition'] = 0
wing['aerodynamic_center_ref'] = 0.25
wing['aileron_chord'] = 0
wing['aileron_surface'] = 0
wing['aileron_position'] = 0

horizontal_tail = {}
horizontal_tail['position'] = 1
horizontal_tail['area'] = 23.35  # [m2]
horizontal_tail['aspect_ratio'] = 4.35
horizontal_tail['taper_ratio'] = 0.4
horizontal_tail['sweep_c_4']  = 1
horizontal_tail['sweep_c_2']  = 1
horizontal_tail['sweep_leading_edge'] = 0
horizontal_tail['sweep_trailing_edge'] = 0
horizontal_tail['volume'] = 0.9
horizontal_tail['aerodynamic_center'] = 0.25
horizontal_tail['aerodynamic_center_ref'] = 0.25
horizontal_tail['aerodynamic_center_xposition'] = 0
horizontal_tail['mean_chord'] = 1
horizontal_tail['tip_chord'] = 1
horizontal_tail['root_chord'] = 1
horizontal_tail['center_chord'] = 1
horizontal_tail['tail_to_wing_area_ratio'] = 0
horizontal_tail['twist'] = 0
horizontal_tail['span'] = 0
horizontal_tail['dihedral'] = 1
horizontal_tail['mean_aerodynamic_chord'] = 1
horizontal_tail['mean_geometrical_chord'] = 1
horizontal_tail['mean_aerodynamic_chord_yposition'] = 0
horizontal_tail['tau'] = 1
horizontal_tail['weight'] = 0
horizontal_tail['wetted_area'] = 0 
horizontal_tail['center_of_gravity_xposition'] = 0


vertical_tail = {}
vertical_tail['area'] = 16.2  # [m2]
vertical_tail['aspect_ratio'] = 1.2
vertical_tail['taper_ratio'] = 0.5
vertical_tail['sweep_c_4']  = 41
vertical_tail['volume'] = 0.09
vertical_tail['aerodynamic_center'] = 0.25
vertical_tail['aerodynamic_center_ref'] = 0.25
vertical_tail['aerodynamic_center_xposition'] = 0
vertical_tail['dorsalfin_wetted_area'] = 0
vertical_tail['twist'] = 0
vertical_tail['dihedral'] = 90
vertical_tail['center_chord'] = 1
vertical_tail['tip_chord'] = 1
vertical_tail['root_chord'] = 1
vertical_tail['span'] = 1
vertical_tail['mean_aerodynamic_chord'] = 1
vertical_tail['mean_geometrical_chord'] = 1
vertical_tail['sweep_c_2'] = 0
vertical_tail['sweep_leading_edge'] = 0
vertical_tail['sweep_trailing_edge'] = 0
vertical_tail['thickness_ratio'] = [0.11, 0.11]
vertical_tail['weight'] = 0
vertical_tail['wetted_area'] = 0
vertical_tail['mean_aerodynamic_chord_yposition'] = 0
vertical_tail['mean_thickness'] = 0
vertical_tail['center_of_gravity_xposition'] = 0

winglet = {}
winglet['aspect_ratio'] = 2.75
winglet['taper_ratio'] = 0.25
winglet['sweep_leading_edge'] = 35
winglet['cant_angle'] = 75
winglet['cant_angle'] = 75
winglet['weight'] = 0
winglet['wetted_area'] = 0
winglet['root_chord'] = 1
winglet['span'] = 0
winglet['thickess'] = 0
winglet['area'] = 0
winglet['tau'] = 0
winglet['center_of_gravity_xposition'] = 0

fuselage = {}
fuselage['aisles_number'] = 1
fuselage['seat_abreast_number'] = 2
fuselage['cabine_height'] = 2
fuselage['seat_width'] = 0.46
fuselage['aisle_width'] = 0.5
fuselage['seat_pitch'] = 0.8128
fuselage['height_to_width_ratio'] = 1.1
fuselage['pax_transitions'] = 3
fuselage['transition_points'] = [75, 95]
fuselage['width'] = 4 
fuselage['height'] = 4 
fuselage['length'] = 0
fuselage['cabine_length'] = 0
fuselage['nose_length'] = 1.64
fuselage['cockpit_length'] = 0
fuselage['tail_length'] = 0
fuselage['Dz_floor'] = 4
fuselage['minimum_width'] = 3
fuselage['container_type'] = 'LD3-45'
fuselage['wetted_area'] = 0
fuselage['diameter'] = 0
fuselage['weight'] = 0
fuselage['center_of_gravity_xposition'] = 0


engine = {}
engine['diameter'] = 1
engine['fan_diameter'] = engine['diameter']*0.98

engine['bypass'] = 5.0
engine['fan_pressure_ratio'] = 1.46
engine['compressor_pressure_ratio'] = 28.5
engine['turbine_inlet_temperature'] = 1450
engine['design_point_pressure'] = 33000
engine['design_point_mach'] = 0.82
engine['position'] = 1
engine['yposition'] = 1
engine['maximum_thrust'] = aircraft['number_of_engines'] * \
        0.95 * 16206 * (1**0.8) * lbf_to_N  # Rolls-Royce Tay 650 Thrust[N]
engine['wetted_area'] = 0
engine['length'] = 0
engine['weight'] = 0
engine['center_of_gravity_xposition'] = 0
engine['fan_rotation_ref'] = 4952
engine['compressor_rotation_ref'] = 14950
engine['fan_rotation'] = 0
engine['compressor_rotation'] = 0
engine['T0'] = 0
engine['T1'] = 0
engine['T2'] = 0

engine['performance_parameters'] = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])
engine['total_pressures'] = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])
engine['total_temperatures'] = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])
engine['exit_areas'] = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])
engine['fuel_flows'] = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])
engine['gas_exit_speeds'] = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])
engine['rotation_speeds'] = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])

nacelle = {}
nacelle['weight'] = 0
nacelle['center_of_gravity_xposition'] = 0

pylon = {}
pylon['wetted_area'] = 0
pylon['thickness_ratio'] = [0.1, 0.1]
pylon['area'] = 0
pylon['taper_ratio'] = 0
pylon['length'] = 0
pylon['mean_geometrical_chord'] = 0
pylon['mean_aerodynamic_chord'] = 0
pylon['span'] = 0
pylon['xposition'] = 0
pylon['sweep_leading_edge'] = 0

pylon['sweep_leading_c_4'] = 0
pylon['aspect_ratio'] = 2
pylon['center_of_gravity_xposition'] = 0


nose_landing_gear = {}
nose_landing_gear['pressure'] = 190
nose_landing_gear['xpostion'] = 0
nose_landing_gear['weight'] = 0
nose_landing_gear['tyre_diameter'] = 0
nose_landing_gear['tyre_width'] = 0
nose_landing_gear['piston_length'] = 0
nose_landing_gear['piston_diameter'] = 0
nose_landing_gear['center_of_gravity_xposition'] = 0
nose_landing_gear['unit_wheels_number'] = 2

main_landing_gear = {}
main_landing_gear['pressure'] = 200
main_landing_gear['xpostion'] = 0
main_landing_gear['weight'] = 0
main_landing_gear['tyre_diameter'] = 0
main_landing_gear['tyre_width'] = 0
main_landing_gear['piston_length'] = 0
main_landing_gear['piston_diameter'] = 0
main_landing_gear['center_of_gravity_xposition'] = 0
main_landing_gear['unit_wheels_number'] = 2

systems = {}
systems['fuel_weight'] = 0
systems['propulsion_weight'] = 0
systems['flight_control_weight'] = 0
systems['fixed_equipment_weight'] = 0
systems['hydraulic_weight'] = 0
systems['electrical_weight']  = 0
systems['avionics_weight'] = 0
systems['air_weight'] = 0 
systems['oxygen_weight'] = 0
systems['APU_weight'] = 0
systems['furnishing_weight'] = 0
systems['paint_weight'] = 0
systems['handling_gear'] = 0
systems['safety'] = 0


performance = {}
performance['range'] = 1600  # Aircraft range [nm]

operations = {}
operations['takeoff_field_length'] = 2000
operations['landing_field_length'] = 1500
operations['mach_maximum_operating'] = 0.82
operations['mach_cruise'] = operations['mach_maximum_operating'] - 0.02
operations['max_operating_speed'] = 340
operations['holding_time'] = 30  # [min]
operations['alternative_airport_distance'] = 100  # [nm]
operations['max_ceiling'] = 41000
operations['passenger_mass'] = 100  # [kg]
operations['load_factor'] = 0.85




airport_departure = {}
airport_departure['takeoff_field_length'] = 2500  # [m]
airport_departure['landing_field_length'] = 2000  # [m]
airport_departure['elevation'] = 0*3.28084  # [m]
airport_departure['delta_ISA'] = 19.95  # [deg C]
airport_departure['array'] = ["FRA", "LHR", "CDG", "AMS",
                      "MAD", "BCN", "FCO","DUB","VIE","ZRH"]

airport_destination = {}
airport_destination['takeoff_field_length'] = 2500  # [m]
airport_destination['landing_field_length'] = 2000  # [m]
airport_destination['elevation'] = 0*3.28084  # [m]
airport_destination['delta_ISA'] = 19.95  # [deg C]

aircraft['maximum_engine_thrust'] = aircraft['number_of_engines'] * \
    0.95 * 16206 * (1**0.8) * lbf_to_N  # Rolls-Royce Tay 650 Thrust[N]
aircraft['average_thrust'] = 0.75*aircraft['maximum_engine_thrust'] * \
    ((5 + engine['bypass']) /
        (4 + engine['bypass']))  # [N]

results = {}
results['profit'] = 0
results['nodes_number'] = 10
results['covered_demand'] = 0
results['aircrafts_used'] = 0


vehicle = {}
vehicle['aircraft'] = aircraft
vehicle['wing'] = wing
vehicle['horizontal_tail'] = horizontal_tail
vehicle['vertical_tail'] = vertical_tail
vehicle['winglet'] = winglet
vehicle['fuselage'] = fuselage
vehicle['engine'] = engine
vehicle['pylon'] = pylon
vehicle['nacelle'] = nacelle
vehicle['nose_landing_gear'] = nose_landing_gear
vehicle['main_landing_gear'] = main_landing_gear
vehicle['systems'] = systems
vehicle['performance'] = performance
vehicle['operations'] = operations
vehicle['airport_departure'] = airport_departure
vehicle['airport_destination'] = airport_destination
vehicle['results'] = results

# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
