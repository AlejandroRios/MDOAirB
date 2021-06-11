"""
File name : Wetted area function
Authors   : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : Dezember 2019
Last edit : January 2021
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This function calculates the wetted area of the principal components of the 
    aircraft.
Inputs:
    - Vehicle dictionaty
Outputs:
    - Updated vehicle dictionary
    - x and y coordinates of wing chords 
TODO's:
    - Split this function into functions for each component
    - Rename engine variables
    - x and y coordinates output into vehicle dictionary

"""
# =============================================================================
# IMPORTS
# =============================================================================
import numpy as np
from framework.Sizing.Geometry.pax_cabine_length import pax_cabine_length
from framework.Sizing.Geometry.tailcone_sizing import tailcone_sizing
from framework.Sizing.Geometry.wetted_area_fuselage import *
from framework.Sizing.Geometry.wetted_area_wing import *
from framework.Sizing.Geometry.sizing_horizontal_tail import *
from framework.Performance.Engine.engine_performance import turbofan
from framework.utilities.logger import get_logger

import os
from framework.CPACS_update.cpacsfunctions import *
# import cpacsfunctions as cpsf
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
log = get_logger(__file__.split('.')[0])

global deg_to_rad
deg_to_rad = np.pi/180
N_to_lbf = 0.2248089431


def wetted_area(vehicle):

    MODULE_DIR = 'c:/Users/aarc8/Documents/github\MDOAirB/framework/CPACS_update'
    cpacs_path = os.path.join(MODULE_DIR, 'ToolInput', 'Aircraft_In.xml')
    cpacs_out_path = os.path.join(MODULE_DIR, 'ToolOutput', 'Aircraft_Out.xml')
    tixi = open_tixi(cpacs_out_path)
    tigl = open_tigl(tixi)

    log.info('---- Start wetted area module ----')

    engine = vehicle['engine']
    fuselage = vehicle['fuselage']
    wing = vehicle['wing']
    horizontal_tail = vehicle['horizontal_tail']
    vertical_tail = vehicle['vertical_tail']
    aircraft = vehicle['aircraft']
    operations = vehicle['operations']
    pylon = vehicle['pylon']
    winglet = vehicle['winglet']

    fileToRead1 = 'proot'
    fileToRead2 = 'pkink'
    fileToRead3 = 'ptip'

    engine_thrust, _ , vehicle = turbofan(
        0, 0, 1, vehicle)  # force [N], fuel flow [kg/hr]

    engine_thrust_lbf= engine_thrust*N_to_lbf

    # Sizing
    fuselage['diameter'] = np.sqrt(fuselage['width']*fuselage['height'])

    n = max(2, engine['position'])  # number of engines

    if wing['position'] > 2:
        wing['position'] = 2
    if wing['position'] < 1:
        wing['position'] = 1

    if horizontal_tail['position'] > 2:
        horizontal_tail['position'] = 2
    if horizontal_tail['position'] < 1:
        horizontal_tail['position'] = 1

    if engine['position'] == 2 or engine['position'] == 3:
        horizontal_tail['position'] = 2

    # Fuselage pax cabine length
    fuselage['cabine_length'] = pax_cabine_length(vehicle)

    fuselage['tail_length'] = tailcone_sizing(
        aircraft['passenger_capacity'], engine['position'], fuselage['height'], fuselage['width'])

    fuselage['length'] = fuselage['cabine_length'] + fuselage['tail_length'] + \
        fuselage['cockpit_length']  # comprimento fuselagem [m]
    fuselage['cabine_length'] = fuselage['length'] - \
        (fuselage['tail_length']+fuselage['cockpit_length'])
    # Calculo da area molhada da fuselagem
    # --> Fuselagem dianteira
    fuselage_wetted_area_forward = wetted_area_forward_fuselage(vehicle)
    # --> Cabina de passageiros
    # calculo da excentricidade da elipse (se��o transversal da fuselagem)
    a = max(fuselage['width'], fuselage['height'])/2
    b = min(fuselage['width'], fuselage['height'])/2
    c = np.sqrt(a**2 - b**2)
    e = c/a
    p = np.pi*a*(2 - (e**2/2) + (3*e**4)/16)
    fusealge_wetted_area_pax_cabine = p*fuselage['cabine_length']
    # --> Cone de cauda
    fuselage_wetted_area_tailcone = wetted_area_tailcone_fuselage(vehicle)
    # Hah ainda que se descontar a area do perfil da raiz da asa
    # Sera feito mais adiante
    fuselage['wetted_area'] = fuselage_wetted_area_forward + \
        fusealge_wetted_area_pax_cabine+fuselage_wetted_area_tailcone

    tixi_out = open_tixi(cpacs_out_path)

    fuselage_xpath = '/cpacs/vehicles/aircraft/model/fuselages/fuselage[1]/'
    
    # Update leading edge position
    tixi_out.updateDoubleElement(fuselage_xpath+'positionings/positioning[8]/length',fuselage['cabine_length']/4, '%g')
    tixi_out.updateDoubleElement(fuselage_xpath+'positionings/positioning[9]/length',fuselage['cabine_length']/4, '%g')
    tixi_out.updateDoubleElement(fuselage_xpath+'positionings/positioning[10]/length',fuselage['cabine_length']/4, '%g')
    tixi_out.updateDoubleElement(fuselage_xpath+'positionings/positioning[11]/length',fuselage['cabine_length']/4, '%g')

    tixi_out.updateDoubleElement(fuselage_xpath+'positionings/positioning[12]/length',fuselage['tail_length']/2, '%g')
    tixi_out.updateDoubleElement(fuselage_xpath+'positionings/positioning[13]/length',fuselage['tail_length']/2, '%g')
    
    nominal_diameter = 2.0705*2


    scale_factor = fuselage['diameter']/nominal_diameter


    tixi_out.updateDoubleElement(fuselage_xpath+'transformation/scaling/y',scale_factor, '%g')
    tixi_out.updateDoubleElement(fuselage_xpath+'transformation/scaling/z',scale_factor, '%g')

    
    tixi_out = close_tixi(tixi_out, cpacs_out_path)

    # -----------------------------------------------------------------------------

    # Wing
    wing_trap_surface = wing['area']  # [m2]area da asa
    wing_trap_aspect_ratio = wing['aspect_ratio']  # Alongamento da asa
    wing_trap_taper_ratio = wing['taper_ratio']
    wing_trap_center_chord = 2*wing_trap_surface / \
        (wing['span']*(1+wing_trap_taper_ratio))  # [m] corda no centr

    if wing['position'] == 1:
        wing_dihedral = 2.5  # [�] diedro para asa baixa
        if engine['position'] == 2:
            wing_dihedral = 3
    else:
        wing_dihedral = -2.5  # [�] diedro para asa alta

    wing['tip_chord'] = wing_trap_taper_ratio * \
        wing_trap_center_chord  # [m] corda na ponta

    wing_trap_mean_geometrical_chord = wing_trap_surface / \
        wing['span']  # [m] corda media geometrica
    # [m] corda media geometrica
    wing_trap_mean_aerodynamic_chord = 2/3*wing_trap_center_chord * \
        (1+wing_trap_taper_ratio+wing_trap_taper_ratio**2)/(1+wing_trap_taper_ratio)
    wing_trap_mean_aerodynamic_chord_yposition = wing['span']/6 * \
        (1+2*wing_trap_taper_ratio) / \
        (1+wing_trap_taper_ratio)  # [m] posi�ao y da mac

    wing['sweep_leading_edge'] = 1/deg_to_rad*(np.arctan(np.tan(deg_to_rad*wing['sweep_c_4'])+1/wing_trap_aspect_ratio*(
        1-wing_trap_taper_ratio)/(1+wing_trap_taper_ratio)))  # [�] enflechamento bordo de ataque
    wing['sweep_c_2'] = 1/deg_to_rad*(np.arctan(np.tan(deg_to_rad*wing['sweep_c_4'])-1/wing_trap_aspect_ratio*(
        1-wing_trap_taper_ratio)/(1+wing_trap_taper_ratio)))  # [�] enflechamento C/2
    wing['sweep_trailing_edge'] = 1/deg_to_rad*(np.arctan(np.tan(deg_to_rad*wing['sweep_c_4'])-3/wing_trap_aspect_ratio*(
        1-wing_trap_taper_ratio)/(1+wing_trap_taper_ratio)))  # [�] enflechamento bordo de fuga

    # Reference wing
    wing['root_chord_yposition'] = fuselage['diameter'] / \
        2  # [m] y da raiz da asa
    wing['kink_chord_yposition'] = wing['semi_span_kink'] * \
        wing['span']/2  # [m] y da quebra

    wing['kink_chord'] = (wing['span']/2*np.tan(deg_to_rad*wing['sweep_leading_edge'])+wing['tip_chord'])-(wing['kink_chord_yposition']*np.tan(deg_to_rad *
                                                                                                                                               wing['sweep_leading_edge'])+(wing['span']/2-wing['kink_chord_yposition'])*np.tan(deg_to_rad*wing['sweep_trailing_edge']))  # [m] corda da quebra
    wing_trap_root_chord = (wing['span']/2*np.tan(deg_to_rad*wing['sweep_leading_edge'])+wing['tip_chord'])-(wing['root_chord_yposition']*np.tan(deg_to_rad *
                                                                                                                                                 wing['sweep_leading_edge'])+(wing['span']/2-wing['root_chord_yposition'])*np.tan(deg_to_rad*wing['sweep_trailing_edge']))  # [m] corda da raiz fus trap
    # corda da raiz fus crank
    wing['root_chord'] = wing_trap_root_chord + \
        (wing['kink_chord_yposition']-wing['root_chord_yposition']) * \
        np.tan(deg_to_rad*wing['sweep_trailing_edge'])
    wing_exposed_area = (wing['root_chord']+wing['kink_chord'])*(wing['kink_chord_yposition']-wing['root_chord_yposition']) + \
        (wing['kink_chord']+wing['tip_chord']) * \
        (wing['span']/2-wing['kink_chord_yposition'])  # area exposta
    # corda na juncao com a fus da asa de ref
    wing_ref_root_chord = wing_exposed_area / \
        (wing['span']/2-wing['root_chord_yposition'])-wing['tip_chord']
    wing_ref_center_chord = (wing['span']/2*wing_ref_root_chord-wing['root_chord_yposition']*wing['tip_chord']) / \
        (wing['span']/2 -
         wing['root_chord_yposition'])  # [m] corda na raiz  da asa de ref
    wing['center_chord'] = wing_trap_center_chord+wing['kink_chord_yposition'] * \
        np.tan(deg_to_rad*wing['sweep_trailing_edge'])  # [m] chord at root
    wing['taper_ratio'] = wing['tip_chord'] / \
        wing_ref_center_chord  # taper ratio actual wing

    wing_ref_tip_chord = wing_ref_center_chord*wing['taper_ratio']
    wing_ref_mean_geometrical_chord = wing_ref_center_chord * \
        (1+wing['taper_ratio'])/2  # mgc asa de ref
    wing_ref_mean_aerodynamic_chord = 2/3*wing_ref_center_chord * \
        (1+wing['taper_ratio']+wing['taper_ratio']**2) / \
        (1+wing['taper_ratio'])  # mac da asa ref
    wing_ref_mean_aerodynamic_chord_yposition = wing['span']/6 * \
        (1+2*wing['taper_ratio']) / \
        (1+wing['taper_ratio'])  # y da mac da asa ref

    wing['aspect_ratio'] = wing['span'] / \
        wing_ref_mean_geometrical_chord  # alongamento asa real

    wing_ref_area = wing['span'] * \
        wing_ref_mean_geometrical_chord  # reference area [m�]
    wing_exposed_span = wing['span'] - \
        fuselage['diameter']/2  # envergadura asa exposta
    # exposed wing aspect ratio
    wing_exposed_aspect_ratio = (wing_exposed_span**2)/(wing_exposed_area/2)
    wing_exposed_taper_ratio = wing['tip_chord'] / \
        wing['root_chord']  # afilamento asa exposta

    wing['mean_aerodynamic_chord'] = wing_ref_mean_aerodynamic_chord
    wing['mean_aerodynamic_chord_yposition'] = wing_ref_mean_aerodynamic_chord_yposition
    wing['sweep_leading_edge'] = wing['sweep_leading_edge']

    wing['leading_edge_xposition'] = 0.4250 * \
        fuselage['length']  # inital estimative
    wing['aerodynamic_center_xposition'] = wing['leading_edge_xposition']+wing_ref_mean_aerodynamic_chord_yposition * \
        np.tan(deg_to_rad*wing['sweep_leading_edge']) + \
        0.25*wing_ref_mean_aerodynamic_chord
    wing_rel_aerodynamic_center_xposition = wing['aerodynamic_center_xposition'] / \
        wing_ref_mean_aerodynamic_chord

    wing['aileron_chord'] = (wing['span']/2*np.tan(deg_to_rad*wing['sweep_leading_edge'])+wing['tip_chord'])-((0.75*wing['span']/2)*np.tan(deg_to_rad *
                                                                                                                                           wing['sweep_leading_edge'])+(wing['span']/2-(0.75*wing['span']/2))*np.tan(deg_to_rad*wing['sweep_trailing_edge']))  # corda no aileron
    wing['aileron_surface'] = (wing['root_chord']+wing['kink_chord'])*(wing['kink_chord_yposition']-wing['root_chord_yposition'])+(wing['kink_chord'] +
                                                                                                                                   wing['aileron_chord'])*((0.75*wing['span']/2)-wing['kink_chord_yposition'])  # area exposta com flap
    

    tixi_out = open_tixi(cpacs_out_path)

    wing_xpath = '/cpacs/vehicles/aircraft/model/wings/wing[1]/'
    
    # Update leading edge position
    tixi_out.updateDoubleElement(wing_xpath+'transformation/translation/x', wing['leading_edge_xposition'], '%g')
    # Update center chord 
    tixi_out.updateDoubleElement(wing_xpath+'sections/section[1]/elements/element/transformation/scaling/x', wing['center_chord'], '%g')
    tixi_out.updateDoubleElement(wing_xpath+'sections/section[1]/elements/element/transformation/scaling/y', wing['center_chord'], '%g')
    tixi_out.updateDoubleElement(wing_xpath+'sections/section[1]/elements/element/transformation/scaling/z', wing['center_chord'], '%g')
    # Update root chord 
    tixi_out.updateDoubleElement(wing_xpath+'sections/section[2]/elements/element/transformation/scaling/x', wing['root_chord'], '%g')
    tixi_out.updateDoubleElement(wing_xpath+'sections/section[2]/elements/element/transformation/scaling/y', wing['root_chord'], '%g')
    tixi_out.updateDoubleElement(wing_xpath+'sections/section[2]/elements/element/transformation/scaling/z', wing['root_chord'], '%g')

    tixi_out.updateDoubleElement(wing_xpath+'positionings/positioning[2]/length',wing['root_chord_yposition'], '%g')

    # Update kink chord 
    tixi_out.updateDoubleElement(wing_xpath+'sections/section[3]/elements/element/transformation/scaling/x', wing['kink_chord'], '%g')
    tixi_out.updateDoubleElement(wing_xpath+'sections/section[3]/elements/element/transformation/scaling/y', wing['kink_chord'], '%g')
    tixi_out.updateDoubleElement(wing_xpath+'sections/section[3]/elements/element/transformation/scaling/z', wing['kink_chord'], '%g')

    tixi_out.updateDoubleElement(wing_xpath+'positionings/positioning[3]/length',wing['kink_chord_yposition'], '%g')
    tixi_out.updateDoubleElement(wing_xpath+'positionings/positioning[3]/sweepAngle',wing['sweep_leading_edge'], '%g')

    # Update tip chord 
    tixi_out.updateDoubleElement(wing_xpath+'sections/section[4]/elements/element/transformation/scaling/x', wing['tip_chord'], '%g')
    tixi_out.updateDoubleElement(wing_xpath+'sections/section[4]/elements/element/transformation/scaling/y', wing['tip_chord'], '%g')
    tixi_out.updateDoubleElement(wing_xpath+'sections/section[4]/elements/element/transformation/scaling/z', wing['tip_chord'], '%g')

    tixi_out.updateDoubleElement(wing_xpath+'positionings/positioning[4]/length',wing['span']/2, '%g')
    tixi_out.updateDoubleElement(wing_xpath+'positionings/positioning[4]/sweepAngle',wing['sweep_leading_edge'], '%g')


    tixi_out = close_tixi(tixi_out, cpacs_out_path)




    ############################# WING WETTED AREA ############################
    wing['semi_span'] = wing['span']/2

    # engine['diameter'] = engine['fan_diameter']/0.98  # [m]
    engine['yposition'] = wing['semi_span_kink']

    (vehicle, xutip, yutip, xltip, yltip,
        xubreak, yubreak, xlbreak, ylbreak, xuraiz, yuraiz, xlraiz, ylraiz) = wetted_area_wing(vehicle, fileToRead1, fileToRead2, fileToRead3)

    # descontar a area do perfil da raiz da asa da area molhada da fuselagem
    xproot = np.array([np.flip(xuraiz), xlraiz])
    xproot = xproot.ravel()
    yproot = np.array([np.flip(yuraiz), ylraiz])
    yproot = yproot.ravel()

    def PolyArea(x, y):
        return 0.5*np.abs(np.dot(x, np.roll(y, 1))-np.dot(y, np.roll(x, 1)))

    area_root = PolyArea(wing['root_chord']*xproot, wing['root_chord']*yproot)
    fuselage['wetted_area'] = fuselage['wetted_area'] - 2*area_root
    # -----------------------------------------------------------------------------
    ################################# WINGLET #################################
    ###########################################################################

    winglet['wetted_area'] = 0
    if aircraft['winglet_presence'] == 1:
        winglet['root_chord'] = 0.65*wing['tip_chord']
        winglet['span'] = winglet['aspect_ratio'] * \
            winglet['root_chord']*(1+winglet['taper_ratio'])/2
        winglet['area'] = winglet['root_chord'] * \
            (1 + winglet['taper_ratio'])*winglet['span']/2
        winglet['tau'] = 1  # Perfil da ponta = perfil da raiz
        # Assume-se 9# da espessura relativa do perfil
        winglet['thickess'] = 0.09
        aux1 = 1 + 0.25*(winglet['thickess'] * ((1 + winglet['tau'] *
                                                 winglet['taper_ratio'])/(1 + winglet['taper_ratio'])))
        winglet['wetted_area'] = 2*winglet['area']*aux1  # [m2]

    # -----------------------------------------------------------------------------
    ##############################VERTICAL TAIL################################
    ###########################################################################
    # initial guess for VT area
    vertical_tail_surface_to_wing_area = vertical_tail['area'] / \
        wing['area']  # rela�ao de areas
    vertical_tail['span'] = np.sqrt(
        vertical_tail['aspect_ratio']*vertical_tail['area'])  # Envergadura EV (m)
    vertical_tail['center_chord'] = 2*vertical_tail['area'] / \
        (vertical_tail['span'] *
         (1+vertical_tail['taper_ratio']))  # corda de centro
    vertical_tail['tip_chord'] = vertical_tail['taper_ratio'] * \
        vertical_tail['center_chord']  # corda da ponta
    vertical_tail['root_chord'] = vertical_tail['tip_chord'] / \
        vertical_tail['taper_ratio']  # corda na raiz
    vertical_tail['mean_geometrical_chord'] = vertical_tail['area'] / \
        vertical_tail['span']  # mgc
    vertical_tail['mean_aerodynamic_chord'] = 2/3*vertical_tail['center_chord'] * \
        (1+vertical_tail['taper_ratio']+vertical_tail['taper_ratio']**2) / \
        (1+vertical_tail['taper_ratio'])  # mac
    vertical_tail['mean_aerodynamic_chord_yposition'] = 2*vertical_tail['span'] / \
        6*(1+2*vertical_tail['taper_ratio'])/(1+vertical_tail['taper_ratio'])
    vertical_tail['sweep_leading_edge'] = 1/deg_to_rad*(np.arctan(np.tan(deg_to_rad*vertical_tail['sweep_c_4'])+1/vertical_tail['aspect_ratio']
                                                                  * (1-vertical_tail['taper_ratio'])/(1+vertical_tail['taper_ratio'])))  # [�] enflechamento bordo de ataque
    vertical_tail['sweep_c_2'] = 1/deg_to_rad*(np.arctan(np.tan(deg_to_rad*vertical_tail['sweep_c_4'])-1 /
                                                         vertical_tail['aspect_ratio']*(1-vertical_tail['taper_ratio'])/(1+vertical_tail['taper_ratio'])))  # [�] enflechamento C/2
    vertical_tail['sweep_trailing_edge'] = 1/deg_to_rad*(np.arctan(np.tan(deg_to_rad*vertical_tail['sweep_c_4'])-3/vertical_tail['aspect_ratio']
                                                                   * (1-vertical_tail['taper_ratio'])/(1+vertical_tail['taper_ratio'])))  # [�] enflechamento bordo de fuga
    # lv=(0.060*wingref.S*wing['span'])/vertical_tail['area'] # fisrt estimate
    # lv=lh - 0.25*ht.ct - vertical_tail['span'] * tan(deg_to_rad*vertical_tail['sweep_leading_edge']) + 0.25*vertical_tail['center_chord'] + vertical_tail['mean_aerodynamic_chord'] *tan(deg_to_rad*vertical_tail['sweep_c_4']) # braco da EV
    # vt.v=vertical_tail['area']*lv/(wingref.S*wing['span']) # volume de cauda


    ############################# VT wetted area ######################################
    vertical_tail_mean_chord_thickness = (
        vertical_tail['thickness_ratio'][0]+3*vertical_tail['thickness_ratio'][1])/4  # [#]espessura media
    vertical_tail_tau = vertical_tail['thickness_ratio'][1] / \
        vertical_tail['thickness_ratio'][0]
    # additional area due to the dorsal fin [m2]
    vertical_tail['wetted_area'] = 2*vertical_tail['area']*(1+0.25*vertical_tail['thickness_ratio'][0] *
                                                            ((1+vertical_tail_tau*vertical_tail['taper_ratio'])/(1+vertical_tail['taper_ratio'])))  # [m2]
    # Read geometry of VT airfoil
    panel_number = 201
    airfoil_name = 'pvt'
    # airfoil_preprocessing(airfoil_name, panel_number)
    # df_pvt = pd.read_table(""+ airfoil_name +'.dat' ,header=None,skiprows=[0],sep=',')
    df_pvt = pd.read_csv("Database/Airfoils/" + airfoil_name+'.dat', sep=',',
                         delimiter=None, header=None, skiprows=[0])
    df_pvt.columns = ['x', 'y']

    # [coordinates,~]=get_airfoil_coord('pvt.dat')

    xvt = df_pvt.x
    yvt = df_pvt.y
    area_root_vt = PolyArea(
        xvt*vertical_tail['root_chord'], yvt*vertical_tail['root_chord'])

    vertical_tail['aerodynamic_center_xposition'] = 0.95*fuselage['length'] - vertical_tail['center_chord'] + vertical_tail['mean_aerodynamic_chord_yposition'] * \
        np.tan(vertical_tail['sweep_leading_edge']*deg_to_rad) + \
        vertical_tail['aerodynamic_center_ref'] * \
        vertical_tail['mean_aerodynamic_chord']

    vertical_tail_xle_position = vertical_tail['aerodynamic_center_xposition'] - vertical_tail['center_chord']*0.25
    # Desconta area da intersecao VT-fuselagem da area molhada da fuselagem
    fuselage['wetted_area'] = fuselage['wetted_area'] - area_root_vt


    tixi_out = open_tixi(cpacs_out_path)

    vertical_tail_xpath = '/cpacs/vehicles/aircraft/model/wings/wing[3]/'
    

    # Update leading edge position
    tixi_out.updateDoubleElement(vertical_tail_xpath+'transformation/translation/x', vertical_tail_xle_position, '%g')
    # Update center chord 
    tixi_out.updateDoubleElement(vertical_tail_xpath+'sections/section[1]/elements/element/transformation/scaling/x', vertical_tail['center_chord'], '%g')
    tixi_out.updateDoubleElement(vertical_tail_xpath+'sections/section[1]/elements/element/transformation/scaling/y', vertical_tail['center_chord'], '%g')
    tixi_out.updateDoubleElement(vertical_tail_xpath+'sections/section[1]/elements/element/transformation/scaling/z', vertical_tail['center_chord'], '%g')

    tixi_out.updateDoubleElement(vertical_tail_xpath+'sections/section[2]/elements/element/transformation/scaling/x', vertical_tail['tip_chord'], '%g')
    tixi_out.updateDoubleElement(vertical_tail_xpath+'sections/section[2]/elements/element/transformation/scaling/y', vertical_tail['tip_chord'], '%g')
    tixi_out.updateDoubleElement(vertical_tail_xpath+'sections/section[2]/elements/element/transformation/scaling/z', vertical_tail['tip_chord'], '%g')
    # Update root chord 
    tixi_out.updateDoubleElement(vertical_tail_xpath+'positionings/positioning[2]/length',vertical_tail['span'], '%g')
    tixi_out.updateDoubleElement(vertical_tail_xpath+'positionings/positioning[2]/sweepAngle',vertical_tail['sweep_leading_edge'], '%g')

    tixi_out = close_tixi(tixi_out, cpacs_out_path)
    # -----------------------------------------------------------------------------
    ##############################HORIZONTAL TAIL##############################
    ###########################################################################
    vehicle = sizing_horizontal_tail(
        vehicle, operations['mach_cruise']+0.05, operations['max_ceiling'])


    horizontal_tail_xle_position = horizontal_tail['aerodynamic_center'] - horizontal_tail['center_chord']*0.25

    tixi_out = open_tixi(cpacs_out_path)

    horizontal_thail_xpath = '/cpacs/vehicles/aircraft/model/wings/wing[2]/'
    

    # Update leading edge position
    tixi_out.updateDoubleElement(horizontal_thail_xpath+'transformation/translation/x', horizontal_tail_xle_position, '%g')
    # Update center chord 
    tixi_out.updateDoubleElement(horizontal_thail_xpath+'sections/section[1]/elements/element/transformation/scaling/x', horizontal_tail['center_chord'], '%g')
    tixi_out.updateDoubleElement(horizontal_thail_xpath+'sections/section[1]/elements/element/transformation/scaling/y', horizontal_tail['center_chord'], '%g')
    tixi_out.updateDoubleElement(horizontal_thail_xpath+'sections/section[1]/elements/element/transformation/scaling/z', horizontal_tail['center_chord'], '%g')

    tixi_out.updateDoubleElement(horizontal_thail_xpath+'sections/section[2]/elements/element/transformation/scaling/x', horizontal_tail['tip_chord'], '%g')
    tixi_out.updateDoubleElement(horizontal_thail_xpath+'sections/section[2]/elements/element/transformation/scaling/y', horizontal_tail['tip_chord'], '%g')
    tixi_out.updateDoubleElement(horizontal_thail_xpath+'sections/section[2]/elements/element/transformation/scaling/z', horizontal_tail['tip_chord'], '%g')
    # Update root chord 
    tixi_out.updateDoubleElement(horizontal_thail_xpath+'positionings/positioning[2]/length',horizontal_tail['span']/2, '%g')
    tixi_out.updateDoubleElement(horizontal_thail_xpath+'positionings/positioning[2]/sweepAngle',horizontal_tail['sweep_leading_edge'], '%g')
    tixi_out.updateDoubleElement(horizontal_thail_xpath+'positionings/positioning[1]/dihedralAngle',horizontal_tail['dihedral'], '%g')
    tixi_out.updateDoubleElement(horizontal_thail_xpath+'positionings/positioning[2]/dihedralAngle',horizontal_tail['dihedral'], '%g')

    tixi_out = close_tixi(tixi_out, cpacs_out_path)
    ###########################################################################
    ###################################ENGINE##################################
    ###########################################################################

    engine['length'] = 2.22*((engine_thrust_lbf)**0.4) * \
        (operations['mach_maximum_operating']**0.2) * \
        2.54/100  # [m] Raymer pg 19

    if engine['position'] == 1:
        # livro 6 pag 111 fig 4.41 x/l=0.6
        engine['yposition'] = wing['semi_span_kink'] * \
            wing['span']/2  # [m] y do motor
        wing_engine_external_yposition = engine['yposition']
        wing['engine_position_chord'] = wing['center_chord'] - engine['yposition'] * \
            np.tan(deg_to_rad*wing['sweep_leading_edge']
                   )  # corda da seccao do motor
    elif engine['position'] == 2:
        engine['yposition'] = fuselage['diameter']/2+0.65 * \
            engine['diameter']*np.cos(15*deg_to_rad)
        wing_engine_external_yposition = engine['yposition']
    elif engine['position'] == 3:
        # livro 6 pag 111 fig 4.41 x/l=0.6
        engine['yposition'] = wing['semi_span_kink'] * \
            wing['span']/2  # [m] y do motor
        wing_engine_external_yposition = engine['yposition']
        wing['engine_position_chord'] = wing['center_chord'] - engine['yposition'] * \
            np.tan(deg_to_rad*wing['sweep_leading_edge']
                   )  # corda da seccao do motor
    elif engine['position'] == 4:
        # livro 6 pag 111 fig 4.41 x/l=0.6
        engine['yposition'] = wing['semi_span_kink'] * \
            wing['span']/2  # [m] y do motor
        # [m] y do motor externo distancia entre os dois 30# de b
        wing_engine_external_yposition = (
            engine['yposition']+0.3)*wing['span']/2
        wing['engine_position_chord'] = wing['center_chord'] - engine['yposition'] * \
            np.tan(deg_to_rad*wing['sweep_leading_edge']
                   )  # corda da seccao do motor
        wing_engine_external_position_chord = (wing['span']/2*np.tan(deg_to_rad*wing['sweep_leading_edge'])+wing['tip_chord'])-(wing_engine_external_yposition
                                                                                                                                * np.tan(deg_to_rad*wing['sweep_leading_edge'])+(wing['span']/2-wing_engine_external_yposition)*np.tan(deg_to_rad*wing['sweep_trailing_edge']))
    # -----------------------------------------------------------------------------
    #########################AREA MOLHADA######################################

    ########################## Engine #########################################
    # aux1=(1-2/auxdiv)**2/3
    # engine.wing_wetted_area=pi*engine['diameter']*engine_length*aux1*(1+1/((engine_length/engine['diameter'])**2)) # [m2]
    ln = 0.50*engine['length']  # Fan cowling
    ll = 0.25*ln
    lg = 0.40*engine['length']  # Gas generator
    lp = 0.10*engine['length']  # Plug
    esp = 0.12
    Dn = (1.+esp)*engine['diameter']
    Dhl = engine['diameter']
    Def = (1+esp/2)*engine['diameter']
    Dg = 0.50*Dn
    Deg = 0.90*Dg
    Dp = lp/2
    wetted_area_fan_cowling = ln*Dn*(2+0.35*(ll/ln)+0.80 *
                                     ((ll*Dhl)/(ln*Dn)) + 1.15*(1-ll/ln)*(Def/Dn))
    wetted_area_gas_generator = np.pi*lg*Dg * \
        (1 - 0.333*(1-(Deg/Dg)*(1-0.18*((Dg/lg)**(5/3)))))
    wetted_area_plug = 0.7*np.pi*Dp*lp
    engine['wetted_area'] = wetted_area_fan_cowling + \
        wetted_area_gas_generator+wetted_area_plug

    # -----------------------------------------------------------------------------
    ###########################################################################
    ####################################PYLON##################################
    ###########################################################################

    if engine['position'] == 1:
        wing['pylon_position_chord'] = wing['engine_position_chord']
        pylon['length'] = engine['length']
        pylon['taper_ratio'] = pylon['length'] / wing['pylon_position_chord']
        pylon['mean_geometrical_chord'] = wing['pylon_position_chord'] * \
            (1+pylon['taper_ratio'])/2
        pylon['mean_aerodynamic_chord'] = 2/3*wing['pylon_position_chord'] * \
            (1+pylon['taper_ratio']+pylon['taper_ratio']**2) / \
            (1+pylon['taper_ratio'])  # mac
        # x/l=-0.6 e z/d = 0.85 figure 4.41 pag 111
        pylon['span'] = 0.85*engine['diameter'] - 0.5*engine['diameter']
        pylon['xposition'] = 0.6*wing['engine_position_chord']
        pylon['aspect_ratio'] = pylon['span']/pylon['mean_geometrical_chord']
        pylon['area'] = pylon['span']*pylon['mean_geometrical_chord']
        pylon['sweep_leading_edge'] = (1/deg_to_rad) * \
            np.tan(pylon['span']/pylon['xposition'])
        pylon['sweep_c_4'] = (1/deg_to_rad)*np.tan(pylon['sweep_leading_edge']*deg_to_rad) + \
            ((1-pylon['taper_ratio']) /
             (pylon['aspect_ratio']*(1-pylon['taper_ratio'])))
        pylon_out_surface = 0
    elif engine['position'] == 2:
        wing['pylon_position_chord'] = engine['length']
        pylon['length'] = 0.80*engine['length']
        pylon['taper_ratio'] = pylon['length'] / wing['pylon_position_chord']
        pylon['mean_geometrical_chord'] = wing['pylon_position_chord'] * \
            (1+pylon['taper_ratio'])/2
        pylon['mean_aerodynamic_chord'] = 2/3*wing['pylon_position_chord'] * \
            (1+pylon['taper_ratio']+pylon['taper_ratio']**2) / \
            (1+pylon['taper_ratio'])  # mac
        # t/d=0.65 figure 4.42 pag 113  ang=15
        pylon['span'] = 0.65*engine['diameter']-engine['diameter']/2
        pylon['aspect_ratio'] = pylon['span']/pylon['mean_geometrical_chord']
        pylon['area'] = pylon['span']*pylon['mean_geometrical_chord']
        pylon['sweep_c_4'] = 0
        pylon_out_surface = 0
    elif engine['position'] == 3:
        wing['pylon_position_chord'] = engine['length']
        pylon['length'] = engine['length']
        pylon['taper_ratio'] = pylon['length'] / wing['pylon_position_chord']
        pylon['mean_geometrical_chord'] = wing['pylon_position_chord'] * \
            (1+pylon['taper_ratio'])/2
        pylon['mean_aerodynamic_chord'] = 2/3*wing['pylon_position_chord'] * \
            (1+pylon['taper_ratio']+pylon['taper_ratio']**2) / \
            (1+pylon['taper_ratio'])  # mac
        # t/d=0.65 figure 4.42 pag 113  ang=15
        pylon['span'] = 0.65*engine['diameter']-engine['diameter']/2
        pylon['aspect_ratio'] = pylon['span']/pylon['mean_geometrical_chord']
        pylon['area'] = pylon['span']*pylon['mean_geometrical_chord']
        pylon['sweep_c_4'] = 0
        pylon_out_surface = 0
    elif engine['position'] == 4:
        wing['pylon_position_chord'] = wing['engine_position_chord']
        pylon['length'] = engine['length']
        pylon['taper_ratio'] = pylon['length'] / wing['pylon_position_chord']
        pylon['mean_geometrical_chord'] = wing['pylon_position_chord'] * \
            (1+pylon['taper_ratio'])/2
        pylon['mean_aerodynamic_chord'] = 2/3*wing['pylon_position_chord'] * \
            (1+pylon['taper_ratio']+pylon['taper_ratio']**2) / \
            (1+pylon['taper_ratio'])  # mac
        # x/l=-0.6 e z/d = 0.85 figure 4.41 pag 111
        pylon['span'] = 0.85*engine['diameter'] - 0.5*engine['diameter']
        pylon['xposition'] = 0.6*wing['engine_position_chord']
        pylon['aspect_ratio'] = pylon['span']/pylon['mean_geometrical_chord']
        pylon['area'] = pylon['span']*pylon['mean_geometrical_chord']
        pylon['sweep_leading_edge'] = (1/deg_to_rad) * \
            np.tan(pylon['span']/pylon['xposition'])
        pylon['sweep_c_4'] = (1/deg_to_rad)*np.tan(pylon['sweep_leading_edge']*deg_to_rad) + \
            ((1-pylon['taper_ratio']) /
             (pylon['aspect_ratio']*(1-pylon['taper_ratio'])))
        # engine out
        wing_pylon_out_position_chord = wing_engine_external_position_chord
        pylon_out_length = engine['length']
        pylon_out_taper_ratio = pylon_out_length/wing_pylon_out_position_chord
        pylon_out_mean_geometrical_chord = wing_pylon_out_position_chord * \
            (1+pylon_out_taper_ratio)/2
        pylon_out_mean_aerodynamic_chord = 2/3*wing_pylon_out_position_chord * \
            (1+pylon_out_taper_ratio+pylon_out_taper_ratio**2) / \
            (1+pylon_out_taper_ratio)  # mac
        # x/l=-0.6 e z/d = 0.85 figure 4.41 pag 111
        ppylon_out_span = 0.85*engine['diameter'] - 0.5*engine['diameter']
        pylon_out_xposition = 0.6*wing_engine_external_position_chord
        pylon_out_aspect_ratio = ppylon_out_span/pylon_out_mean_geometrical_chord
        pylon_out_surface = ppylon_out_span*pylon_out_mean_geometrical_chord
        pylon_out_sweep_leading_edge = (1/deg_to_rad) * \
            np.tan(ppylon_out_span/pylon_out_xposition)
        pylon_out_sweep = (1/deg_to_rad)*np.tan(pylon_out_sweep_leading_edge*deg_to_rad) + \
            ((1-pylon_out_taper_ratio) /
             (pylon_out_aspect_ratio*(1-pylon_out_taper_ratio)))

    #############################WETTED AREA###################################
    pylon_mean_thickness = (pylon['thickness_ratio'][0] +
                            pylon['thickness_ratio'][1])/2  # [#]espessura media
    if engine['position'] == 1 or engine['position'] == 2 or engine['position'] == 3:
        pylon['wetted_area'] = 2*pylon['area']*(1+0.25*pylon['thickness_ratio'][0]*(
            1+(pylon['thickness_ratio'][0]/pylon['thickness_ratio'][1])*pylon['taper_ratio'])/(1+pylon['taper_ratio']))  # [m2]
    else:
        pylon_wetted_area_in = 2*pylon['area']*(1+0.25*pylon['thickness_ratio'][0]*(
            1+(pylon['thickness_ratio'][0]/pylon['thickness_ratio'][1])*pylon['taper_ratio'])/(1+pylon['taper_ratio']))  # [m2]
        pylon_wetted_area_out = 2*pylon_out_surface*(1+0.25*pylon['thickness_ratio'][0]*(
            1+(pylon['thickness_ratio'][0]/pylon['thickness_ratio'][1])*pylon_out_taper_ratio)/(1+pylon_out_taper_ratio))  # [m2]
        pylon['wetted_area'] = pylon_wetted_area_in + pylon_wetted_area_out

    # -----------------------------------------------------------------------------
    #  *************** Definicoes adicionais **********************************
    # cg dos tanques de combust�vel da asa e posicao do trem d pouso principal
    # winglaywei2013
    ################################TOTAL######################################
    aircraft['wetted_area'] = fuselage['wetted_area'] + wing['wetted_area'] + horizontal_tail['wetted_area'] + vertical_tail['wetted_area'] + \
        2*engine['wetted_area']+pylon['wetted_area'] + \
        vertical_tail['dorsalfin_wetted_area'] + winglet['wetted_area']
    Fuswing_wetted_area_m2 = fuselage['wetted_area']

    log.info('Individual wetted area [m2]: {}'.format(aircraft['wetted_area']))
    log.info('---- End wetted area module ----')

    return (
        vehicle,
        xutip,
        yutip,
        xltip,
        yltip,
        xubreak,
        yubreak,
        xlbreak,
        ylbreak,
        xuraiz,
        yuraiz,
        xlraiz,
        ylraiz)

# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================

# print(wetted_area(
#         41000,
#         0.85,
#         0.85,
#         50,
#         4,
#         1,
#         0.46,
#         0.5,
#         0.8128,
#         0.3,
#         72,
#         8,
#         0.25,
#         15,
#         -2,
#         1,
#         2.9088,
#         3.1786,
#         1,
#         1,
#         16.2,
#         1.2,
#         0.5,
#         41,
#         23.35,
#         4.35,
#         0.4,
#         1,
#         0.25,
#         0,
#         2,
#         0.5))
