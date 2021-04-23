"""
File name :
Authors   : 
Email     : aarc.88@gmail.com
Date      : 
Last edit :
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This compute the total SPL given mutiple acoustic pressure ratios 
    of one of mutiple sources
    - This computes the total SPL from multiple sources 
    using decibel arithmetic  
    
Inputs:
    - Pressure Ratios       [unitless]
    - Sound Pressure Level        [decibel]
Outputs:
    - Sound Pressure Level  [decibel]
    - Sound Pressure Level        [decibel]
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
def pressure_ratio_to_SPL_arithmetic(p_pref_total):
    SPL_total = 10*np.log10(np.sum(p_pref_total))
    return SPL_total

## @ingroupMethods-Noise-Fidelity_One-Noise_Tools
def SPL_arithmetic(SPL):
    p_prefs   = 10**(SPL/10)
    SPL_total = 10*np.log10(np.sum(p_prefs, axis = 1))
    return SPL_total
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
