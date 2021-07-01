"""
File name : Atmosphere function
Authors   : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : September/2020
Last edit : September/2020
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - International Standard Atmosphere (ISA) in SI units
Inputs:
    - Altitude [ft]
Outputs:
    - T = temperature (K),
    - p = pressure (N/m2),
    - rho = density (kg/m3),
    - a = sound speed (m/s)
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


def atmosphere(h):
    ft_to_m = 0.3048
    h = h*ft_to_m
    h = h/1000
    h1 = 11
    h2 = 20
    h3 = 32
    L0 = -6.5e-3
    L2 = 1e-3
    g0 = 9.80665
    m0 = 28.96442
    R0 = 8314.32
    R = R0/m0
    T0 = 288.15
    p0 = 1.01325e5
    rho0 = 1.2250
    T1 = T0+L0*h1*1e3
    p1 = p0*(T1/T0)**(-g0/(R*L0))
    rho1 = rho0*(T1/T0)**(-(1+g0/(R*L0)))
    T2 = T1
    p2 = p1*np.exp(-g0/(R*T2)*(h2-h1)*1e3)
    rho2 = rho1*np.exp(-g0/(R*T2)*(h2-h1)*1e3)

    if h <= h1:
        # Troposphere:
        T = T0+L0*h*1e3
        p = p0*(T/T0)**(-g0/(R*L0))
        rho = rho0*(T/T0)**(-(1+g0/(R*L0)))
    elif h <= h2:
        # Tropopause and low stratosphere:
        T = T1
        p = p1*np.exp(-g0/(R*T)*(h-h1)*1e3)
        rho = rho1*np.exp(-g0/(R*T)*(h-h1)*1e3)
    elif h <= h3:
        # Stratosphere:
        T = T2+L2*(h-h2)*1e3
        p = p2*(T/T2)**(-g0/(R*L2))
        rho = rho2*(T/T2)**(-(1+g0/(R*L2)))
    gamma = 1.4
    a = np.sqrt(gamma*R*T0)
    return T, p, rho, a
# =============================================================================
# MAIN
# =============================================================================


# =============================================================================
# TEST
# =============================================================================
# h = 2500
# print(atmosphere(h))
