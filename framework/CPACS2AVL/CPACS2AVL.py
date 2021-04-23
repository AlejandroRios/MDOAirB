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


from framework.utilities.logger import get_logger

log = get_logger(__file__.split('.')[0])

log.info('-------- Start Run CPACS2AVL --------')
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
# CPACS XML input and output dir
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
cpacs_path = os.path.join(MODULE_DIR, 'ToolInput', 'D150_v30.xml')
cpacs_out_path = os.path.join(MODULE_DIR, 'ToolOutput', 'D150_v30.xml')

# Open tixi and tigl
tixi = cpsf.open_tixi(cpacs_path)
tigl = cpsf.open_tigl(tixi)

tigl_version= tigl.getVersion()
print('Tigl version :', tigl_version)

# Dir inside cpacs file pointing to paramaters
model_xpath = '/cpacs/vehicles/aircraft/model/'
profiles_xpath = '/cpacs/vehicles/profiles/'
vehicles_xpath = '/cpacs/vehicles/'
toolspecific_xpath = '/cpacs/toolspecific/AVL/'

n_wings = tigl.getWingCount()

# Reference parameters
Cref = tigl.wingGetMAC(tigl.wingGetUID(1))
Sref = tigl.wingGetReferenceArea(1, 1)
b    = tigl.wingGetSpan(tigl.wingGetUID(1))

avl_file_name = 'avl_file.avl'
aircraft_name = 'aircraft'

# Start writing avl input file
file = open(avl_file_name, 'w')
file.write(aircraft_name+'\n')
file.write('0.0\n')
file.write('0 0 0\n')
file.write('{:.3f} {:.3f} {:.3f}\n'.format(Sref, Cref[0], b))
file.write('0.0 0.0 0.0\n')
file.write('0.1\n')

# Wing vortex discretization number and format
Nchord = cpsf.get_value(tixi, toolspecific_xpath+ 'vlm_autopanels_c/')
Cspace = cpsf.get_value(tixi, toolspecific_xpath+ 'vlm_distpanels_c/')
Nspan = cpsf.get_value(tixi, toolspecific_xpath+ 'vlm_autopanels_s/')
Sspace = cpsf.get_value(tixi, toolspecific_xpath+ 'vlm_distpanels_c/')

# Surface level writing
for i in range(1, n_wings+1):
    n_segments = tigl.wingGetSectionCount(i)
    wing_name = tigl.wingGetUID(i)

    component_segment_UID = tigl.wingGetComponentSegmentUID(i, 1)
    n_component_segment = tigl.getControlSurfaceCount(component_segment_UID)
    n_control_surfaces = tigl.getControlSurfaceCount(component_segment_UID)
 
    file.write('SURFACE\n')
    file.write(wing_name+'\n')
    file.write('{:.1f} {:.1f} {:.1f} {:.1f}\n'.format(Nchord, Cspace, Nspan, Sspace))

    # Check symmetry in plane x-z = 2 
    if tigl.wingGetSymmetry(i) == 2:
        file.write('YDUPLICATE \n')
        file.write('0 \n')

    incidence = cpsf.get_value(tixi, model_xpath+ 
                               'wings/wing['+str(i)+']/transformation/rotation/y')

    file.write('ANGLE \n')
    file.write('{:.1f} \n'.format(incidence))

    file.write('SCALE \n')
    file.write('1.0 1.0 1.0 \n')

    translate_x = cpsf.get_value(tixi, model_xpath+ 
                               'wings/wing['+str(i)+']/transformation/translation/x')
    translate_y= cpsf.get_value(tixi, model_xpath+ 
                               'wings/wing['+str(i)+']/transformation/translation/y')
    translate_z = cpsf.get_value(tixi, model_xpath+ 
                               'wings/wing['+str(i)+']/transformation/translation/z')                                                      
    file.write('TRANSLATE \n')
    file.write('{:.5f} {:.5f} {:.5f} \n'.format(translate_x, translate_y, translate_z))

    print('======================================================')
    'TODO - Control surface declaration'
    try:
        print('control surfaces TE:', tixi.getNumberOfChilds(model_xpath+ 'wings/wing['+str(i)+']/componentSegments/componentSegment/controlSurfaces/trailingEdgeDevices/'))
    except:
        print('No TE controls')

    try:    
        print('control surfaces LE:', tixi.getNumberOfChilds(model_xpath+ 'wings/wing['+str(i)+']/componentSegments/componentSegment/controlSurfaces/spoilers/'))
    except:
        print('No LE controls')

    try:
        print('control surfaces Type:', tixi.getNumberOfChilds(model_xpath+ 'wings/wing['+str(i)+']/componentSegments/componentSegment/controlSurfaces/'))
    except:
        print('No controls')
    # n_control_surface_types = tixi.getNumberOfChilds(model_xpath+ 'wings/wing['+str(i)+']/componentSegments/componentSegment/controlSurfaces/')
    # n_LE_control_surfaces = tixi.getNumberOfChilds(model_xpath+ 'wings/wing['+str(i)+']/componentSegments/componentSegment/controlSurfaces/spoilers/')
    # n_TE_control_surfaces = tixi.getNumberOfChilds(model_xpath+ 'wings/wing['+str(i)+']/componentSegments/componentSegment/controlSurfaces/trailingEdgeDevices/')
    print('======================================================')
    vector_section_x = []
    vector_section_y = []
    vector_section_z = []

    # Section level writing
    for j in range(1, n_segments+1):
        file.write('SECTION \n')
        ''' Most examples in cpacs uses positioning to define the position of the wing sections leading edge cooridinates.
        Following the examples, becomes necessary to calculate the x, y and z coordinates from length, sweep and dihedral angles.
        '''
        positioning_length = cpsf.get_value(tixi, model_xpath+
                                           'wings/wing['+str(i)+']/positionings/positioning['+str(j)+']/length')
        positioning_sweep_angle = cpsf.get_value(tixi, model_xpath+
                                           'wings/wing['+str(i)+']/positionings/positioning['+str(j)+']/sweepAngle')  
        positiong_dihedral_angle = cpsf.get_value(tixi, model_xpath+
                                           'wings/wing['+str(i)+']/positionings/positioning['+str(j)+']/dihedralAngle')

        section_z_aux = positioning_length*np.sin(positiong_dihedral_angle*np.pi/180)
        ca_aux = positioning_length*np.cos(positiong_dihedral_angle*np.pi/180)
        section_y_aux = ca_aux*np.cos(positioning_sweep_angle*np.pi/180)
        section_x_aux = section_y_aux*np.tan(positioning_sweep_angle*np.pi/180)

        '''Once positioning is defined CPACS also allows to perform a tranformation of the wing sections taking as reference 
        the positionig cooridinates. This increment on coordinates values must be considered and sum to obtaing the global 
        values for the construction of AVL file.
        '''
        section_x_aux0 = cpsf.get_value(tixi, model_xpath+
                                           'wings/wing['+str(i)+']/sections/section['+str(j)+']/transformation/translation/x')
        section_y_aux0 = cpsf.get_value(tixi, model_xpath+
                                           'wings/wing['+str(i)+']/sections/section['+str(j)+']/transformation/translation/y')   
        section_z_aux0 = cpsf.get_value(tixi, model_xpath+
                                           'wings/wing['+str(i)+']/sections/section['+str(j)+']/transformation/translation/z')

        vector_section_x.append(section_x_aux + section_x_aux0)
        vector_section_y.append(section_y_aux + section_y_aux0)
        vector_section_z.append(section_z_aux + section_z_aux0)

        if j == 1:
            section_x = vector_section_x[j-1]
            section_y = vector_section_y[j-1]
            section_z = vector_section_z[j-1]
        else:
            section_x = sum(vector_section_x)
            section_y = sum(vector_section_y)
            section_z = sum(vector_section_z)
                                    
        incidence_section = cpsf.get_value(tixi, model_xpath+
                                           'wings/wing['+str(i)+']/sections/section['+str(j)+']/transformation/rotation/y')

        chord_section = cpsf.get_value(tixi, model_xpath+
                                     'wings/wing['+str(i)+']/sections/section['+str(j)+']/'+
                                      'elements/element[1]/transformation/scaling/x')

        if tigl.wingGetSymmetry(i) == 2:
            file.write('{:.3f} {:.3f} {:.3f} {:.3f} {:.3f} \n'.format(section_x, section_y, section_z, chord_section, incidence_section))
        else:
            file.write('{:.3f} {:.3f} {:.3f} {:.3f} {:.3f} \n'.format(section_x, section_z, section_y, chord_section, incidence_section))

        airfoil = cpsf.get_value(tixi, model_xpath+
                                'wings/wing['+str(i)+']/sections/section['+str(j)+']/elements/element/airfoilUID')

        file.write('AFILE \n')
        file.write(airfoil+'\n')

file.close()  


def find(substr, infile):
    with open(MODULE_DIR+ '\\'+ infile) as a:
        num_line = []       
        for num, line in enumerate(a, 1):
            if substr in line:               
                num_line = num
    return(num_line)
    
def read(line_num, infile):
    with open(MODULE_DIR+ '\\'+ infile) as lines:
        for line in islice(lines, line_num, line_num+1):
            line_saida = line.split()
            line.split(', ')
        # line_saida = [line.split() for line in islice(lines, line_num, line_num+1)]
    return(line_saida)

# Execute and read avl results
def total_forces():

    wd = os.getcwd()
    os.chdir("/")    
    p = subprocess.Popen('avl.exe < avl_run.run', shell = True, cwd = MODULE_DIR)
    try:
        p.wait(20)
    except subprocess.TimeoutExpired:
        p.kill()        

    search_file = 'st.st'
    CX_line = (find('CXtot', search_file)) - 1
    CL_line = (find('CLtot', search_file)) - 1
    XNP_line = (find('Xnp', search_file)) - 1

    CXtot_line = read(CX_line, search_file)
    CYtot_line = read(CX_line + 1, search_file)
    CZtot_line = read(CX_line + 2, search_file)

    CLtot_line = read(CL_line, search_file)
    CDtot_line = read(CL_line + 1, search_file)
    CDvis_line = read(CL_line + 2, search_file)
    CLff_line = read(CL_line + 3, search_file)
    CYff_line = read(CL_line + 4, search_file)

    Xnp_line = read(XNP_line, search_file)

    CXtot = CXtot_line[2]
    Cltot = CXtot_line[5]
    Cl_dot_tot = CXtot_line[8]
    
    CYtot = CYtot_line[2]
    Cmtot = CYtot_line[5]
    CZtot = CZtot_line[2]
    Cntot = CZtot_line[5]
    Cn_dot_tot = CZtot_line[8]

    CLtot = CLtot_line[2]
    CDtot = CDtot_line[2]
    CDvis = CDvis_line[2]
    CDind = CDvis_line[5]
    CLff  = CLff_line[2]
    CDff  = CLff_line[5]
    CYff  = CYff_line[2]
    e = CYff_line[5]

    NP = Xnp_line[4]

    if os.path.exists('st.st'):
        os.remove('st.st')
    
    return CDtot, CDind

CD = total_forces()

# Dir to write AVL total forces results into cpacs XML output file
xpath_write = '/cpacs/toolspecific/AVL/save_results/total_forces/'
CDtot = float(CD[0])
CDind = float(CD[1])

print('\nCD_tot', CD[0])
print('\nCD_ind', CD[1])

# Open and write cpacs xml output file
tixi_out = cpsf.open_tixi(cpacs_out_path)
tixi_out.updateDoubleElement(xpath_write+'CD_tot', CDtot, '%g')
tixi_out.updateDoubleElement(xpath_write+'CD_ind', CDind, '%g')

# Close cpacs xml output file
tixi_out = cpsf.close_tixi(tixi_out, cpacs_out_path)

log.info('-------- End Run CPACS2AVL --------')
