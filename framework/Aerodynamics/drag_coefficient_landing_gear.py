"""
File name :
Authors   : 
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

# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
def drag_coefficient_landing_gear(vehicle):
    # Ref: Drag Force and Drag Coefficient
    # Sadraey M., Aircraft Performance Analysis, VDM Verlag Dr. Müller, 2009
    #
    #****************************************************************************
    #   Inputs:
    #          Dmain = Diametro do pneu do trem de pouso principal [m]
    #          nose_landing_gear['tyre_diameter'] = Diametro do pneu do trem de pouso do nariz [m]
    #          Wmain = Largura do pneu do trem de pouso principal [m]
    #          Wnose = Largura do pneu do trem de pouso do nariz [m]
    #          Lstrutmain = Comprimento do munhao do TDP principal [m]
    #          Lstrutnose = Comprimento do munhao do TDP do nariz [m]
    #          Dstrutmain = Diametro do munhao do TDP principal [m]
    #          Dstrutnose = Diametro do munhao do TDP do nariz [m]
    #          nstrut     = número de munhoes do TDP principal
    #          nmain      = numero d epneus do TDP principal por munhao
    #          nnose      = numero d epneus do TDP do nariz 
    #          wing['area']       = Wing reference area [m2]
    #****************************************************************************

    main_landing_gear = vehicle['main_landing_gear']
    nose_landing_gear = vehicle['nose_landing_gear']
    wing = vehicle['wing']

    # Constants
    nstrut = 2
    CDLGw = 0.30 #(no fairing)
    CDLGs = 1.2  # vertical cylinder LD infinity (Table 3.1)
    #
    Swheel_main = main_landing_gear['tyre_diameter']*main_landing_gear['tyre_width']
    Swheel_nose = nose_landing_gear['tyre_diameter']*nose_landing_gear['tyre_width']
    Sstrut_main = main_landing_gear['piston_length']*main_landing_gear['piston_diameter']
    Sstrut_nose = nose_landing_gear['piston_length']*nose_landing_gear['piston_diameter']
    # TDP principal 
    CD_wheel_main = 0
    for i in range(nstrut):
        CD_wheel_main = CD_wheel_main+ CDLGw*main_landing_gear['unit_wheels_number']*Swheel_main/wing['area']

    CD_strut_main = nstrut*CDLGs*Sstrut_main/wing['area']
    CD_main       = CD_strut_main  + CD_wheel_main
    # TDP nariz
    CD_wheel_nose = CDLGw*nose_landing_gear['unit_wheels_number'] *Swheel_nose/wing['area']
    CD_strut_nose = CDLGs*Sstrut_nose/wing['area']
    CD_nose       = CD_strut_nose  + CD_wheel_nose
    # Miscelleaneous drag
    CD_main = 1.10*CD_main
    CD_nose = 1.10*CD_nose

    return CD_main, CD_nose

# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
