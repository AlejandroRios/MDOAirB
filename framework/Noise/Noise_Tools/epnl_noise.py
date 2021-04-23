"""
File name :
Authors   : 
Email     : aarc.88@gmail.com
Date      : 
Last edit :
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This method calculates de effective perceived noise level (EPNL) based on a
    time history Perceived Noise Level with Tone Correction (PNLT).
    Adapted from SUAVE
Inputs:
    - PNLT - Perceived Noise Level with Tone Correction
Outputs:
    - EPNL - Effective Perceived Noise Level in EPNdB
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
def epnl_noise(PNLT):
       
    # Maximum PNLT on the time history data    
    PNLT_max = np.max(PNLT)
    
    # Calculates the number of discrete points on the trajectory
    nsteps   = len(PNLT)    
    
    # Exclude sources that are not being calculated or doesn't contribute for the total noise of the aircraft
    if all(PNLT==0):
        EPNL = 0
        return(EPNL)

    # Finding the time duration for the noise history where PNL is higher than the maximum PNLT - 10 dB
    i = 0
    while PNLT[i]<=(PNLT_max-10) and i<=nsteps:
        i = i+1
    t1 = i #t1 is the first time interval
    i  = i+1

    # Correction for PNLTM-10 when it falls outside the limit of the data
    if PNLT[nsteps-1]>=(PNLT_max-10):
        t2=nsteps-2
    else:
        while i<=nsteps and PNLT[i]>=(PNLT_max-10):
            i = i+1
        t2 = i-1 #t2 is the last time interval 
    
    # Calculates the integral of the PNLT which between t1 and t2 points
    sumation = 0
    for i in range (t1-1,t2+1):
        sumation = 10**(PNLT[i]/10)+sumation
        
    # Duration Correction calculation
    duration_correction = 10*np.log10(sumation)-PNLT_max-13
                
    # Final EPNL calculation
    EPNL = PNLT_max+duration_correction
    
    return EPNL   
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
