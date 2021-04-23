"""
File name :High pressure turbine parameters function
Authors   : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : September/2020
Last edit : September/2020
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
from framework.Attributes.Atmosphere.temperature_dependent_air_properties import FAIR
from framework.Performance.Engine.mass_flow_parameter import MASSFP
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================


def TURBC(Tt4, f, A4dA4_5, M4, M4_5, eta_tH, Tt4_5_R, Tt3, beta, epsilon1, epsilon2):
    # Inputs: Tt4, f, (A4/A4_5), M4, M4_5, eta_tH, Tt4_5_R, Tt3, beta,
    # epsilon1, espilon2
    # Outputs: pi_tH, tau_tH, Tt4_5

    _, ht4, _, _, _, _, _, _ = FAIR(item=1, f=f, T=Tt4)
    _, _, MFP4 = MASSFP(Tt=Tt4, f=f, M=M4)
    _, ht3, _, _, _, _, _, _ = FAIR(item=1, f=0, T=Tt3)
    m_dot_f = f*(1-beta-epsilon1-epsilon2)
    m_dot_4 = (1+f)*(1-beta-epsilon1-epsilon2)
    m_dot_4_1 = (1+f)*(1-beta-epsilon1-epsilon2) + epsilon1
    m_dot_4_5 = (1+f)*(1-beta-epsilon1-epsilon2) + epsilon1 + epsilon2
    f4_1 = m_dot_f/(m_dot_4_1-m_dot_f)
    f4_5 = m_dot_f/(m_dot_4_5-m_dot_f)
    ht4_1 = (m_dot_4*ht4+epsilon1*ht3)/(m_dot_4+epsilon1)
    _, _, Prt4_1, _, _, _, _, _ = FAIR(item=2, f=f4_1, h=ht4_1)
    Tt4_5 = Tt4_5_R

    while True:  # Label 1
        _, _, MFP4_5 = MASSFP(Tt=Tt4_5, f=f4_5, M=M4_5)
        pi_tH = (m_dot_4_5/m_dot_4)*(MFP4/MFP4_5)*A4dA4_5*np.sqrt(Tt4_5/Tt4)
        _, _, _, _, _, _, _, _ = FAIR(item=1, f=f4_5, T=Tt4_5)
        Prt4_4i = pi_tH*Prt4_1
        _, ht4_4i, _, _, _, _, _, _ = FAIR(item=3, f=f4_1, Pr=Prt4_4i)
        ht4_4 = ht4_1-eta_tH*(ht4_1-ht4_4i)
        Tau_tH = ht4_4/ht4_1
        ht4_5 = (m_dot_4_1*ht4_4+epsilon2*ht3)/(m_dot_4_1+epsilon2)
        Tt4_5n, _, _, _, _, _, _, _ = FAIR(item=2, f=f4_5, h=ht4_5)
        if np.abs(Tt4_5 - Tt4_5n) > 0.01:
            Tt4_5 = Tt4_5n
            continue  # Goto 1
        else:
            break  # Exit Loop

    return pi_tH, Tau_tH, Tt4_5
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
# print(TURBC(1.46662e3, 0.0222, 0.6, 1, 1, 0.9625, 1.1147e3, 719.4905, 0.0281, 0.0511, 0.0948))
