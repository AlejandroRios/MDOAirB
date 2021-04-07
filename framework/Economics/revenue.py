"""
Function  : revenue.py
Title     :
Written by:
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
import pandas as pd
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================


def revenue(demand, distance, pax_capacity, pax_number):
    average_ticket_price = 110
    RPM = pax_number*distance
    passenger_revenue = pax_number*average_ticket_price
    yield_ij = passenger_revenue/RPM
    return demand*distance*yield_ij

# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
# distance = 3000
# load_factor = 0.3
# pax_capacity = 78
# pax_number = 78
# demand = 4000
# print(revenue(demand, distance, pax_capacity, pax_number))
