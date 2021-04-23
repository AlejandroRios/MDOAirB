"""
File name :
Authors   : 
Email     : aarc.88@gmail.com
Date      : 
Last edit :
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This calculates the installation effect, in decibels, to be added to the predicted secondary jet noise level. Adapted from SUAVE.
Inputs:
    - Ce = wing chord length at the engine location - as figure 7.3 of the SAE ARP 876D                    [m]          
    - Xe = fan exit location downstream of the leading edge (Xe<Ce) - as figure 7.3 of the SAE ARP 876D    [m] 
    - Ye = separation distance from the wing chord line to nozzle lip - as figure 7.3 of the SAE ARP 876D  [m] 
    - theta_s                                                                                              [rad]
    - Diameter_mixed                                                                                       [m] 
Outputs:
    - INST_s          [-]
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
def jet_installation_effect (Xe,Ye,theta_s,diameter_mixed,vehicle):

    wing = vehicle['wing']

    #Instalation effect
    INST_s=0.5*((wing['engine_position_chord']-Xe)**2/(wing['engine_position_chord']*diameter_mixed))*(np.exp(-Ye/diameter_mixed)*((1.8*theta_s/np.pi))-0.6)**2

    #The magnitude of the installation effect is between 0 to 2.5 dB.
    for i in range (0,24):
        if INST_s[i]>2.5:
            INST_s[i]=2.5

    return INST_s
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
