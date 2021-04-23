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
from framework.Performance.Engine.engine_performance import turbofan
from framework.Noise.Noise_Smith.atmospheric_attenuation import atmospheric_attenuation
import numpy as np
from scipy import interpolate
from framework.utilities.logger import get_logger
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
kt_to_ms = 0.514
m_to_ft= 3.28084
log = get_logger(__file__.split('.')[0])

def noise_engine(noise_parameters,aircraft_geometry,altitude,delta_ISA,theta,fi,R,manete,N1,N2,vairp,vehicle):
    engine = vehicle['engine']


    f = np.array([50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000])
    
    
    vairp = 0.1
    ## CORPO DA FUNÇÃO
    ## Dados da atmosfera ##
    _, _, _, _, _, _, _, a = atmosphere_ISA_deviation(altitude, delta_ISA)   # propriedades da atmosfera
    mach               = vairp/(a* kt_to_ms)                                      # Numero de Mach
    
    ## Dados do motor ##
    thrust_force, fuel_flow_1 , vehicle = turbofan(altitude, mach, manete, vehicle)  # Atenção: N1 e N2
    
    ## Ruído do fan e compressor ##
    ratT                = engine['total_temperatures'][7]/engine['total_temperatures'][2]
    mponto              = engine['fuel_flows'][1]
    nfan                = engine['fan_rotation'] 
    MTRd                = 1.3
    nrotor              = 38
    nstat               = 80
    RSS                 = 200
    IGV                 = 0
    _, ruidoFant      = fan(altitude,delta_ISA,noise_parameters,vairp,theta,fi,R,engine['diameter'],ratT,mponto,nfan,MTRd,nrotor,nstat,RSS,IGV)
    
    
    ## Ruido da câmara de combustão ##
    mdot                = engine['fuel_flows'][0]
    T3K                 = engine['total_temperatures'][3]
    T4K                 = engine['total_temperatures'][4]
    P3                  = engine['total_pressures'][3]
    RH                  = 70
    _, ruidocamarat  = combustion_chamber(altitude,delta_ISA,noise_parameters,vairp,theta,fi,R,mdot,T3K,T4K,P3)
    
    
    ## Ruido da turbina ##
    Tturbsaida           = engine['total_temperatures'][4]
    nturb                = engine['fan_rotation'] 
    MTRturb              = 0.50
    nrotor               = 76
    RSSturb              = 50
    _, ruidoTurbinat  = turbine(altitude,delta_ISA,noise_parameters,vairp,theta,fi,R,mdot,nturb,Tturbsaida,MTRturb,nrotor,RSSturb)
    
    
    ## Ruido de Jato ##
    ACJ                 = engine['exit_areas'][1]
    ABJ                 = engine['exit_areas'][2]
    h                   = 0.150
    DCJ                 = 2*ACJ/(np.pi*h)+h/2
    VCJ                 = engine['gas_exit_speeds'][0]
    VBJ                 = engine['gas_exit_speeds'][1]
    TCJ                 = engine['total_temperatures'][6]
    TBJ                 = engine['total_temperatures'][7]
    roCJ                = 0.561
    roBJ                = 1.210
    plug                = 1.0
    coaxial             = 1.0


    # (altitude,delta_ISA,noise_parameters,vairp,theta,fi,R,plug,coaxial,ACJ,ABJ,h,DCJ,VCJ,VBJ,TCJ,TBJ,roCJ,roBJ)

    # try:
        # if VCJ >= 0:
    _, ruidoJatot     = nozzle(altitude,delta_ISA,noise_parameters,vairp,theta,fi,R,plug,coaxial,ACJ,ABJ,h,DCJ,VCJ,VBJ,TCJ,TBJ,roCJ,roBJ)
        # else:
            # raise ValueError('VCJ is 0.')
    # except (ValueError, IndexError):
    #     log.error(">>>>>>>>>> Error at <<<<<<<<<<<< noise_engine", exc_info = True)
    
    
    ## Ruido total ##
    ruidoTotal          = 10*np.log10(10**(0.1*ruidoFant)+10**(0.1*ruidocamarat)+10**(0.1*ruidoTurbinat)+10**(0.1*ruidoJatot))
    
    
    ## DADOS DE SAIDA ##
    OASPLENG            = ruidoTotal
    ft                  = f.T
    
    return ft, OASPLENG

def fan(altitude,delta_ISA,noise_parameters,vairp,theta,fi,R,engine_diameter,ratT,mponto,nfan,MTRd,nrotor,nstat,RSS,IGV):
    

    RH = noise_parameters['relative_humidity']
    
    ## Variáveis globais
    #global f
    f = np.array([50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000])

    ## Tabelas para interpolação
    f1                  = np.array([44.7, 56.2, 70.7, 89.1, 112, 141, 178, 224, 282, 355, 447, 562, 708, 891, 1122, 1413, 1778, 2239, 2818, 3548, 4467, 5623, 7079, 8913])
    f2                  = np.array([56.2, 70.7, 89.1, 112, 141, 178, 224, 282, 355, 447, 562, 708, 891, 1122, 1413, 1778, 2239, 2818, 3548, 4467, 5623, 7079, 8913, 11220])
    F2cb                = np.array([-9.5, -8.5, -7, -5, -2, 0, 0, -3.5, -7.5, -9, -9.5, -10, -10.5, -11, -11.5, -12, -12.5, -13, -13.5])
    tetacb              = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180])
    F3blent             = np.array([-2, -1, 0, 0, 0, -2, -4.5, -7.5, -11, -15, -19, -25, -31, -37, -43, -49, -55, -61, -67])
    tetablent           = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180])
    F3dsent             = np.array([-3.00, -1.50, 0.000, 0.000, 0.000, -1.20, -3.50, -6.80, -10.5, -14.5, -19.0, -23.5, -28.0, -32.5, -37.0, -41.5, -46.0, -50.5, -55.0])
    tetadsent           = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180])
 
    F3bldesc            = np.array([-15.8, -11.5, -8, -5, -2.7, -1.2, -0.3, 0, -2, -6, -10, -15, -20])
    tetabldesc          = np.array([60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180])
 
    tetadsdesc          = np.array([60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180])
    F3dsdesc            = np.array([-15, -11, -8, -5, -3, -1, 0, 0, -2, -5.5, -9, -13, -18])


    ## CORPO DA FUNÇÃO ##
    ## Manipulação de dados de entrada ##
    v0                  = vairp                                                # Velocidade da aeronave [m/s]
    radialdistance      = R                                                    # distância para avaliação do ruído [m]

    ## Dados da atmosfera ##
    _, _, _, T, _, _, _, a = atmosphere_ISA_deviation(altitude, 0)                             # propriedades da atmosfera
                                        # velocidade do som [m/s]


    ## Cálculos iniciais ##
    M0                  = v0/(a*kt_to_ms)                                              # número de Mach da aeronave
    MTR                 = np.sqrt(M0**2+(nfan*np.pi/30*engine_diameter/2/(a*kt_to_ms))**2)
    delta               = np.abs(MTR/(1-nstat/nrotor))


    ## Cálculo do SPL global: ##
    deltaT              = ratT*T-T
    mponto0             = 0.453
    deltaT0             = 0.555
    # deltaT0             = 288.15
    SPL                 = 20*np.log10(deltaT/deltaT0)+10*np.log10(mponto/mponto0)


    ## Ruido de entrada do FAN ##
    ## Ruído banda larga ##
    fb                  = nfan*nrotor/60                                       # frequencia fundamental de passagem das pás
    if MTRd<=1.0 and MTR<=0.9:
        F1bent          = 58.5
    elif MTRd> 1.0 and MTR<=0.9:
        F1bent          = 58.5+20*np.log10(MTRd)
    elif MTRd> 1.0 and MTR>0.9:
        F1bent          = 58.5+20*np.log10(MTRd)-20*np.log10(MTR/0.9)
    else:
        F1bent          = 58.5-20*np.log10(MTR/0.9)

    if RSS<=100:
        F2bent          = -5*np.log10(RSS/300)
    else:
        F2bent          = -5*np.log10(100/300)

    F3bent              =     interpolate.interp1d(tetablent,F3blent,fill_value='extrapolate')(theta)

    F4bent              = 10*np.log10(np.exp(-0.5*(np.log(f/(2.5*fb))/np.log(2.2))**2))  
    Lcbent              = SPL+F1bent+F2bent+F3bent+3*(IGV==1)
    SPLbent             = Lcbent+F4bent-10
    ## Ruído discreto ##
    # Correção 01
    if MTRd<=1.0 and MTR<=0.72:
        F1dent          = 60.5
    elif MTRd>1.0 and MTR<=0.72:
        F1dent          = 60.5+20*np.log10(MTRd)
    elif MTRd>1.0 and MTR>0.72:
        F1dent          = min((59.5+80*np.log10(MTRd/MTR)),(60.5+20*np.log10(MTRd)+50*np.log10(MTR/0.72)))
    else:
        F1dent          = 60.5+20*np.log10(MTRd)+50*np.log10(MTR/0.72)

    
    # Correção 02
    if RSS<=100:
        F2dent          = -10*np.log10(RSS/300)
    else:
        F2dent          = -10*np.log10(100/300)

    # Correção 03
    F3dent              = interpolate.interp1d(tetadsent,F3dsent,fill_value='extrapolate')(theta)

    Lcdent              = SPL+F1dent+F2dent+F3dent
    # Correção 04
    k                   = achatom(np.fix(f/fb))
    if  IGV==1:
        F4dent          = (-3-3*k)*(delta>1.05 and k>1)-8*(delta<=1.05 and k==1)+(-3-3*k)*(delta<=1.05 and k>1) 
                                                                                # para k=1 e delta>1.05, não há valor, e a np.expressao retorna 0
    else:
        F4dent          = (3-3*k)*(delta>1.05)-8*(delta<=1.05 and k==1)+(3-3*k)*(delta<=1.05 and k>1)

    # Valor final
    SPLdent             = (k!=0)*(Lcdent+10*np.log10(10**(0.1*F4dent))-10)

    ## Ruído combinação, só para MTR supersônico ##
    if  MTR>1:
        F1c1_2          = (318.49*MTR-288.49)*(MTR<=1.146)+(-14.052*MTR+92.603)*(MTR>1.146)
        F1c1_4          = (147.52*MTR-117.52)*(MTR<=1.322)+(-13.274*MTR+95.049)*(MTR>1.322)
        F1c1_8          = (67.541*MTR-37.541)*(MTR<=1.61)+(-12.051*MTR+90.603)*(MTR>1.61)
        F2c             = interpolate.interp1d(tetacb,F2cb,fill_value='extrapolate')(theta)
        F3c1_2          = (30*np.log10(2*f/fb))*(f/fb<=0.5)+(-30*np.log10(2*f/fb))*(f/fb>0.5)
        F3c1_4          = (50*np.log10(4*f/fb))*(f/fb<=0.25)+(-50*np.log10(4*f/fb))*(f/fb>0.25)
        F3c1_8          = (50*np.log10(8*f/fb))*(f/fb<=0.125)+(-30*np.log10(8*f/fb))*(f/fb>0.125)
        Lcc1_2          = SPL+F1c1_2+F2c+F3c1_2-5*(IGV==1)
        Lcc1_4          = SPL+F1c1_4+F2c+F3c1_4-5*(IGV==1)
        Lcc1_8          = SPL+F1c1_8+F2c+F3c1_8-5*(IGV==1)
        SPLc            = 10*np.log10(10**(0.1*Lcc1_2)+10**(0.1*Lcc1_4)+10**(0.1*Lcc1_8))-17      # soma dos 3 espectros de frequencia
    else:
        SPLc      = np.zeros(24)

    ## Ruído da descarga do FAN ##
    ## Ruído banda larga ##
    # Correção 01
    if MTRd<=1.0 and MTR<=1.0:
        F1bdesc         = 60.0
    elif MTRd> 1.0 and MTR<=1.0:
        F1bdesc         = 60.0+20*np.log10(MTRd)
    elif MTRd> 1.0 and MTR>1.0:
        F1bdesc         = 60.0+20*np.log10(MTRd)-20*np.log10(MTR)
    else:
        F1bdesc         = 60.0-20*np.log10(MTR)

    # Correção 02
    F2bdesc             = F2bent                                               #F2b é o mesmo do ruído da entrada no FAN.
    # Correção 03
    F3bdesc             = interpolate.interp1d(tetabldesc,F3bldesc,fill_value='extrapolate')(theta)
    # Correção 04
    F4bdesc             = F4bent
    # VAlor final
    Lcbdesc             = SPL+F1bdesc+F2bdesc+F3bdesc+3*(IGV==1)
    SPLbdesc            = Lcbdesc+F4bdesc-2
    ## Ruído discreto ##
    # Correção 01
    if MTRd<=1.0 and MTR<=1.0:
        F1ddesc         = 63.0
    elif MTRd> 1.0 and MTR<=1.0:
        F1ddesc         = 63.0+20*np.log10(MTRd)
    elif MTRd> 1.0 and MTR>1.0:
        F1ddesc         = 63.0+20*np.log10(MTRd)-20*np.log10(MTR)
    else:
        F1ddesc         = 63.0-20*np.log10(MTR)

    # Correção 02
    F2ddesc             = F2dent                                               # F2d é o mesmo do ruído da entrada do FAN
    # Correção 03
    F3ddesc             = interpolate.interp1d(tetadsdesc,F3dsdesc,fill_value='extrapolate')(theta)
    # Correção 04
    F4ddesc             = F4dent
    # Valor final
    Lcddesc             = SPL+F1ddesc+F2ddesc+F3ddesc+6*(IGV==1)
    # SPLddesc            = Lcddesc+F4ddesc-2

    SPLddesc = []
    for ij in range(0,24):
        if k[ij]==0:
            SPLddesc.append(0)
        else:
            aux1 = Lcddesc+10*np.log10(10**(0.1*F4ddesc[ij]))-2
            SPLddesc.append(float(aux1))
    
    SPLddesc = np.asarray(SPLddesc)
    ## amortecimento atmosférico ##
    ft, alfaamortt, amorttott, amortatm, SPLrt = atmospheric_attenuation(T,noise_parameters,radialdistance,f)

    ## Efeito doppler ##
    deltaLdoppler       = -40*np.log10(1-M0*np.cos(theta*np.pi/180))

    ## soma dos ruídos banda larga de entrada e descarga do FAN ##
    SPLb                = 10*np.log10(10**(0.1*SPLbent)+10**(0.1*SPLbdesc))       # método direto de soma
    ## soma dos ruídos discretos de entrada e descarga do FAN ##
    SPLd                = 10*np.log10(10**(0.1*SPLdent)+10**(0.1*SPLddesc))       # método direto de soma


    ## soma dos ruidos discreto, banda larga e combinação ##
    SPLFan              = 10*np.log10(10**(0.1*SPLb)+10**(0.1*SPLc)+10**(0.1*SPLd)) 
                                                                                # método direto de soma, considerando o amortecimento atmosférico
                                                                                

    ## DADOS DE SAIDA ##
    ruidoFan            = SPLFan-amorttott
    ft                  = f.T
    ruidoFant           = ruidoFan.T
    a1                  = len(ruidoFant)
    for ia1 in range(a1):
        if ruidoFant[ia1]<1:
            ruidoFant[ia1] = 1
    return ft, ruidoFant



def achatom(k):
    kprocess = np.zeros(24)

    for ik in range(2,24):
        if k[ik]==k[ik-1]:
            kprocess[ik] = 0
        else:
            kprocess[ik] = k[ik]

    return kprocess


def combustion_chamber(altitude,delta_ISA,noise_parameters,vairp,theta,fi,R,mdot,T3K,T4K,P3):
    RH = noise_parameters['relative_humidity']


    f = np.array([50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000])

    ## Fatores de conversão
    #global m_to_ft deg_to_rad

    deg_to_rad = np.pi/180

    ## Tabelas para interpolação
    tetatab             = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180]
    OASPLPWLtab         = [-32.4, -30.8, -29.6, -28.0, -26.6, -25.0, -24.0, -23.4, -22.3, -20.8, -19.6, -18.8, -18.6, -18.5, -18.7, -19.0, -19.0, -19.1, -19.2]


    ## CORPO DA FUNÇÃO ##
    ## Manipulação de dados de entrada ##
    v0                  = vairp                                                # velocidade da aeronave [m/s]
    radialdistance      = R                                                    # distância para avaliação do ruído [m]

    ## Dados da atmosfera ##
    _, _, _, T, P, _, _, a = atmosphere_ISA_deviation(altitude, delta_ISA) # propriedades da atmosfera

    ## Cálculos iniciais ##
    M0                  = v0/(a*kt_to_ms)                                              # número de Mach da aeronave

    ## Ruido da câmara de combustão ##
    epsilon             = fi
    OAPWL               = 56.5+10*np.log10((mdot/0.4536)*((T4K-T3K)*(P3/P)*(T/T3K))) #colocar temperatura total THIS LINE HAVE WRONG UNITS AT MATLABCDE P3[Pa] and P[KPa]
    OASPLPWL            = interpolate.interp1d(tetatab,OASPLPWLtab,fill_value='extrapolate')(theta)
    OASPLtr             = OAPWL+OASPLPWL-20*np.log10(radialdistance)              # SPLr está incluído
    fp                  = 740*np.sqrt((0.4536/mdot)*(P3/101325)*np.sqrt(288.15/T4K))
    # if (fp<300) or (fp>1000):
    if np.logical_or(fp<300,fp>1000):
        fp=400
    if np.all(f<=fp):
        SPLf            = 15.02*(np.log10(f/fp))**6+65.92*(np.log10(f/fp))**5+108.33*(np.log10(f/fp))**4+75.37*(np.log10(f/fp))**3+2.96*(np.log10(f/fp))**2+1.48*np.log10(f/fp)-10
    else:
        SPLf            = 0.20*(np.log10(f/fp))**6-1.02*(np.log10(f/fp))**5+1.21*(np.log10(f/fp))**4+2.72*(np.log10(f/fp))**3-11.54*(np.log10(f/fp))**2-1.30*np.log10(f/fp)-10

    SPLftr              = SPLf+OASPLtr


    ## Amortecimento atmosférico ##
    ft, alfaamortt, amorttott, amortatm, SPLrt = atmospheric_attenuation(T,noise_parameters,radialdistance,f)

    ## Efeito doppler ##
    deltaLdoppler       = -40*np.log10(1-M0*np.cos(epsilon*deg_to_rad))


    ## DADOS DE SAIDA ##
    Ruidocamara         = SPLftr-amortatm.T+deltaLdoppler
    ft                  = f.T
    ruidocamarat        = Ruidocamara.T
    a1                  = len(ruidocamarat)
    for ia1 in range(a1):
        if ruidocamarat[ia1]<1:
            ruidocamarat[ia1] = 1

    return ft, ruidocamarat


def turbine(altitude,delta_ISA,noise_parameters,vairp,theta,fi,R,mdot,nturb,Tturbsaida,MTRturb,nrotor,RSSturb):

    RH = noise_parameters['relative_humidity']
    f = np.array([50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000])

    ## Fatores de conversão
    #global m_to_ft deg2rad

    deg2rad = np.pi/180

    ## Tabelas para interpolação
    tetatab             =  np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180.1])
    F1tab               =  np.array([-37.0, -33.0, -29.0, -25.0, -21.0, -17.0, -13.0, -10.0, -07.0, -04.0, -1.25, 00.00, -01.4, -05.0, -09.0, -14.0, -19.0, -24.0, -29.0])
    F3tab               =  np.array([-48.2, -42.9, -37.6, -32.3, -27.0, -21.7, -18.0, -14.0, -10.0, -05.5, -02.3, 00.00, -02.1, -08.0, -14.0, -20.0, -26.0, -32.0, -38.0])


    ## CORPO DA FUNÇÃO ##
    ## Manipulação de dados de entrada ##
    v0                  = vairp                                                # velocidade da aeronave [m/s]
    epsilon             = fi
    radialdistance      = R                                                    # distância para avaliação do ruído [m]

    ## Dados da atmosfera ##
    _, _, _, T, P, _, _, a = atmosphere_ISA_deviation(altitude, 0) # propriedades da atmosfera                          # propriedades da atmosfera
    # T                   = atm(1)                                               # temperatura ambiente [K]
    # (a*kt_to_ms)                = atm(7)                                               # velocidade do som [m/s]


    ## Cálculos iniciais ##
    M0                  = v0/(a*kt_to_ms)                                              # número de Mach da aeronave

    ## Ruido da turbina ##
    F1                  = interpolate.interp1d(tetatab,F1tab,fill_value='extrapolate')(theta)
    F3                  = interpolate.interp1d(tetatab,F3tab,fill_value='extrapolate')(theta)

    ## Ruido banda larga ##
    termo1              = ((MTRturb*(a*kt_to_ms)/0.305)*(340.3/(a*kt_to_ms)))**3
    termo2              = (mdot/0.4536)
    termo3              = (1-M0*np.cos(epsilon*deg2rad))
    SPLpeak             = 10*np.log10(termo1*termo2*termo3**-4)+F1-10
    f0                  = nrotor*nturb/60/termo3
    if f0>10000:
        f0 = 10000

    Fb                  = 10*np.log10(f/f0)*(f<f0)-20*np.log10(f/f0)*(f>=f0)
    SPLbl               = SPLpeak+Fb


    ## Ruido discreto ##
    termo1              = (MTRturb*(a*kt_to_ms)/0.305)**0.6*(340.3/(a*kt_to_ms))**3
    termo2              = (mdot/0.4536)
    termo3              = (RSSturb/100)
    termo4              = (1-M0*np.cos(epsilon*deg2rad))
    #
    SPLtone             = 10*np.log10(termo1*termo2*termo3*termo4**-4)+F3+56
    #
    f1                  = f/2**(1/6)
    f2                  = f*2**(1/6)
    # k                   = 1:10000/f0   # REVIEWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
    k  = 1
    SPLdisc             = SPLtone-10*(k-1)
    #
    ## Colocação dos tons ##
    # ftom = zeros(size(f))
    
    # for j in range(1,(10000/f0)):
    #     ftom[:,j]       = f*((j*f0)>f1 and (j*f0)<f2)                           # acha as frequencias em que deve ser colocado o tom, em formato de j colunas
    ftom = np.zeros(24)
    for j in range(len(ftom)):
        # if np.any((j*f0)>f1) and np.all((j*f0)<f2):

        if (1*f0)>f1[j] and (1*f0)<f2[j]:
            ftom[j]       = f[j]*1
        else:
            ftom[j]       = 0

        

    

    # ftom[:,j]       = f*((j*f0)>f1 and (j*f0)<f2)  
    # ftons               = np.sum(ftom, axis = 1)                                        # acha as frequencias em formato de uma coluna
    ftons               = ftom.T                                               # transpoe a matriz e obtem um vetor 1x24
    SPLd                = np.zeros(24)
    i                   = np.nonzero(ftons)                                          # retorna as posições dos valores de ftons que não são zeros
    I1                  = max(np.shape(i))                                         # avalia a quantidade de frequências nas quais devem ser colocados os tons
    I2                  = max(np.shape(SPLdisc))                                   # avalia a quantidade de tons
    I3                  = I1/I2                                                # verifica se é um múltiplo inteiro
    I4                  = np.floor(I1/I2)                                         # verifica se é um múltiplo inteiro
    if I1>I2:                                                                    # verifica se há mais frequências que tons
        if (I3-I4)==0:                                                           # verifica se é um múltiplo inteiro
            for ai2 in range(I2):
                for ai1 in range(I3):
                    SPLdisca[I2*(ai2-1)+ai1] = SPLdisc[ai2]                    # redimensiona a matriz de tons
        SPLdisc         = SPLdisca                                             # redimensiona a matriz de tons


    SPLd[i]             = SPLd[i]+SPLdisc                                      # coloca os tons


    ## Soma dos ruidos discreto e banda larga ##
    SPLturb             = 10*np.log10(10**(0.1*SPLbl)+10**(0.1*SPLd))

    ## Amortecimento atmosférico ##
    ft, alfaamortt, amorttott, amortatm, SPLrt = atmospheric_attenuation(T,noise_parameters,radialdistance,f)
    ## Extrapolando o espectro para um metro ##
    deltaLamort1m       = alfaamortt.T*45.72/100                                 # para transformar em um metro
    amortatm1m          = interpolate.interp1d(f,deltaLamort1m,fill_value='extrapolate')(f)
    ruido1m             = SPLturb+33.2+amortatm1m                              # 33.2=20*np.log10(45.72)


    ## DADOS DE SAIDA ##
    ruidoTurbina        = ruido1m-amortatm.T-SPLrt.T
    ft                  = f.T
    ruidoTurbinat       = ruidoTurbina.T
    a1                  = len(ruidoTurbinat)
    for ia1 in range(a1):
        if ruidoTurbinat[ia1]<1:
            ruidoTurbinat[ia1] = 1
    return ft, ruidoTurbinat


def nozzle(altitude,delta_ISA,noise_parameters,vairp,theta,fi,R,plug,coaxial,ACJ,ABJ,h,DCJ,VCJ,VBJ,TCJ,TBJ,roCJ,roBJ):

    RH = noise_parameters['relative_humidity']
    f = np.array([50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000])


    ## Fatores de conversão
    #global m_to_ft deg_to_rad
    deg_to_rad = np.pi/180


    ## Tabelas para interpolação
    ARPtab              = np.array([0, .05, .1, .15, .2, .25, .3, .35, .4, .45, .5, .55, .6, .65, .7, .75, .8, .85, .9, .95, 1, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.55, 1.6, 1.65, 1.7])
    VRtab               = np.array([0.2, 0.4, 0.6, 0.8, 1])
    FSPtab              = np.array([ 0.0, 4.0, 7.0, 11.0, 14.0, 16.0, 19.0, 21.0, 24.0, 25.0, 27.0, 28.0, 28.0, 29.0, 29.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0, 30.0,
    0.0, 5.0, 9.0, 13.0, 17.0, 21.0, 25.0, 28.0, 31.0, 35.0, 38.0, 41.0, 43.0, 46.0, 48.0, 51.0, 53.0, 55.0, 57.0, 59.0, 61.0, 63.0, 65.0, 66.0, 68.0, 69.0, 71.0, 72.0, 73.0, 74.0, 76.0, 77.0, 78.0, 79.0, 80.0,
    0.0, 6.0, 12.0, 18.0, 23.0, 28.0, 33.0, 37.0, 41.0, 45.0, 48.0, 51.0, 53.0, 56.0, 59.0, 61.0, 64.0, 65.0, 67.0, 69.0, 71.0, 73.0, 74.0, 75.0, 77.0, 78.0, 79.0, 81.0, 82.0, 83.0, 84.0, 85.0, 86.0, 87.0, 88.0,
    0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 29.0, 33.0, 37.0, 40.0, 43.0, 46.0, 48.0, 52.0, 54.0, 56.0, 59.0, 61.0, 63.0, 64.0, 65.0, 68.0, 69.0, 70.0, 72.0, 73.0, 74.0, 75.0, 76.0, 77.0, 78.0, 80.0, 81.0, 82.0, 82.5,
    0.0, 4.0, 8.0, 12.0, 16.0, 20.0, 23.0, 26.0, 30.0, 32.0, 35.0, 38.0, 41.0, 43.0, 45.0, 48.0, 50.0, 52.0, 54.0, 56.0, 58.0, 60.0, 61.0, 63.0, 65.0, 66.0, 67.0, 69.0, 70.0, 71.0, 73.0, 74.0, 75.0, 76.0, 77.0]).T/100
    logStab             = np.array([-1.7, -1.6, -1.5, -1.4, -1.3, -1.2, -1.1, -1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9])
    tetatab             = np.array([109.9, 120, 130, 140, 150, 160, 170, 180.1])
    SDLtab              = -np.array([39.1, 36.8, 34.5, 32.3, 30.0, 27.7, 25.4, 23.2, 21.1, 19.1, 17.4, 15.9, 14.7, 13.7, 12.8, 12.1, 11.6, 11.3, 11.1, 11.2, 11.3, 11.7, 12.3, 13.0, 13.7, 14.6, 15.6, 16.7, 17.8, 18.9, 20.1, 21.3, 22.4, 23.6, 24.8, 26.0, 27.2,
    42.4, 40.0, 37.6, 35.2, 32.8, 30.4, 28.0, 25.6, 23.2, 20.8, 18.5, 16.2, 14.1, 12.2, 10.9, 10.2, 09.9, 10.2, 10.6, 11.1, 11.8, 12.7, 13.7, 14.7, 15.8, 16.9, 18.0, 19.2, 20.4, 21.6, 22.8, 24.0, 25.2, 26.4, 27.6, 28.8, 30.0,
    43.0, 40.2, 37.4, 34.6, 31.8, 29.0, 26.2, 23.4, 20.6, 17.8, 15.2, 13.1, 11.5, 10.2, 09.6, 09.3, 09.6, 10.2, 11.4, 12.7, 14.0, 15.3, 16.6, 18.0, 19.3, 20.7, 22.0, 23.4, 24.7, 26.1, 27.5, 28.8, 30.2, 31.5, 32.8, 34.1, 35.5,
    44.5, 41.3, 38.2, 35.0, 31.8, 28.7, 25.5, 22.4, 19.3, 16.1, 13.2, 11.3, 10.0, 09.4, 09.1, 09.4, 09.9, 10.9, 12.4, 14.0, 15.6, 17.2, 18.8, 20.4, 22.1, 23.7, 25.3, 26.9, 28.5, 30.1, 31.7, 33.3, 34.9, 36.5, 38.1, 39.7, 41.3,
    42.4, 39.3, 36.2, 33.1, 29.9, 26.9, 23.6, 20.5, 17.5, 14.7, 12.1, 09.9, 08.3, 07.7, 08.3, 09.7, 11.6, 13.4, 15.2, 17.0, 18.8, 20.6, 22.3, 24.1, 25.9, 27.7, 29.5, 31.3, 33.1, 34.9, 36.7, 38.5, 40.3, 42.0, 43.8, 45.6, 47.4,
    36.4, 31.9, 27.9, 24.3, 21.1, 18.3, 15.9, 13.8, 12.1, 10.8, 09.9, 09.2, 08.7, 09.2, 10.2, 12.0, 13.9, 15.8, 17.7, 19.6, 21.5, 23.4, 25.3, 27.2, 29.1, 31.0, 32.9, 34.8, 36.7, 38.6, 40.5, 42.4, 44.3, 46.2, 48.1, 50.0, 51.9,
    32.8, 28.7, 25.0, 21.7, 18.8, 16.3, 14.1, 12.3, 10.9, 09.8, 09.0, 08.5, 09.0, 10.0, 11.8, 13.8, 15.8, 17.8, 19.8, 21.8, 23.8, 25.8, 27.8, 29.8, 31.8, 33.8, 35.8, 37.8, 39.8, 41.8, 43.8, 45.8, 47.8, 49.8, 51.8, 53.8, 55.8,
    29.4, 25.6, 22.2, 19.2, 16.6, 14.3, 12.4, 10.9, 09.7, 08.9, 08.4, 08.9, 09.9, 11.8, 13.9, 16.0, 18.1, 20.2, 22.3, 24.4, 26.5, 28.6, 30.7, 32.8, 34.9, 37.0, 39.1, 41.2, 43.3, 45.4, 47.5, 49.6, 51.7, 53.8, 55.9, 58.0, 60.1]).T

                        
    ## CORPO DA FUNÇÃO ##
    ## Manipulação de dados de entrada ##
    Acorejet            = ACJ                                                  # área do jato central [m²]
    Abypassjet          = ABJ                                                  # area do jato perfiférico [m²]
    hgap                = h                                                    # diferença entre os diâmetros do jato central e do plug [m]
    D                   = DCJ                                                  # diâmetro dojato central [m]
    De                  = 2*np.sqrt(D*hgap-hgap**2)                                # diâmetro equivalente [m]
    v0                  = vairp                                                # velocidade da aeronave [m/s]
    radialdistance      = R                                                    # distância para avaliação do ruído [m]


    ## Dados da atmosfera ##
    _, _, _, T, P, rho, _, a = atmosphere_ISA_deviation(altitude, 0) 


    ## Cálculos iniciais ##
    M0                  = v0/(a*kt_to_ms)                                              # número de Mach da aeronave
    tetalinha           = theta*(VCJ/(a*kt_to_ms))**0.1                                  # ângulo efetivo para cálculo do ruído
    w                   = 3*(VCJ/(a*kt_to_ms))**3.5/(0.60+(VCJ/(a*kt_to_ms))**3.5)-1             # expoente de correção do ruído devido à densidade do jato de escape
    vrel                = (VCJ/(a*kt_to_ms))*(1-v0/VCJ)**0.75                           # velocidade relativa do escoamento
    Mc                  = 0.62*(VCJ-v0)/(a*kt_to_ms)                                   # razão entre a velocidade relativa do jato ao avião e a velocidade do som

    ## Ruido para jato circular ##
    OASPLcirc           = 10*np.log10(Acorejet/radialdistance**2*(rho/1.225)**2*((a*kt_to_ms)/340)**4)+10*(3*vrel**3.5/(0.6+vrel**3.5)-1)*np.log10(roCJ/rho)+141+10*np.log10(vrel**7.5/(1+0.01*vrel**4.5))

    ## Ruido para jato plugue ##
    termo1              = 10*np.log10((Acorejet/radialdistance**2)*(rho/1.225)**2*((a*kt_to_ms)/340.3)**4)
    termo2              = 10*(3*vrel**3.5/(0.6+vrel**3.5)-1)*np.log10(roCJ/rho)
    termo3              = 141
    termo4              = 3*np.log10(0.1+2*hgap/D)
    termo5              = 10*np.log10(vrel**7.5/(1+0.01*vrel**4.5))
    OASPLplug           = termo1+termo2+termo3+termo4+termo5

    ## Ruido para jato coaxial, plugue ou circular ##
    if (Abypassjet/Acorejet)<29.7:
        m               = 1.1*np.sqrt(Abypassjet/Acorejet)
    else:
        m               = 6.0

    termo1              = 5*np.log10((TCJ)/(TBJ))
    termo2              = (1-VBJ/VCJ)**m
    termo3              = 1.2*(1+(Abypassjet*VBJ**2)/(Acorejet*VCJ**2))**4
    termo4              = (1+(Abypassjet/Acorejet))**3
    deltaOASPLcoaxial   = termo1+10*np.log10(termo2+termo3/termo4)
    OASPL90plug         = OASPLplug+deltaOASPLcoaxial
    OASPL90circ         = OASPLcirc+deltaOASPLcoaxial

    ARP                 = np.log10(1+Abypassjet/Acorejet)                         # Area ratio parameter
    vratio              = VBJ/VCJ
    minvratio           = min(VRtab)
    if vratio<minvratio:
        VBJ      = minvratio*VCJ

    FSP_f = interpolate.interp2d(VRtab,ARPtab,FSPtab, kind='cubic')

    FSP = FSP_f(VBJ/VCJ,ARP)

    ## Correção espectral
    S_S1                = 1/(1-FSP*((TBJ)/(TCJ)))
    termo1              = S_S1
    termo2              = De/VCJ
    termo3              = (2*hgap/De)**0.4
    termo4              = ((TCJ)/T)**(0.4*(1+np.cos(tetalinha*np.pi/180)))
    S_f                 = termo1*termo2*termo3*termo4
    logS                = np.log10(S_f*f)

    ## Espectro de frequências ##
    cdf                 = 30*np.log10(1+Mc*(1+Mc**5)**0.2)*np.cos(theta*deg_to_rad)        # ordenada do gráfico do espectro #
    if tetalinha<110:
        tetalinha       = 110

    if tetalinha>180:
        tetalinha       = 180

    tetainterp          = tetalinha
    # logS
    ai1                 = len(logS)
    for iai1 in range(ai1):
        if logS[iai1] < min(logStab):
            logS[iai1] = min(logStab)

        if logS[iai1] > max(logStab):
            logS[iai1] = max(logStab)


    # cálculos
    aux0                = np.size(logS)
    aux1                = np.isfinite(logS).astype(int)
    aux2                = np.sum(np.isfinite(aux0).astype(int))
    aux3                = np.sum(aux1)
    if aux3==aux0 and aux2==1:
        SDL_f = interpolate.interp2d(tetatab,logStab,SDLtab, kind='cubic')
        SDL = SDL_f(tetainterp,logS.T)
    else:
        SDL             = ones(len(logStab))


    SPLcoaxial          = OASPL90plug*(plug==1)+OASPL90circ*(plug==0)+SDL-cdf 
    SPLplug             = OASPL90plug+SDL-cdf
    SPLcirc             = OASPL90circ+SDL-cdf
    if plug==0:
        SPLJet          = SPLcirc.T
    else:
        if coaxial ==0:
            SPLJet      = SPLplug.T
        else:
            SPLJet      = SPLcoaxial.T


    ## Atenuação do ruído na atmosfera ##
    ft, alfaamortt, amorttott, deltaLamort, SPLrt = atmospheric_attenuation(T,noise_parameters,radialdistance,f)


    ## DADOS DE SAIDA ##
    ruidoJato           = SPLJet-deltaLamort.T
    ft                  = f.T
    ruidoJatot          = ruidoJato.T

    a1                  = len(ruidoJatot)
    for ia1 in range(a1):
        if ruidoJatot[ia1]<1:
            ruidoJatot[ia1] = 1


    ruidoJatot = ruidoJatot.reshape(-1)
            
    return ft, ruidoJatot
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================
