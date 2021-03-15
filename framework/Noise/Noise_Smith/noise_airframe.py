"""
File name :
Author    : 
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
from framework.Attributes.Atmosphere.atmosphere_ISA_deviation import atmosphere_ISA_deviation
from framework.Noise.Noise_Smith.atmospheric_attenuation import atmospheric_attenuation
import numpy as np
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
deg_to_rad = np.pi/180
kt_to_ms = 0.514444

def noise_airframe(noise_parameters, aircraft_geometry, altitude, delta_ISA, theta, fi, R, Fphase, vairp, vehicle):
    
    wing = vehicle['wing']
    horizontal_tail= vehicle['horizontal_tail']
    vertical_tail= vehicle['vertical_tail']

    nose_landing_gear = vehicle['nose_landing_gear'] 
    main_landing_gear = vehicle['main_landing_gear']


    velocity = vairp


    f = np.array([50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000])

    FTOLD = Fphase
    if FTOLD == 1:
        deltaf = aircraft_geometry['flap_deflection_TO']
    else:
        deltaf = aircraft_geometry['flap_deflection_LD']
    
    fir = fi
    pref = 2e-5
    
    # Atmospheric data at the source
    theta_source, delta_source, sigma_source, T_source, P_source, rho_source, viscosity_source, a_source = atmosphere_ISA_deviation(altitude, 0)

    mach_source = velocity/(a_source*kt_to_ms)
    viscosity_source = viscosity_source/rho_source

    # Atmospheric data at the receptor
    _, _, _, _, P_receptor, _, _, _ = atmosphere_ISA_deviation(0, 0)

    # Noise calculation

    if aircraft_geometry['wing_flap_type1_position'] == 1:
        if theta < 90:
            D = 4*(np.cos(fir*deg_to_rad))**2*(np.cos(theta*deg_to_rad/2))**2*(1-np.cos(theta*deg_to_rad))
        else:
            D = 4*(np.cos(fir*deg_to_rad))**2*(np.cos(theta*deg_to_rad/2))**2

        

        Sr = f*0.37*(wing['area']/wing['span'])*((velocity/viscosity_source)*(wing['area']/wing['span']))**(-0.2)*((1-mach_source*np.cos(theta*deg_to_rad))/velocity)

        FSr = 0.613*(10*Sr)**5*((10*Sr)**1.5+0.5)**-4
        k1 = 4.464e-5
        k2 = 5
        k3 = 0.37*wing['area']*((velocity/viscosity_source)*(wing['area']/wing['span']))**(-0.2)
        Pbw2 = k1*k3*mach_source**k2
        p2Wing = Pbw2*D*FSr/(4*np.pi*R**2*(1-mach_source*np.cos(theta*deg_to_rad))**4)
        SPLWing = 10*np.log10(p2Wing)+10*np.log10(rho_source**2*(a_source*kt_to_ms)**4/pref**2)-20*np.log10(P_source/P_receptor)
    else:
        if theta <90:
            D           = 4*(np.cos(fir*deg_to_rad))**2*(np.cos(theta*deg_to_rad/2))**2*(1-np.cos(theta*deg_to_rad))
        # else
            D           = 4*(np.cos(fir*deg_to_rad))**2*(np.cos(theta*deg_to_rad/2))**2
        Sr              = f*0.37*(wing['area']/wing['span'])*((velocity/viscosity_source)*(wing['area']/wing['span']))**(-0.2)*((1-mach_source*np.cos(theta*deg_to_rad))/velocity)
        FSr             = 0.485*(10*Sr)**4*((10*Sr)**1.35+0.5)**-4
        k1              = 4.464e-5
        k2              = 5
        k3              = 0.37*wing['area']*((velocity/viscosity_source)*(wing['area']/wing['span']))**(-0.2)
        Pbw2            = k1*k3*mach_source**k2
        p2Wing          = Pbw2*D*FSr/(4*np.pi*R**2*(1-mach_source*np.cos(theta*deg_to_rad))**4)
        SPLWing         = 10.*np.log10(p2Wing)+10*np.log10(rho_source**2*(a_source*kt_to_ms)**4/pref**2)-20*np.log10(P_source/P_receptor)

    a1                  = len(SPLWing)
    for ia1 in range(a1):
        if SPLWing[ia1]<0:
            SPLWing[ia1] = 0


    ## Horizontal tail ##
    D                   = 4*(np.cos(fir*deg_to_rad))**2*(np.cos(theta*deg_to_rad/2))**2
    Sr                  = f*0.37*(horizontal_tail['area']/horizontal_tail['span'])*((velocity/viscosity_source)*(horizontal_tail['area']/horizontal_tail['span']))**(-0.2)*((1-mach_source*np.cos(theta*deg_to_rad))/velocity)
    FSr                 = 0.613*(10*Sr)**4*((10*Sr)**1.5+0.5)**-4
    k1                  = 4.464e-5
    k2                  = 5
    k3                  = 0.37*horizontal_tail['area']*((velocity/viscosity_source)*(horizontal_tail['area']/horizontal_tail['span']))**(-0.2)
    Pbw2                = k1*k3*mach_source**k2
    p2HT                = Pbw2*D*FSr/(4*np.pi*R**2*(1-mach_source*np.cos(theta*deg_to_rad))**4)
    SPLHT               = 10.*np.log10(p2HT)+10*np.log10(rho_source**2*(a_source*kt_to_ms)**4/pref**2)-20*np.log10(P_source/P_receptor)
    a1                  = len(SPLHT)
    for ia1 in range(a1):
        if SPLHT[ia1]<0:
            SPLHT[ia1] = 0


    ## Vertical tail ##
    D                   = 4*(np.cos(fir)*deg_to_rad)**2*(np.cos(theta*deg_to_rad/2))**2
    Sr                  = f*0.37*(vertical_tail['area']/vertical_tail['span'])*((velocity/viscosity_source)*( vertical_tail['area']/vertical_tail['span']))**(-0.2)*((1-mach_source*np.cos(theta*deg_to_rad))/velocity)
    FSr                 = 0.613*(10*Sr)**4*((10*Sr)**1.5+0.5)**-4
    k1                  = 4.464e-5
    k2                  = 5
    k3                  = 0.37*vertical_tail['area']*((velocity/viscosity_source)*( vertical_tail['area']/vertical_tail['span']))**(-0.2)
    Pbw2                = k1*k3*mach_source**k2
    p2VT                = Pbw2*D*FSr/(4*np.pi*R**2*(1-mach_source*np.cos(theta*deg_to_rad))**4)
    SPLVT               = 10*np.log10(p2VT)+10*np.log10(rho_source**2*(a_source*kt_to_ms)**4/pref**2)-20*np.log10(P_source/P_receptor)
    a1                  = len(SPLVT)
    for ia1 in range(a1):
        if SPLVT[ia1]<0:
            SPLVT[ia1] = 0


    ## Leading edge slats ##
    if aircraft_geometry['slats_position']==1:
        D               = 4*(np.cos(fir*deg_to_rad))**2*(np.cos(theta*deg_to_rad/2))**2
        Sr              = f*0.37*(wing['area']/wing['span'])*((velocity/viscosity_source)*(wing['area']/wing['span']))**(-0.2) *((1-mach_source*np.cos(theta*deg_to_rad))/velocity)
        FSr             = 0.613*(2.19*Sr)**4*((2.19*Sr)**1.5+0.5)**-4
        k1              = 4.464e-5
        k2              = 5
        k3              = 0.37*wing['area']*((velocity/viscosity_source)*(wing['area']/wing['span']))**(-0.2)
        Pbw2            = k1*k3*mach_source**k2
        p2Slat          = Pbw2*D*FSr/(4*np.pi*R**2*(1-mach_source*np.cos(theta*deg_to_rad))**4)
        SPLSlat         = 10.*np.log10(p2Slat)+10*np.log10(rho_source**2*(a_source*kt_to_ms)**4/pref**2)-20*np.log10(P_source/P_receptor)
        a1              = len(SPLSlat)
        for ia1 in range(a1):
            if SPLSlat[ia1]<0:
                SPLSlat[ia1] = 0
    else:
    	SPLSlat              = np.zeros(len(f))

 
    ## Single- and double-slotted trailing edge flaps ##
    if aircraft_geometry['slots_number']==1 or aircraft_geometry['slots_number']==2:

        D               = 3*(np.sin(deltaf*deg_to_rad)*np.cos(theta*deg_to_rad)+np.cos(deltaf*deg_to_rad)*np.sin(theta*deg_to_rad)*np.cos(fir*deg_to_rad))**2
        if theta <90:
            D           = D/1
        else:
            D           = D/(1-np.cos(theta*deg_to_rad))**(-4)

        Sr              = (f/velocity)*(aircraft_geometry['fuselage_surface']/aircraft_geometry['fuselage_length'])*(1-mach_source*np.cos(theta*deg_to_rad))
        FSr             = (Sr<2)*(0.0480*Sr)+(Sr>=2)*(0.1406*Sr**-0.55)
        k1              = 2.787e-4
        k2              = 6
        k3              = aircraft_geometry['fuselage_surface']*(np.sin(deltaf*deg_to_rad))**2
        Pbw2            = k1*k3*mach_source**k2
        p2Flap          = Pbw2*D*FSr/(4*np.pi*R**2*(1-mach_source*np.cos(theta*deg_to_rad))**4)
        SPLFlap         = 10*np.log10(p2Flap)+10*np.log10(rho_source**2*(a_source*kt_to_ms)**4/pref**2)-20*np.log10(P_source/P_receptor)
    else:
        D               = 3*(np.sin(deltaf*deg_to_rad)*np.cos(theta*deg_to_rad)+np.cos(deltaf*deg_to_rad)*np.sin(theta*deg_to_rad)*np.cos(fir*deg_to_rad))**2
        if theta <90:
            D           = D/1
        else:
            D           = D/(1-np.cos(theta*deg_to_rad))**(-4)

        Sr              = (f/velocity)*(aircraft_geometry['fuselage_surface']/aircraft_geometry['fuselage_length'])*(1-mach_source*np.cos(theta*deg_to_rad))
        if Sr < 2:
            FSr         = 0.0257*Sr
        else:
            FSr         = 0.0536*Sr**-0.0625

        k1              = 3.509e-4
        k2              = 6
        k3              = aircraft_geometry['fuselage_surface']*(np.sin(deltaf*deg_to_rad))**2
        Pbw2            = k1*k3*mach_source**k2
        p2Flap          = Pbw2*D*FSr/(4*np.pi*R**2*(1-mach_source*np.cos(theta*deg_to_rad))**4)
        SPLFlap         = 10.*np.log10(p2Flap)+10*np.log10(rho_source**2*(a_source*kt_to_ms)**4/pref**2)-20*np.log10(P_source/P_receptor)

    a1                  = len(SPLFlap)
    for ia1 in range(a1):
        if SPLFlap[ia1]<0:
            SPLFlap[ia1] = 0

    ## Main landing gear ##
    if aircraft_geometry['main_landing_gear_position']==1:
        if aircraft_geometry['main_landing_gear_wheels'] == 1 or aircraft_geometry['main_landing_gear_wheels'] == 2:
            if theta <90:
                D       = 1.5*(np.sin(theta*deg_to_rad))**2
            else:
                D       = 1.5*(np.sin(theta*deg_to_rad))**2*(1-np.cos(theta*deg_to_rad))**4

            Sr          = f*(main_landing_gear['tyre_diameter']/velocity)*(1-mach_source*np.cos(theta*deg_to_rad))
            FSr         = 13.59*Sr**2*(30.0+Sr**2)**-2.25
            k1          = 4.349e-4
            k2          = 6
            k3          = aircraft_geometry['main_landing_gear_wheels'] *main_landing_gear['tyre_diameter']**2
            Pbw2        = k1*k3*mach_source**k2
            p2G         = Pbw2*D*FSr/(4*np.pi*R**2*(1-mach_source*np.cos(theta*deg_to_rad))**4)
        else:
            if theta <90:
                D       = 1.5*(np.sin(theta*deg_to_rad))**2
            else:
                D       = 1.5*(np.sin(theta*deg_to_rad))**2*(1-np.cos(theta*deg_to_rad))**4

            Sr          = f*(main_landing_gear['tyre_diameter']/velocity)*(1-mach_source*np.cos(theta*deg_to_rad))
            FSr         = 0.0577*Sr**2*(5.0+0.25*Sr**2)**-1.5
            k1          = 3.414e-4
            k2          = 6
            k3          = aircraft_geometry['main_landing_gear_wheels'] *main_landing_gear['tyre_diameter']**2
            Pbw2        = k1*k3*mach_source**k2
            p2G         = Pbw2*D*FSr/(4*np.pi*R**2*(1-mach_source*np.cos(theta*deg_to_rad))**4)

        if aircraft_geometry['main_landing_gear_wheels'] ==1 or aircraft_geometry['main_landing_gear_wheels'] ==2:
            if theta <90:
                D       = 3*(np.sin(theta*deg_to_rad))**2*(np.sin(fir*deg_to_rad))**2
            else:
                D       = 3*(np.sin(theta*deg_to_rad))**2*(np.sin(fir*deg_to_rad))**2*(1-np.cos(theta*deg_to_rad))**4

            Sr          = f*(main_landing_gear['tyre_diameter']/velocity)*(1-mach_source*np.cos(theta*deg_to_rad))
            FSr         = 5.325*Sr**2*(30.0+Sr**2)**-1
            k1          = 2.753e-4
            k2          = 6
            k3          = aircraft_geometry['main_landing_gear_length']*main_landing_gear['tyre_diameter']
            Pbw2        = k1*k3*mach_source**k2
            p2S         = Pbw2*D*FSr/(4*np.pi*R**2*(1-mach_source*np.cos(theta*deg_to_rad))**4)
        else:
            if theta <90:
                D       = 3*(np.sin(theta*deg_to_rad))**2*(np.sin(fir*deg_to_rad))**2
            else:
                D       = 3*(np.sin(theta*deg_to_rad))**2*(np.sin(fir*deg_to_rad))**2*(1-np.cos(theta*deg_to_rad))**4
            
            Sr          = f*(main_landing_gear['tyre_diameter']/velocity)*(1-mach_source*np.cos(theta*deg_to_rad))
            FSr         = 1.280*Sr**3*(1.06+Sr**2)**-3
            k1          = 2.753e-4
            k2          = 6
            k3          = aircraft_geometry['main_landing_gear_length']*main_landing_gear['tyre_diameter']
            Pbw2        = k1*k3*mach_source**k2
            p2S         = Pbw2*D*FSr/(4*np.pi*R**2*(1-mach_source*np.cos(theta*deg_to_rad))**4)
        
        p2MLG           = aircraft_geometry['main_landing_gear_number']*(p2G+p2S)
        SPLMLG          = 10*np.log10(p2MLG)+10*np.log10(rho_source**2*(a_source*kt_to_ms)**4/pref**2)-20*np.log10(P_source/P_receptor)
        a1              = len(SPLMLG)
        for ia1 in range(a1):
            if SPLMLG[ia1]<0:
                SPLMLG[ia1] = 0
            
        
    else:
        SPLMLG          = np.zeros(len(f))
    
    
    ## Nose landing gear ##
    if aircraft_geometry['nose_landing_gear_position']==1:
        if aircraft_geometry['nose_landing_gear_wheels']==1 or aircraft_geometry['nose_landing_gear_wheels']==2:
            if theta <90:
                D       = 1.5*(np.sin(theta*deg_to_rad))**2
            else:
                D       = 1.5*(np.sin(theta*deg_to_rad))**2*(1-np.cos(theta*deg_to_rad))**4
            
            Sr          = f*(nose_landing_gear['tyre_diameter'] /velocity)*(1-mach_source*np.cos(theta*deg_to_rad))
            FSr         = 13.59*Sr**2*(30.0+Sr**2)**-2.25
            k1          = 4.349e-4
            k2          = 6
            k3          = aircraft_geometry['nose_landing_gear_wheels']*nose_landing_gear['tyre_diameter'] **2
            Pbw2        = k1*k3*mach_source**k2
            p2G         = Pbw2*D*FSr/(4*np.pi*R**2*(1-mach_source*np.cos(theta*deg_to_rad))**4)
        else:
            if theta <90:
                D       = 1.5*(np.sin(theta*deg_to_rad))**2
            else:
                D       = 1.5*(np.sin(theta*deg_to_rad))**2*(1-np.cos(theta*deg_to_rad))**4
            
            Sr          = f*(nose_landing_gear['tyre_diameter'] /velocity)*(1-mach_source*np.cos(theta*deg_to_rad))
            FSr         = 0.0577*Sr**2*(5.0+0.25*Sr**2)**-1.5
            k1          = 3.414e-4
            k2          = 6
            k3          = aircraft_geometry['nose_landing_gear_wheels']*nose_landing_gear['tyre_diameter'] **2
            Pbw2        = k1*k3*mach_source**k2
            p2G         = Pbw2*D*FSr/(4*np.pi*R**2*(1-mach_source*np.cos(theta*deg_to_rad))**4)
        
        if aircraft_geometry['nose_landing_gear_wheels']==1 or aircraft_geometry['nose_landing_gear_wheels']==2:
            if theta <90:
                D       = 3*(np.sin(theta*deg_to_rad))**2*(np.sin(fir*deg_to_rad))**2
            else:
                D       = 3*(np.sin(theta*deg_to_rad))**2*(np.sin(fir*deg_to_rad))**2*(1-np.cos(theta*deg_to_rad))**4
            
            Sr          = f*(nose_landing_gear['tyre_diameter'] /velocity)*(1-mach_source*np.cos(theta*deg_to_rad))
            FSr         = 5.325*Sr**2*(30.0+Sr**2)**-1
            k1          = 2.753e-4
            k2          = 6
            k3          = aircraft_geometry['nose_landing_gear_length']*nose_landing_gear['tyre_diameter'] 
            Pbw2        = k1*k3*mach_source**k2
            p2S         = Pbw2*D*FSr/(4*np.pi*R**2*(1-mach_source*np.cos(theta*deg_to_rad))**4)
        else:
            if theta <90:
                D       = 3*(np.sin(theta*deg_to_rad))**2*(np.sin(fir*deg_to_rad))**2
            else:
                D       = 3*(np.sin(theta*deg_to_rad))**2*(np.sin(fir*deg_to_rad))**2*(1-np.cos(theta*deg_to_rad))**4
            
            Sr          = f*(main_landing_gear['tyre_diameter']/velocity)*(1-mach_source*np.cos(theta*deg_to_rad))
            FSr         = 1.280*Sr**3*(1.06+Sr**2)**-3
            k1          = 2.753e-4
            k2          = 6
            k3          = aircraft_geometry['nose_landing_gear_length']*main_landing_gear['tyre_diameter']
            Pbw2        = k1*k3*mach_source**k2
            p2S         = Pbw2*D*FSr/(4*np.pi*R**2*(1-mach_source*np.cos(theta*deg_to_rad))**4)
        
        p2NLG           = aircraft_geometry['nose_landig_gear_number']*(p2G+p2S)
        SPLNLG          = 10.*np.log10(p2NLG)+10*np.log10(rho_source**2*(a_source*kt_to_ms)**4/pref**2)-20*np.log10(P_source/P_receptor)
        a1              = len(SPLNLG)
        for ia1 in range(a1):
            if SPLNLG[ia1]<0:
                SPLNLG[ia1] = 0
            
        
    else:
        SPLNLG          = np.zeros(len(f))
    
    
    
    ## Global ##
    
    SPLTotal            = 10*np.log10(10**(0.1*SPLWing)+10**(0.1*SPLHT)+10**(0.1*SPLVT)+10**(0.1*SPLSlat)+10**(0.1*SPLFlap)+10**(0.1*SPLMLG)+10**(0.1*SPLNLG))
    a1                  = len(SPLTotal)
    for ia1 in range(a1):
        if SPLTotal[ia1]<0:
            SPLTotal[ia1] = 0
        
    
    
    ## Atenuação do ruído na atmosfera ##
    ft, alfaamortt, amorttott, deltaLamort, SPLrt = atmospheric_attenuation(T_source,noise_parameters,R,f)
    SPLAC               = SPLTotal-deltaLamort.T


     
    return f, SPLAC



# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
