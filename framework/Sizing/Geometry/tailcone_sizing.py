"""
Function  : tailcone_sizing.py
Title     : Tail cone sizing
Written by: Alejandro Rios
Date      : November/2019
Last edit : August/2020
Language  : Python
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This module performs the tailcone sizing

Future implementations:
    - 

Inputs:
    - Number of pax
    - Engine position
    - Fuselage height
    - Fuselage width

Outputs:
    - tailcone length
"""
########################################################################################
"""Importing Modules"""
########################################################################################
########################################################################################
"""Function definition"""
########################################################################################




import numpy as np
import os
def tailcone_sizing(NPax, PEng, fuse_height, fuse_width):
    #  Provide a sizing of the tailcone
    fusext = 0
    if NPax <= 50:
        # passenger baggage 200 kg/m3 e 20 kg por pax
        bagvol = NPax*20/200   # m3

    if PEng == 2:
        ltail_df = 2.0
    else:
        ltail_df = 1.8  # relacao coni/diametro Roskam vol 2 pag 110

    ltail = ltail_df*fuse_width+fusext

    return ltail
