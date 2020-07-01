# functions to correct rowing speed for weather
from numpy import cos, sin, arccos, sqrt, deg2rad, rad2deg, exp, log, log10
from scipy.optimize import root_scalar

# TODO: consider switching to python decimals

def rowpower(v, water_temp = 18.0, air_temp = 18.0, air_pressure = 1012.0, air_humidity = 0.25, water_flow = 0.0, wind_v = 0.0, wind_angle = 0, cd_air = 0.9, A_air = 2, A_water = 9.0, boat_length = 18.0):    
    ### Comment on inputs and their units ###
    # water_temp is degrees c
    # air_temp is degrees c
    # air_pressure is hPa
    # air_humidity is a percentage from 0 to 1
    # v ie boat speed is m/s
    # water_flow is m/s - positive == head-current, negative == tail-current
    # wind_v ie wind speed is m/s
    # wind_angle is in radians (so convert from degrees on input if needed). 0 degrees = headwind, 180 degrees = tailwind
    # A_air is surface area affected by air resistance and winds in m^2
    # A_water is the wetted surface area of a boat in m^2
    # cd_air is the coefficient of air drag
    # boat_length is in metres
    
    if v + water_flow <= 0:
        raise ValueError("Speed must be greater than the tail current - we don't model backing down")
   
    ### Calculations ###
    # formula from https://www.omnicalculator.com/physics/air-density
    sgc_air = 287.058 # specific gas constant for air, J/kg*K
    sgc_wv = 461.495 # specific gas constant for water vapour, J/kg*K
    wv_pressure = air_humidity * (6.1078 * 10**(7.5*air_temp / (air_temp + 237.3)))
    air_density = (((air_pressure - wv_pressure) / (sgc_air * (air_temp+273.15))) + (wv_pressure / (sgc_wv * (air_temp+273.15))))*100
    
    # formula from https://nvlpubs.nist.gov/nistpubs/jres/097/jresv97n3p335_A1b.pdf
    water_density = 999.84847 + 6.337563*10**-2*water_temp - 8.523829*10**-3*water_temp**2 + 6.943248*10**-5*water_temp**3 - 3.821216*10**-7*water_temp**4

    # kv formula borrowed from wikipedia - values in kPa*s (first value) and kelvin (the rest)
    kinematic_viscosity = 0.00002939 * exp(507.88/(water_temp+273.15-149.3)) / water_density

    # formulas from https://www.sheldonbrown.com/brandt/wind.html
    apparent_wind_speed = sqrt((v+wind_v*cos(wind_angle))**2+(wind_v*sin(wind_angle))**2)
    apparent_wind_angle = arccos((v+wind_v*cos(wind_angle))/apparent_wind_speed)
    
    reynolds = (v+water_flow) * boat_length / kinematic_viscosity
    cd_water = 0.455/(log10(reynolds)**2.58) # formula from Robert A. Granger, “Fluid Mechanics”, Dover 1995

    air_drag = cos(apparent_wind_angle) * apparent_wind_speed**2 * 0.5 * air_density * cd_air * A_air
    water_drag = (v+water_flow)**2 * cd_water * 0.5 * 1.07 * water_density * A_water

    # the 1.2 is to account for wave drag, which is not computed here
    # See https://sanderroosendaal.wordpress.com/2010/11/21/drag-revisited-2/ for more
    power = v*(air_drag+1.2*water_drag)
    
    return power
    
def powerdiff(v, watts):
    return watts - rowpower(v)
    
def row_v(v0, **kwargs):
    #create kwargs version that calls scipy
    sol = root_scalar(powerdiff, args=(rowpower(v0,**kwargs)), bracket = [0.1, 10], method='brentq')
    return sol.root
    
def powerdiff2(v, watts, kwargs):
    return rowpower(v, **kwargs) - watts

# turns a given watts into a speed. NB call rowpower as the watts value to compare two parameter sets    
def rowspeed(watts, **kwargs):
    #fix bracket for water_flow values < 0
    if 'water_flow' in kwargs and kwargs['water_flow'] < 0:
        bracket = [0.1-kwargs['water_flow'], 10]
    else:
        bracket = [0.1, 10]
    sol = root_scalar(powerdiff2, args=(watts, kwargs), bracket = bracket, method='brentq')
    return sol.root
