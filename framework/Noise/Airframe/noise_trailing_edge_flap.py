"""
File name :
Authors   : 
Email     : aarc.88@gmail.com
Date      : 
Last edit :
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description: 
    - Trailing edge flap noise calcilation. Adapted from SUAVE.
    - Reference: Martin R. Fink, Airframe noise prediction method
    - pag 34, equation 22
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
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
kts_2_fts = 1.6878098571


def noise_trailing_edge_flap(V_cas, mach, phi, theta, distance, frequency, phase ,vehicle):

    wing = vehicle['wing']
    # Process
    G = np.zeros(24)

    test = frequency*wing['flap_chord']/(V_cas*kts_2_ftst*(1-mach*np.cos(theta)))

        if (wing['flap_slots_number'] == 1 or wing['flap_slots_number'] == 2):
        for i in range(0, 24):
            if (test[i] < 2):
                G[i] = 99+10*np.log10(test[i])
            elif (test[i] < 20):
                G[i] = 103.82-6*np.log10(test[i])
            else:
                G[i] = 135.04-30*np.log10(test[i])

    elif wing['flap_slots_number'] == 3:
        for i in range(0, 24):
            if(test[i] < 2):
                G[i] = 99+10*np.log10(test[i])
            elif (test[i] < 75):
                G[i] = 102.61-2*np.log10(test[i])
            else:
                G[i] = 158.11-30*np.log10(test[i])

    G = np.transpose(G)

    if phase == 'takeoff':
        delta_flap = wing['flap_deflection_takeoff']
    else:
        delta_flap = wing['flap_deflection_landing']

    if theta+delta_flap >= np.pi:
        directivity = 0.0
    else:
        directivity = 20.0 * \
            np.log10(np.sin(theta) * (np.cos(phi))**2 * np.sin(theta+delta_flap))

    SPL = G+10*np.log10(wing['flap_area']*(np.sin(delta_flap))**2/(distance**2)) + \
        60*np.log10((V_cas/kts_2_fts)/100.0)+directivity

    return SPL

# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
