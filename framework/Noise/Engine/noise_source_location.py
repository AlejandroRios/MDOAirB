"""
File name :
Authors   : 
Email     : aarc.88@gmail.com
Date      : 
Last edit :
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This function calculates the noise source location. Adapted from SUAVE
Inputs:
    - B                         [-]
    - Xo                        [-]
    - zk                        [-]
    - diameter_primary          [m]
    - theta_p                   [rad]
    - area_primary              [m^2]
    - area_secondary            [m^2]
    - distance_microphone       [m]
    - diameter_secondary        [m]
    - theta                     [rad]
    - theta_s                   [rad]
    - theta_m                   [rad]
    - Diameter_mixed            [m]
    - velocity_primary          [m/s]
    - velocity_secondary        [m/s]
    - velocity_mixed            [m/s]
    - velocity_aircraft         [m/s]
    - sound_ambient             [dB]
    - Str_m                     [-]
    - Str_s                     [-]
Outputs:
    - theta_p  [rad]
    - theta_s  [rad]
    - theta_m  [rad]
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
def noise_source_location(B,Xo,zk,diameter_primary,theta_p,area_primary,area_secondary,distance_microphone,
                           diameter_secondary,theta,theta_s,theta_m,Diameter_mixed,velocity_primary,velocity_secondary,
                           velocity_mixed,velocity_aircraft,sound_ambient,Str_m,Str_s):
    
    # P rimary jet source location
    XJ = np.zeros(24)
    
    for i in range(24):
        residual = diameter_primary
        XJ[i]    = (zk*diameter_primary)*(4.+4.*np.arctan((18.*theta_p[i]/np.pi)-9.)+(area_secondary/area_primary))
        B[i]     = (1./np.sin(theta))*(((Xo+XJ[i])/distance_microphone)+np.cos(theta))
        
        if (B[i]>=0.):
            theta_p[i]=np.arcsin(((B[i])**2.+1.)**(-0.5))
        else:
            theta_p[i]=np.pi-np.arcsin(((B[i])**2.+1.)**(-0.5))

        XJ[i] = (zk*diameter_primary)*(4.+4.*np.arctan((18.*theta_p[i]/np.pi)-9.)+(area_secondary/area_primary))
        
        while residual>(diameter_primary/200.):
            XJ_old = XJ[i]
            theta1 = theta_p[i]
            B[i]   = (1./np.sin(theta))*(((Xo+XJ[i])/distance_microphone)+np.cos(theta))
            
            if B[i]>=0.:
                theta_p[i] = np.arcsin(((B[i])**2.+1.)**(-0.5))
            else:
                theta_p[i] = np.pi-np.arcsin(((B[i])**2.+1.)**(-0.5))

            theta2     = theta_p[i]
            theta_p[i] = (theta1+theta2)/2.
            XJ[i]      = (zk*diameter_primary)*(4.+4.*np.arctan((18.*theta_p[i]/np.pi)-9.)+(area_secondary/area_primary))
            residual   = np.abs(XJ_old-XJ[i])

        # Secondary jet source location
        residual = diameter_secondary
        XJ_old   = 0.0
        XJ[i]    = (zk*diameter_secondary)*(2.+1.6*np.arctan((4.5*theta_s[i]/np.pi)-2.25))*(1.+0.5/np.sqrt(Str_s[i])) \
            *  np.sqrt(1.+(0.7*velocity_secondary/sound_ambient))*(velocity_secondary/(velocity_secondary-velocity_aircraft))
        
        B[i]     = (1./np.sin(theta))*(((Xo+XJ[i])/distance_microphone)+np.cos(theta))
        
        if B[i]>=0.:
            theta_s[i] = np.arcsin(((B[i])**2.+1.)**(-0.5))
        else:
            theta_s[i] = np.pi-np.arcsin(((B[i])**2.+1.)**(-0.5))
            
        XJ[i] = (zk*Diameter_mixed)*(2.+1.6*np.arctan((4.5*theta_s[i]/np.pi)-2.25))*(1.+0.5/np.sqrt(Str_s[i]))* \
            np.sqrt(1.+(0.7*velocity_secondary/sound_ambient))*(velocity_secondary/(velocity_secondary-velocity_aircraft))
        
        while residual>(Diameter_mixed/200.):
            XJ_old = XJ[i]
            theta1 = theta_s[i]
            B[i]   = (1/np.sin(theta))*(((Xo+XJ[i])/distance_microphone)+np.cos(theta))
            
            if B[i]>=0.:
                theta_s[i] = np.arcsin((B[i]**2.+1.)**(-0.5))
            else:
                theta_s[i] = np.pi-np.arcsin(((B[i])**2.+1.)**(-0.5))

            theta2     = theta_s[i]
            theta_s[i] = (theta1+theta2)/2.
            XJ[i]      = (zk*Diameter_mixed)*(2.+1.6*np.arctan((4.5*theta_s[i]/np.pi)-2.25))*(1.+0.5/np.sqrt(Str_s[i]))* \
                np.sqrt(1.+(0.7*velocity_secondary/sound_ambient))*(velocity_secondary/(velocity_secondary-velocity_aircraft))
            
            residual = np.abs(XJ_old-XJ[i])

        #Mixed jet source location
        residual = Diameter_mixed
        XJ_old   = 0.
        XJ[i] = (zk*Diameter_mixed)*(3.+np.exp(-Str_m[i])+(2.+1.1*np.arctan((18.*theta_m[i]/np.pi)-13.))+ \
            (1.+0.5/np.sqrt(Str_m[i])))*np.sqrt(0.5+0.5*velocity_mixed/sound_ambient) * \
            (velocity_mixed/(velocity_mixed-velocity_aircraft))
        
        B[i] = (1./np.sin(theta))*(((Xo+XJ[i])/distance_microphone)+np.cos(theta))
        if B[i]>=0.:
            theta_m[i] = np.arcsin(((B[i])**2.+1.)**(-0.5))
        else:
            theta_m[i] = np.pi-np.arcsin(((B[i])**2.+1.)**(-0.5))

        XJ[i]=(zk*Diameter_mixed)*(3.+np.exp(-Str_m[i])+(2.+1.1*np.arctan((18.*theta_m[i]/np.pi)-13.))+\
            (1.+0.5/np.sqrt(Str_m[i])))*np.sqrt(0.5+0.5*velocity_mixed/sound_ambient) \
            *(velocity_mixed/(velocity_mixed-velocity_aircraft))
        
        while residual>(Diameter_mixed/200.):
            XJ_old = XJ[i]
            theta1 = theta_m[i]
            B[i]   = (1./np.sin(theta))*(((Xo+XJ[i])/distance_microphone)+np.cos(theta))
            
            if B[i]>=0.:
                theta_m[i] = np.arcsin(((B[i])**2.+1.)**(-0.5))
            else:
                theta_m[i] = np.pi-np.arcsin(((B[i])**2.+1.)**(-0.5))
                
            theta2     = theta_m[i]
            theta_m[i] = (theta1+theta2)/2.
            XJ[i]      = (zk*Diameter_mixed)*(3.+np.exp(-Str_m[i])+(2.+1.1*np.arctan((18.*theta_m[i]/np.pi)-13.))+\
                (1.+0.5/np.sqrt(Str_m[i])))*np.sqrt(0.5+0.5*velocity_mixed/sound_ambient) \
                *(velocity_mixed/(velocity_mixed-velocity_aircraft))
            
            residual   = abs(XJ_old-XJ[i])
   
   
    source_location = {}
    source_location['theta_p'] = theta_p
    source_location['theta_s'] = theta_s
    source_location['theta_m'] = theta_m
    
    return source_location
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
