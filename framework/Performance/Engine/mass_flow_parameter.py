"""
File name : Mass flow parameters function
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
from scipy import optimize
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================


def MASSFP(Tt=None, f=None, M=None, ht=None, Prt=None, gammat=None, at=None):
    # Inputs: Case, Tt, f, and M
    # Outputs: Tt/T, Pt/P, and MFP

    list_variables = [Tt, f, M, ht, Prt, gammat, at]
    nargin = sum(x is not None for x in list_variables)

    if nargin < 7:
        # in: T0 [K] f | out: ht [J/kg] Prt [Pa] R0 [J/KgK]
        _, ht, Prt, _, _, _, gammat, at = FAIR(1, f=f, T=Tt)

    global h_t, g_c, f_g, M_g
    h_t = ht
    g_c = 1             # [m/s]
    f_g = f
    M_g = M

    Vguess = (M*at)/(1+((gammat-1)/2)*M**2)

    optimize.fsolve(vals, Vguess)
    TtdT = Tt/T_g
    PtdP = Prt/Pr_g
    MFP = (M/PtdP)*np.sqrt((gamman_g*g_c)/R_g*TtdT)

    return TtdT, PtdP, MFP


def vals(V):

    global T_g, Pr_g, R_g, gamman_g, a_g
    h = h_t - V**2/(2*g_c)
    T_g, _, Pr_g, _, _, R_g, gamman_g, a_g = FAIR(2, f=f_g, h=h)

    Vn = M_g*a_g
    if V != 0:
        Verror = np.abs((V-Vn)/V)
    else:
        Verror = np.abs(V-Vn)
    return Verror


# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================

# import time
# start_time = time.time()
# print(MASSFP(Tt=1.4662e3, f=0.0222, M=1))
# print("--- %s seconds ---" % (time.time() - start_time))
