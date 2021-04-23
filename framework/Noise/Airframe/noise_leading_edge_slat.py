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
    - SPL_wing                   - Sound Pressure Level of the clean wing [dB]
    - Sw                         - Wing Area [sq.ft]
    - bw                         - Wing Span [ft]
    - wing_BL_thickness                     - Wing Turbulent Boundary Layer thickness [ft]
    - velocity                   - Aircraft speed [kts]
    - viscosity                  - Dynamic viscosity
    - M                          - Mach number
    - phi                        - Azimuthal angle [rad]
    - theta                      - Polar angle [rad]
    - distance                   - Distance from airplane to observer, evaluated at retarded time [ft]
    - frequency                  - Frequency array [Hz]
Outputs:
    -
TODO's:
    -

"""
# =============================================================================
# IMPORTS
# =============================================================================
import numpy as np
from framework.Noise.noise_clean_wing import noise_clean_wing
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================


def noise_leading_edge_slat(SPL_wing, V_cas, mach, phi, theta, wing_BL_thickness, distance, frequency, phase, vehicle, viscosity):

    wing = vehicle['wing']

    if phase == 'takeoff':
        delta_flap = wing['flap_deflection_takeoff']
    else:
        delta_flap = wing['flap_deflection_landing']

    # Process
    SPLslat1 = SPL_wing+3.0
    SPLslat2 = noise_clean_wing(0.15*wing['area'], wing['span'], 1, 1,
                                wing_BL_thickness, V_cas, viscosity, mach, phi, theta, distance, frequency)
    peakfactor = 3+max(SPL_wing)-max(SPLslat2)
    SPLslat2 = SPLslat2+peakfactor

    SPL = 10.*np.log10(10.0**(0.1*SPLslat1)+10.0**(0.1*SPLslat2))

    return SPL

# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
