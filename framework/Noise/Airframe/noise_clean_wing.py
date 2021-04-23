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
import numpy as np
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
kts_2_fts = 1.6878098571

def noise_clean_wing(ND,IsHorz,wing_BL_thickness,V_cas,viscosity,mach,phi,theta,distance,frequency, vehicle):
    wing = vehicle['wing']

    delta  = 0.37*(wing['area']/wing['span'])*((V_cas*kts_2_fts)*wing['area']/(wing['span']*viscosity))**(-0.2)

    if IsHorz==1:
        DIR = np.cos(phi)
    elif IsHorz==0:
        DIR = np.sin(phi)


    if DIR==0:
        SPL = np.zeros(24)
    else:

        fmax  = 0.1*(V_cas*kts_2_fts)/(delta*(1-mach*np.cos(theta)))
        fmaxw = 0.1*(V_cas*kts_2_fts)/wing_BL_thickness

        OASPL = 50*np.log10((V_cas)/100.0)+10*np.log10(delta*wing['span']/(distance**2.0))+8*ND+ \
            20*np.log10(DIR*np.sin(theta)*np.cos(theta/2.0))+104.3

        SPL   = OASPL+10.0*np.log10(0.613*(frequency/fmax)**4*((frequency/fmax)**1.5+0.5)**(-4))-0.03*np.abs(((frequency/fmaxw)-1))**1.5

    return SPL
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
