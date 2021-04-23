"""
File name :
Authors   : 
Email     : aarc.88@gmail.com
Date      : 
Last edit :
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This computes the certification noise limits as a function of the aircraft weight [lbs] 
    and number of engines for each segment. 
    Adapted from SUAVE
Inputs:
    - vehicle
    - results
Outputs:
    - noise_approach_limit  - Approach noise limit as a function of the landing weight, [EPNdB]
    - noise_flyover_limit   - Flyover noise limit as a function of the takeoff weight,  [EPNdB]
    - noise_sideline_limit  - Sideline noise limit as a function of the takeoff weight, [EPNdB]
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
def noise_certification_limits(results,vehicle):
    
    #unpack
    weight_approach     = np.float(results.approach.segments.descent.conditions.weights.total_mass[-1]) / Units.lbs
    weight_tow_mission  = np.float(results.flyover.segments.climb.conditions.weights.total_mass[-1])     / Units.lbs
    n_engines           = np.int(vehicle.propulsors.turbofan.number_of_engines)
    
    #Determination of the number of engines
    if n_engines > 3:
        C_flyover = 8.96*(10**-3.)
    elif n_engines == 3:
        C_flyover = 1.27*(10**-2.)
    else:
        C_flyover = 2.13*(10**-2)
    
    #Constants for the Stage III noise limits
    T_flyover  = 4.
    C_approach = 1.68*(10**-8.)
    T_approach = 2.33
    C_sideline = 6.82*(10**-7.)
    T_sideline = 2.56
    
    #Calculation of noise limits based on the weight
    noise_sideline_limit = np.around(np.log((weight_tow_mission/C_sideline))* T_sideline /np.log(2),decimals=1)
    noise_flyover_limit  = np.around(np.log((weight_tow_mission/C_flyover)) * T_flyover  /np.log(2),decimals=1)
    noise_approach_limit = np.around(np.log((weight_approach   /C_approach))* T_approach /np.log(2),decimals=1)

    certification_limits = Data()
    certification_limits.noise_sideline_limit  = noise_sideline_limit
    certification_limits.noise_flyover_limit   = noise_flyover_limit 
    certification_limits.noise_approach_limit  = noise_approach_limit 

    return certification_limits

# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
