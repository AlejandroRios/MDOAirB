"""
File name :
Authors   : 
Email     : aarc.88@gmail.com
Date      : 
Last edit :
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This function calculates the adjustments, in decibels, to be added to the predicted jet noise levels due to
    external plugs in coaxial jets. Adapted from SUAVE.
Inputs:
    - Velocity_primary      [m/s]
    - Velocity_secondary    [m/s]
    - Velocity_mixed        [m/s]
    - Diameter_primary      [m]
    - Diameter_secondary    [m]
    - Diameter_mixed        [m]
    - Plug_diameter         [m]
    - sound_ambient         [dB]
    - theta_p               [rad]
    - theta_s               [rad]
    - theta_m               [rad]
    - Outputs:
    -
TODO's:
    - PG_p        [dB]
    - PG_s        [dB]
    - PG_m        [dB]

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
def external_plug_effect(V_primary,V_secondary, V_mixed, diameter_primary,
                         diameter_secondary,diameter_mixed, plug_diameter, sound_ambient, theta_p,theta_s,theta_m):

    # Primary jet
    PG_p = 0.1*(V_primary/sound_ambient)*(10-(18*theta_p/np.pi))*plug_diameter/diameter_primary
    
    # Secondary jet
    PG_s = 0.1*(V_secondary/sound_ambient)*(6-(18*theta_s/np.pi))*plug_diameter/diameter_secondary
    
    # Mixed jet
    PG_m = 0.1*(V_primary*V_mixed/(sound_ambient**2))*(9-(18*theta_m/np.pi))*plug_diameter/diameter_mixed
    
    # Pack Results 
    jet_plug_effects = {}
    jet_plug_effects['PG_p'] = PG_p
    jet_plug_effects['PG_s'] = PG_s
    jet_plug_effects['PG_m'] = PG_m 

    return jet_plug_effects

# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
# V_primary = 100
# V_secondary = 200
# V_mixed =250
# diameter_primary = 0.5
# diameter_secondary = 0.3
# diameter_mixed = 0.45
# plug_diameter = 0.1
# sound_ambient = 1
# theta_p = 0.1
# theta_s = 0.1
# theta_m = 0.1
# print(external_plug_effect(V_primary,V_secondary, V_mixed, diameter_primary,
#                          diameter_secondary,diameter_mixed, plug_diameter, sound_ambient, theta_p,theta_s,theta_m))