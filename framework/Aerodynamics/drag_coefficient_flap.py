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
    -
Outputs:
    -
TODO's:
    -

"""
# =============================================================================
# IMPORTS
# =============================================================================

# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
def drag_coefficient_flap(vehicle):
    #
    # Ref: Drag Force and Drag Coefficient
    # Sadraey M., Aircraft Performance Analysis, VDM Verlag Dr. Müller, 2009
    #**************************************************************************
    # Input:
    # wing['flap_deflection_landing']: flap deflection [degrees]
    # wing['rear_spar_ref']: chordwise location of aft spar
    #**************************************************************************
    # Considerations:
    # Internal flap: double sllotted
    # External flap: single slotted
    #**************************************************************************
    wing = vehicle['wing']

    A_int = 0.0011
    B_int = 1
    A_ext = 0.00018
    B_ext = 2
    cflap= 1 -(wing['rear_spar_ref'] +0.02)
    # 
    cdflap_int = cflap*A_int*(wing['flap_deflection_landing']**B_int)
    cdflap_ext = cflap*A_ext*(wing['flap_deflection_landing']**B_ext)
    cd_flap     = cdflap_int + cdflap_ext

    return cd_flap
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
