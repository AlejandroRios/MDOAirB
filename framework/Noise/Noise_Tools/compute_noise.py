"""
File name :
Authors   : 
Email     : aarc.88@gmail.com
Date      : 
Last edit :
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This method calculates approach noise of a turbofan aircraft. Adapted from SUAVE.
Inputs:
    - mission
    - aircraft configuration 
Outputs:
    - SPL    -  [dB]
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
def compute_noise(config,noise_segment,noise_analyses):
    
    engine_flag    = config.engine_flag  #remove engine noise component from the approach segment 
    turbofan       = config.propulsors['turbofan']
    engine_noise   = noise_SAE(turbofan,noise_segment,noise_analyses,config)
    
    airframe_noise = noise_airframe_Fink(noise_segment,noise_analyses,config ) 

    noise_sum      = 10. * np.log10(10**(airframe_noise.EPNL_total/10)+ (engine_flag)*10**(engine_noise.EPNL_total/10))

    return noise_sum

# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
