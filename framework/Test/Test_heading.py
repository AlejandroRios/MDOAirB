import math
import pandas as pd
import numpy as np

# def get_bearing(lat1,lon1,lat2,lon2):
#     dLon = lon2 - lon1;
#     y = math.sin(dLon) * math.cos(lat2);
#     x = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(dLon);
#     brng = np.rad2deg(math.atan2(y, x));
#     if brng < 0: brng+= 360
#     return brng

def calculate_bearing(pointA, pointB):
    """
    Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing
departures = ['CD1', 'CD2', 'CD3', 'CD4',
        'CD5', 'CD6', 'CD7', 'CD8', 'CD9', 'CD10']
arrivals = ['CD1', 'CD2', 'CD3', 'CD4',
        'CD5', 'CD6', 'CD7', 'CD8', 'CD9', 'CD10']

data_airports = pd.read_csv("Database/Airports/airports.csv")

print(data_airports)

bearing = {}
heading = {}
for i in range(len(departures)):
    bearing[departures[i]] = {}
    heading[departures[i]] = {}
    for k in range(len(arrivals)):
        if (i != k) :
            bearing[departures[i]][arrivals[k]] = calculate_initial_compass_bearing((data_airports['LAT'][i],data_airports['LON'][i]),(data_airports['LAT'][k],data_airports['LON'][k]))
            heading[departures[i]][arrivals[k]] = bearing[departures[i]][arrivals[k]] - (data_airports['DMG'][i] + data_airports['DMG'][k])/2
        else:
            bearing[departures[i]][arrivals[k]] = 0
            heading[departures[i]][arrivals[k]] = 0


print(heading)