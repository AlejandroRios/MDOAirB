"""
File name :
Author    : 
Email     : aarc.88@gmail.com
Date      : 
Last edit :
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
import pandas as pd
import numpy as np
import json
from datetime import datetime
from framework.utilities.logger import get_logger
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
log = get_logger(__file__.split('.')[0])

def write_optimal_results(profit, DOC_ik, vehicle):

    log.info('==== Start writing aircraft results ====')

    start_time = datetime.today().strftime('%Y-%m-%d-%H%M')

    aircraft = vehicle['aircraft']
    wing = vehicle['wing']
    fuselage = vehicle['fuselage']
    horizontal_tail = vehicle['horizontal_tail']
    vertical_tail = vehicle['vertical_tail']
    winglet = vehicle['winglet']

    engine = vehicle['engine']
    pylon = vehicle['pylon']


    results = vehicle['results']
    performance = vehicle['performance']
    operations = vehicle['operations']

    airport_departure = vehicle['airport_departure']
    airport_destination = vehicle['airport_destination']

    # write string one by one adding newline
    with open(r'Database/Results/Aircrafts/acft_' + str(profit) + '_' + str(start_time) +'.txt','w') as output:
    # with open('Database/Results/Aircrafts/acft_' + str(profit) +'.txt','a') as output:
        output.write(
            '======== Aircraft and network optimization results ========')
        output.write('\n\n')

        # ===============================================================================
        output.write('\n ----- Aircraft parameters ----- \n')

        output.write('\n Performance: \n')

        output.write(
            'RANGE: ' + str("{:.2f}".format(performance['range'])) + ' [nm] \n')
        output.write(
            'MMO: ' + str("{:.2f}".format(operations['mach_maximum_operating'])) + '\n')
        output.write(
            'VMO: ' + str("{:.2f}".format(operations['max_operating_speed'])) + ' [kts] \n')
        output.write(
            'Ceiling: ' + str("{:.2f}".format(operations['max_ceiling'])) + ' [ft] \n')

        output.write('\n Fuselage: \n')

        output.write(
            'Pax: ' + str("{:.2f}".format(aircraft['passenger_capacity'])) + '\n')
        output.write(
            'Crew: ' + str("{:.2f}".format(aircraft['crew_number'])) + '\n')
        output.write('Aisles number: ' +
                     str("{:.2f}".format(fuselage['aisles_number'])) + '\n')
        output.write('Seats number: ' +
                     str("{:.2f}".format(fuselage['seat_abreast_number'])) + '\n')
        output.write('Seat width: ' +
                     str("{:.2f}".format(fuselage['seat_width'])) + ' [m] \n')
        output.write('Seat pitch: ' +
                     str("{:.2f}".format(fuselage['seat_pitch'])) + ' [m] \n')
        output.write('Cabine height: ' +
                     str("{:.2f}".format(fuselage['cabine_height'])) + ' [m] \n')
        output.write('Fuselage length: ' +
                     str("{:.2f}".format(fuselage['length'])) + ' [m] \n')
        output.write('Cockpit length: ' +
                     str("{:.2f}".format(fuselage['cockpit_length'])) + ' [m] \n')
        output.write('Tail length: ' +
                     str("{:.2f}".format(fuselage['tail_length'])) + ' [m] \n')
        output.write(
            'Width: ' + str("{:.2f}".format(fuselage['width'])) + ' [m] \n')
        output.write('Diameter: ' +
                     str("{:.2f}".format(fuselage['diameter'])) + ' [m] \n')
        output.write(
            'Height: ' + str("{:.2f}".format(fuselage['height'])) + ' [m] \n')
        output.write('Dz floor: ' +
                     str("{:.2f}".format(fuselage['Dz_floor'])) + ' [m] \n')
        output.write('Wetted area: ' +
                     str("{:.2f}".format(fuselage['wetted_area'])) + ' [m2] \n')
        output.write(
            'Weight: ' + str(fuselage['weight']) + ' [kg] \n')

        output.write('\n Aerodynamics: \n')

        output.write(
            'CLmax: ' + str("{:.2f}".format(aircraft['CL_maximum_clean'])) + '\n')
        output.write(
            'CLmax TO: ' + str("{:.2f}".format(aircraft['CL_maximum_takeoff'])) + '\n')
        output.write(
            'CLmax LD: ' + str("{:.2f}".format(aircraft['CL_maximum_landing'])) + '\n')

        output.write('\n Wing: \n')

        output.write(
            'Area: ' + str("{:.2f}".format(wing['area'])) + ' [m2] \n')
        output.write('Span: ' + str("{:.2f}".format(wing['span'])) + ' [m] \n')
        output.write('Aspect Ratio: ' +
                     str("{:.2f}".format(wing['aspect_ratio'])) + '\n')
        output.write('Taper Ratio: ' +
                     str("{:.2f}".format(wing['taper_ratio'])) + '\n')
        output.write('Sweep c/4: ' +
                     str("{:.2f}".format(wing['sweep_c_4'])) + ' [deg] \n')
        output.write(
            'Sweep LE: ' + str("{:.2f}".format(wing['sweep_leading_edge'])) + ' [deg] \n')
        output.write(
            'Twist: ' + str("{:.2f}".format(wing['twist'])) + ' [deg] \n')
        output.write('Wetted area: ' +
                     str("{:.2f}".format(wing['wetted_area'])) + ' [m2] \n')
        output.write('Kink position: ' +
                     str("{:.2f}".format(wing['semi_span_kink'])) + ' [%] \n')
        output.write('Root incidence: ' +
                     str("{:.2f}".format(wing['root_incidence'])) + ' [deg] \n')
        output.write('Kink incidence: ' +
                     str("{:.2f}".format(wing['kink_incidence'])) + ' [deg] \n')
        output.write('Tip incidence: ' +
                     str("{:.2f}".format(wing['tip_incidence'])) + ' [deg] \n')
        output.write('Root t/c: ' +
                     str("{:.2f}".format(wing['thickness_ratio'][0])) + '\n')
        output.write('Kink t/c: ' +
                     str("{:.2f}".format(wing['thickness_ratio'][1])) + '\n')
        output.write(
            'Tip t/c: ' + str("{:.2f}".format(wing['thickness_ratio'][2])) + '\n')
        output.write('Center chord: ' +
                     str("{:.2f}".format(wing['center_chord'])) + ' [m] \n')
        output.write('Root chord: ' +
                     str("{:.2f}".format(wing['root_chord'])) + ' [m] \n')
        output.write('Kink chord: ' +
                     str("{:.2f}".format(wing['kink_chord'])) + ' [m] \n')
        output.write('Tip chord: ' +
                     str("{:.2f}".format(wing['tip_chord'])) + ' [m] \n')
        output.write(
            'MAC: ' + str("{:.2f}".format(wing['mean_aerodynamic_chord'])) + ' [m] \n')
        output.write('Leading edge xposition: ' +
                     str(wing['leading_edge_xposition']) + ' [m] \n')
        output.write('Slat presence: ' +
                     str("{:.2f}".format(aircraft['slat_presence'])) + '\n')
        output.write('Flap span: ' +
                     str("{:.2f}".format(wing['flap_span'])) + ' [%] \n')
        output.write('Flap area: ' +
                     str("{:.2f}".format(wing['flap_area'])) + ' [m2] \n')
        output.write('Flap def. TO: ' +
                     str("{:.2f}".format(wing['flap_deflection_takeoff'])) + ' [deg] \n')
        output.write('Flap def. LD: ' +
                     str("{:.2f}".format(wing['flap_deflection_landing'])) + ' [deg] \n')
        output.write('Aileron position: ' +
                     str("{:.2f}".format(wing['aileron_position'])) + ' [%] \n')
        output.write('Rear spar position: ' +
                     str("{:.2f}".format(wing['rear_spar_ref'])) + ' [%] \n')

        output.write('\n Vertical tail: \n')

        output.write(
            'Area: ' + str(vertical_tail['area']) + ' [m2] \n')
        output.write('Aspect Ratio: ' +
                     str("{:.2f}".format(vertical_tail['aspect_ratio'])) + '\n')
        output.write('Taper Ratio: ' +
                     str("{:.2f}".format(vertical_tail['taper_ratio'])) + '\n')
        output.write(
            'Sweep c/4: ' + str("{:.2f}".format(vertical_tail['sweep_c_4'])) + ' [deg] \n')

        output.write('\n Horizontal tail: \n')

        output.write(
            'Area: ' + str(horizontal_tail['area']) + ' [m2] \n')
        output.write('Aspect Ratio: ' +
                     str("{:.2f}".format(horizontal_tail['aspect_ratio'])) + '\n')
        output.write(
            'Taper Ratio: ' + str("{:.2f}".format(horizontal_tail['taper_ratio'])) + '\n')
        output.write(
            'Sweep c/4: ' + str("{:.2f}".format(horizontal_tail['sweep_c_4'])) + ' [deg] \n')

        output.write('\n Winglet: \n')

        output.write('Aspect Ratio: ' +
                     str("{:.2f}".format(winglet['aspect_ratio'])) + '\n')
        output.write('Taper Ratio: ' +
                     str("{:.2f}".format(winglet['taper_ratio'])) + '\n')
        output.write('Sweep leading edge: ' +
                     str("{:.2f}".format(winglet['sweep_leading_edge'])) + ' [deg] \n')

        output.write('\n Engine: \n')
        output.write('Maximum thrust: ' +
                     str(engine['maximum_thrust']) + ' [kg] \n')
        output.write('Bypass ratio: ' +
                     str("{:.2f}".format(engine['bypass'])) + '\n')
        output.write('Fan diameter: ' +
                     str("{:.2f}".format(engine['fan_diameter'])) + ' [m] \n')
        output.write('Fan pressure ratio: ' +
                     str("{:.2f}".format(engine['fan_pressure_ratio'])) + '\n')
        output.write('Compressor pressure ratio: ' +
                     str("{:.2f}".format(engine['compressor_pressure_ratio'])) + '\n')
        output.write('Turbine inlet temperature: ' +
                     str("{:.2f}".format(engine['turbine_inlet_temperature'])) + ' [deg C] \n')
        output.write('Engine length: ' +
                     str("{:.2f}".format(engine['length'])) + ' [m] \n')

        output.write('\n Pylon: \n')

        output.write('Wetted area: ' +
                     str("{:.2f}".format(pylon['wetted_area'])) + ' [m2] \n')

        output.write('\n Aircraft: \n')

        output.write('Wing position: ' +
                     str("{:.2f}".format(wing['position'])) + '\n')
        output.write('Horizontal tail position: ' +
                     str("{:.2f}".format(horizontal_tail['position'])) + '\n')

        output.write('Engine position: ' +
                     str("{:.2f}".format(engine['position'])) + '\n')
        output.write(
            'Wetted area: ' + str(aircraft['wetted_area']) + ' [m2] \n')
    

        output.write('\n ----- Network parameters ----- \n')

        output.write('\nReferemce values: \n')

        output.write(
            'Mach: ' + str("{:.2f}".format(0)) + ' \n')
        output.write(
            'Range: ' + str("{:.2f}".format(0)) + ' [nm] \n')
        output.write(
            'DOC: ' + str("{:.2f}".format(0)) + ' [$/nm] \n')
        output.write(
            'Passengers: ' + str("{:.2f}".format(0)) + ' \n')
        output.write(
            'Net present value: ' + str("{:.2f}".format(0)) + ' [$] \n')
        output.write(
            'Price: ' + str("{:.2f}".format(0)) + ' [$] \n')
        output.write(
            'Average fare: ' + str("{:.2f}".format(0)) + ' [$] \n')
        output.write(
            'Average load factor: ' + str("{:.2f}".format(0)) + ' \n')
        output.write(
            'Average market share: ' + str("{:.2f}".format(0)) + ' [%] \n')

        output.write('Airports array: ' + str(airport_departure['array']) + "\n")

        market_share = 0.1

        demand_db = pd.read_csv('Database/Demand/demand.csv')
        demand_db = round(market_share*(demand_db.T))
        output.write('\nDaily demand: \n')
        np.savetxt(output, demand_db.values, fmt='%d')

        distances_db = pd.read_csv('Database/Distance/distance.csv')
        distances_db = (distances_db.T)
        output.write('\nDistances: \n')
        np.savetxt(output, distances_db.values, fmt='%d')

        # headings_db = pd.read_csv('Database/distabces/distance.csv')
        # headings_db = (headings_db.T)
        output.write('\nHeadings: \n')
        # np.savetxt(output, headings_db.values, fmt='%d')

        output.write('\nDOC: \n')
        for key in DOC_ik.keys():
            output.write("%s,%s\n\n"%(key,DOC_ik[key]))

        frequencies_db = np.load('Database/Network/frequencies.npy',allow_pickle='TRUE').item()
        # frequencies = pd.DataFrame(frequencies_db, index=False, header=False )

        frequencies = np.array(frequencies_db)
        
        # frequencies_db = pd.read_csv('Database/Network/frequencies.npy')
        # frequencies_db = (frequencies_db.T)
        output.write('\n\nFrequencies: \n')
        # np.savetxt(output, frequencies_db.values, fmt='%d')

        output.write(str(frequencies) + "\n")

        output.write('\nResults: \n')

        output.write(
            'Number of nodes: ' + str("{:.2f}".format(results['nodes_number'])) + ' \n')
        output.write(
            'Number of arcs: ' + str("{:.2f}".format(0)) + ' \n')
        output.write(
            'Average degree of nodes: ' + str("{:.2f}".format(0)) + ' \n')
        output.write(
            'Average path length: ' + str("{:.2f}".format(0)) + ' \n')
        output.write(
            'Network density: ' + str("{:.2f}".format(0)) + ' \n')
        output.write(
            'Average clustering: ' + str("{:.2f}".format(0)) + '\n')


        output.write(
            'Total cost: ' + str("{:.2f}".format(0)) + ' [$] \n')
        output.write(
            'Total revenue: ' + str("{:.2f}".format(0)) + ' [$] \n')
        output.write(
            'Total profit: ' + str("{:.2f}".format(results['profit'])) + ' [$] \n')
        output.write(
            'Number of frequencies: ' + str("{:.2f}".format(0)) + ' \n')
        output.write(
            'Number of used aircraft: ' + str("{:.2f}".format(results['aircrafts_used'])) + ' \n')
    
    log.info('==== End writing aircraft results ====')

    return


def write_kml_results(arrivals, departures, profit, vehicle):
    log.info('==== Start writing klm results ====')
    start_time = datetime.today().strftime('%Y-%m-%d-%H%M')

    departures = departures
    arrivals = arrivals

    data_airports = pd.read_csv("Database/Airports/airports.csv")
    frequencies_db = np.load('Database/Network/frequencies.npy',allow_pickle='TRUE').item()
    with open(r'Database/Results/Kml/acft_' + str(profit) + '_' + str(start_time) +'.kml','w') as output:
    # with open(r'Database/Results/Klm/acft_' + str(profit) + '.kml','w') as output:

        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        output.write('<Document>\n')
        output.write('        <Folder>\n')
        output.write('          <name>NETWORK01</name>\n')
        output.write('              <Style>\n')
        output.write('                <LineStyle>\n')
        output.write('                   <color>ffff0055</color> <width>5</width>\n')
        output.write('                </LineStyle>\n')
        output.write('             </Style>\n')
        # output.write('      <Placemark>\n')

        n = 0
        for i in departures:
            for k in arrivals:
                if (i != k) and (frequencies_db[(i,k)] > 0):
                    output.write('      <Placemark>\n')
                    output.write('             <LineString>\n')

                    dep_latitude = data_airports.loc[data_airports['APT2'] == i, 'LAT'].iloc[0]
                    dep_longitude = data_airports.loc[data_airports['APT2'] == i, 'LON'].iloc[0]
                    des_latitude = data_airports.loc[data_airports['APT2'] == k, 'LAT'].iloc[0]
                    des_longitude = data_airports.loc[data_airports['APT2'] == k, 'LON'].iloc[0]
                    output.write('                <coordinates>' + str("{:.2f},".format(dep_longitude)) + str("{:.2f},".format(dep_latitude)) + '0,' + str("{:.2f},".format(des_longitude)) + str("{:.2f},".format(des_latitude))+ '0' +'</coordinates>\n')
                    output.write('             </LineString>\n')
                    output.write('     	</Placemark>\n')
                    n = n+1

        output.write('       </Folder>\n')
        output.write('</Document>\n')
        output.write('</kml>\n')

    log.info('==== End writing klm results ====')

    return


def write_bad_results(x,error):
    start_time = datetime.today().strftime('%Y-%m-%d-%H%M')

    with open(r'Database/Results/Aircrafts_unfeasible/acft_' + str(start_time) +'.txt','w') as output:
    # with open('Database/Results/Aircrafts/acft_' + str(profit) +'.txt','a') as output:
        output.write(
            '======== Aircraft and network optimization results ========')
        output.write('\n\n')
        # ===============================================================================
        output.write('\n ----- Aircraft parameters ----- \n')
        output.write(str(x) + "\n")

        output.write('\n ----- Error message ----- \n')
        output.write(str(error) + "\n")


    return
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
# from framework.Database.Aircrafts.baseline_aircraft_parameters import *

# write_optimal_results(vehicle,150000)
