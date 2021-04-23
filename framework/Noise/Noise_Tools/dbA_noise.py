"""
File name :
Authors   : 
Email     : aarc.88@gmail.com
Date      : 
Last edit :
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This method calculates the A-weighted level from a 1/3 octave band noise spectra 
    - This method calculates the A-weighted weighted level SPL given its stectra
    Adapted from SUAVE
Inputs:
    - SPL     - Sound Pressure Level in 1/3 octave band
    - SPL     - Sound Pressure Level             [dB] 
Outputs:
    - SPL_dbA - A-weighted Sound Pressure Level in dBA
    - SPL_dbA - A-weighted Sound Pressure Level  [dBA] 
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
def dbA_noise(SPL):

    # Matrix with the dbA attenuation factor for each octave band frequnecy ranging from 50Hz to 10000Hz
    dbA_attenuation = np.array((-30.2,-26.2,-22.5,-19.1,-16.1,-13.4,-10.9,-8.6,-6.6,-4.8,-3.2,-1.9,-0.8,0,0.6,1,1.2,1.3,1.2,1,0.5,-0.1,-1.1,-2.5))
    
    #Calculation the SPL_dbA
    SPL_dbA = SPL+dbA_attenuation
        
    return SPL_dbA

def A_weighting(SPL,f): 
 
    Ra_f       = ((12200**2)*(f**4))/ (((f**2)+(20.6**2)) * ((f**2)+(12200**2)) * (((f**2) + 107.7**2)**0.5)* (((f**2)+ 737.9**2)**0.5)) 
    A_f        =  2.0  + 20*np.log10(Ra_f) 
    SPL_dBA = SPL + A_f
    return SPL_dBA

# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
