"""
File name :
Authors   : 
Email     : aarc.88@gmail.com
Date      : 
Last edit :
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This method converts the SPL spectrum from blade harmonic passing frequency
    to thrid octave spectrum.
    Adapted from SUAVE
Inputs:
    - SPL     - Sound Pressure Level             [dB]
Outputs:
    - [dB] 
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
def SPL_harmonic_to_third_octave(SPL,f,settings): 

    cf = settings.center_frequencies
    lf = settings.lower_frequencies
    uf = settings.upper_frequencies
    
    num_cf           = len(cf)
    num_f            = len(f)
    SPL_third_octave = np.zeros(num_cf)
    
    for i in range(num_cf):
        SPL_in_range = []
        for j in range(num_f):  
            if ((lf[i] <= f[j]) and (f[j] <= uf[i])) and (SPL[j] != 0) :   
                SPL_in_range.append(SPL[j]) 
            if len(SPL_in_range) > 0:
                SPL_third_octave[i] = SPL_arithmetic(np.atleast_2d(np.array(SPL_in_range)))
    
    return SPL_third_octave
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
