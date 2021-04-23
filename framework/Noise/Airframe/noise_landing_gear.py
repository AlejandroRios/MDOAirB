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
    - main_landing_gear['tyre_diameter']         - Landing gear tyre diameter                                     [ft]
    - main_landing_gear['piston_length']         - Lading gear strut length                                       [ft]
    - main_landing_gear['unit_wheels_number']    - Number of main_landing_gear['unit_wheels_number'] per unit                                      [-]
    - mach         - Mach number                                                    [-]
    - velocity  - Aircraft speed                                                 [kts]
    - phi       - Azimuthal angle                                                [rad]
    - theta     - Polar angle                                                    [rad]
    - distance  - Distance from airplane to observer, evaluated at retarded time [ft]
    - frequemcy - Frequency array                                                [Hz] 
Outputs:
    - SPL           - Sound Pressure Level of the landing gear         [dB]
    - OASPL         - Overall Sound Pressure Level of the landing gear [dB]
TODO's:
    -

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
kts_2_fts = 1.6878098571


def noise_landing_gear(mach, V_cas, phi, theta, distance, frequency, vehicle):

    nose_landing_gear = vehicle['nose_landing_gear']
    main_landing_gear = vehicle['main_landing_gear']

    velocity_fts = V_cas*kts_2_fts
    velocity_kts = V_cas

    if (main_landing_gear['unit_wheels_number'] == 1 or main_landing_gear['unit_wheels_number'] == 2):
        G1 = 13+np.log10(4.5*((frequency*main_landing_gear['tyre_diameter']/(velocity_fts*(1-mach*np.cos(theta))))**2) *
                         (12.5+((frequency*main_landing_gear['tyre_diameter']1/(velocity_fts*(1-mach*np.cos(theta))))**2))**-2.25)
        G2 = (13+np.log10(2.0*(frequency*main_landing_gear['tyre_diameter']/(velocity_fts*(1-mach*np.math.cos(theta)))**2.0)) *
              (30+(frequency*main_landing_gear['tyre_diameter']/(velocity_fts*(1-mach*np.cos(theta))))**8)**-1*(0.34*main_landing_gear['piston_length']/main_landing_gear['tyre_diameter'])) * \
            (np.math.sin(phi))**2
    elif main_landing_gear['unit_wheels_number'] == 4:
        G1 = 12+np.log10(frequency*main_landing_gear['tyre_diameter']/(velocity_fts*(1-mach*np.cos(theta))))**2 \
            * (0.4+(frequency*main_landing_gear['tyre_diameter']/(velocity_fts*(1-mach*np.cos(theta))))**2)**(-1.6)
        G2 = (12+np.log10(7.0*(frequency*main_landing_gear['tyre_diameter']/(velocity_fts*(1-mach*np.cos(theta))))**3.0 *
                          (1.06+(frequency*main_landing_gear['tyre_diameter']/(velocity_fts*(1-mach*np.cos(theta))))**2)**(-3.0)*(1)))*(np.sin(phi))**2

    G3 = 12.79+np.log10(0.34*main_landing_gear['piston_length'] /
                        main_landing_gear['tyre_diameter'])*(np.sin(phi))**2
    SPL = 60.*np.log10(velocity_kts/194.0)+20.*np.log10(
        main_landing_gear['tyre_diameter']/distance)+10.*np.log10(10.0**G1+10.0**G2)
    OASPL = 60.*np.log10(velocity_kts/194.0)+20.*np.log10(
        main_landing_gear['tyre_diameter']/distance)+10.*np.log10(10.0**12.52+10.0**G3)

    return SPL
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
