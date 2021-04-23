"""
File name : Plot network results
Authors   : Alejandro Rios
Email     : aarc.88@gmail.com
Date      : November/2020
Last edit : November/2020
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
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import networkx as nx
# =============================================================================
# CLASSES
# =============================================================================

# =============================================================================
# FUNCTIONS
# =============================================================================
# df = pd.read_csv('Data4Clustering02.csv', header=0, delimiter=', ')
# df_head = df.head()
# =============================================================================
# MAIN
# =============================================================================

# =============================================================================
# TEST
# =============================================================================


fig, ax = plt.subplots()
m = Basemap(resolution='i', projection='merc', llcrnrlat=35,
            urcrnrlat=60, llcrnrlon=-15, urcrnrlon=30)
m.drawmapboundary(fill_color='aqua')
m.fillcontinents(color='1.0', lake_color='aqua')
m.drawcoastlines()
m.drawcountries()
parallels = np.arange(0., 81, 10.)
# labels = [left, right, top, bottom]
m.drawparallels(parallels, labels=[False, True, True, False])
meridians = np.arange(10., 351., 20.)
m.drawmeridians(meridians, labels=[True, False, False, True])

data = pd.read_csv('network_EU.csv', header=0, delimiter=', ')
number_of_airports = len(data.APT)
# Creamos ciudades de la 0 a la 9
cities = [i for i in range(number_of_airports)]
arcs = [(i, j) for i in cities for j in cities if i != j]

lon_coordinates = data.LON
lat_coordinates = data.LAT

x = lon_coordinates
y = lat_coordinates
x = x.values.tolist()
y = y.values.tolist()
# print(x)
names = data.APT

x, y = m(x, y)
m.scatter(x, y, 100, color="orange", marker="o", edgecolor="r", zorder=3)
for i in range(len(names)):
    plt.text(x[i], y[i], names[i], va="baseline", color='k',
             fontsize=12, family="monospace", weight="bold")
# for i, j in arcs:
#     # plt.plot([lon_coordinates[i], lon_coordinates[j]], [lat_coordiantes[i], lat_coordiantes[j]], color="blue", alpha=0.3)
#     x1, y1 = m(lon_coordinates[i], lat_coordinates[i])
#     x2, y2 = m(lon_coordinates[j], lat_coordinates[j])
#     # m.drawgreatcircle(x1, y2, y1, y2, linewidth=2, color='b')
#     m.drawgreatcircle(lon_coordinates[i], lat_coordinates[i], lon_coordinates[j], lat_coordinates[j], linewidth=1, color='purple', alpha = 0.3, )

plt.show()
