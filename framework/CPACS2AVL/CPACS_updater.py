"""
File name : CPACS to AVL function
Authors   : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : September/2020
Last edit : September/2020
Language  : Python 3.8 or >
Aeronautical Institute of Technology - Airbus Brazil

Description:
    - This functions takes cpacs file and write AVL input file.
TODO's:
    - Define AVL writer as a def
    - Separate run and read functions
Inputs:
    -
Outputs:
    - 
"""
# =============================================================================
# IMPORTS
# =============================================================================
import os
import sys
import linecache
import subprocess
import numpy as np
from itertools import islice
from framework.Economics.crew_salary import crew_salary
from framework.CPACS2AVL.cpacsfunctions import *
import cpacsfunctions as cpsf



# =============================================================================
# FUNCTIONS
# =============================================================================
# CPACS XML input and output dir
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
cpacs_path = os.path.join(MODULE_DIR, 'ToolInput', 'D150_v30.xml')
cpacs_out_path = os.path.join(MODULE_DIR, 'ToolOutput', 'D150_v30.xml')

tixi = cpsf.open_tixi(cpacs_out_path)
tigl = cpsf.open_tigl(tixi)

# Reference parameters
Cref = tigl.wingGetMAC(tigl.wingGetUID(1))
Sref = tigl.wingGetReferenceArea(1, 1)
b    = tigl.wingGetSpan(tigl.wingGetUID(1))

print(Sref)
xpath_write = '/cpacs/toolspecific/AVL/save_results/total_forces/'
model_xpath = '/cpacs/vehicles/aircraft/model/'

# Open and write cpacs xml output file
tixi_out = cpsf.open_tixi(cpacs_out_path)
tixi_out.updateDoubleElement(model_xpath+'reference/area', Sref, '%g')
tixi_out.updateDoubleElement(model_xpath+'reference/length', b, '%g')

# Close cpacs xml output file
tixi_out = cpsf.close_tixi(tixi_out, cpacs_out_path)