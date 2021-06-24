import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from collections import defaultdict
from pulp import *
import pandas as pd
# sphinx_gallery_thumbnail_number = 2

departure_airports = ["FRA", "LHR", "CDG", "AMS",
                      "MAD", "BCN", "FCO"]
arrival_airports = ["FRA", "LHR", "CDG", "AMS",
                    "MAD", "BCN", "FCO"]

# departure_airports = ["FRA", "LHR", "CDG", "AMS",
#               "MAD", "BCN", "FCO", "DUB", "VIE", "ZRH"]
# arrival_airports = ["FRA", "LHR", "CDG", "AMS",
#               "MAD", "BCN", "FCO", "DUB", "VIE", "ZRH"]

# FRA LHR CDG AMS MAD BCN FCO DUB VIE ZRH"
# harvest = np.array([[0,  0,  3,  0,  3,  0,  0,  0,  0,  0],
#                     [0,  0,  4,  0,  4,  0,  0,  0,  0,  0],
#                     [3,  4,  0,  4,  3,  4,  4,  2,  3,  2],
#                     [0,  0,  4,  0,  3,  0,  0,  0,  0,  0],
#                     [3,  4,  3,  3,  0,  7,  4,  2,  2,  2],
#                     [0,  0,  4,  0,  7,  0,  0,  0,  0,  0],
#                     [0,  0,  4,  0,  4,  0,  0,  0,  0,  0],
#                     [0,  0,  2,  0,  2,  0,  0,  0,  0,  0],
#                     [0,  0,  3,  0,  2,  0,  0,  0,  0,  0],
#                     [0,  0,  2,  0,  2,  0,  0,  0,  0,  0]])

# harvest = np.array([[0,  0,  3,  0,  3,  0,  0,  0,  0,  0],
#                     [0,  0,  3,  0,  4,  0,  0,  0,  0,  0],
#                     [3,  3,  0,  3,  3,  3,  3,  2,  2,  2],
#                     [0,  0,  3,  0,  3,  0,  0,  0,  0,  0],
#                     [3,  4,  3,  3,  0,  6,  3,  1,  1,  2],
#                     [0,  0,  3,  0,  6,  0,  0,  0,  0,  0],
#                     [0,  0,  3,  0,  3,  0,  0,  0,  0,  0],
#                     [0,  0,  2,  0,  1,  0,  0,  0,  0,  0],
#                     [0,  0,  2,  0,  1,  0,  0,  0,  0,  0],
#                     [0,  0,  2,  0,  2,  0,  0,  0,  0,  0]])

# harvest = np.array([[0,  0,  2,  0,  3,  0,  0,  0,  0,  0],
#                     [0,  0,  3,  0,  3,  0,  0,  0,  0,  0],
#                     [2,  3,  0,  3,  2,  3,  3,  2,  2,  2],
#                     [0,  0,  3,  0,  3,  0,  0,  0,  0,  0],
#                     [3,  3,  2,  3,  0,  6,  3,  1,  1,  2],
#                     [0,  0,  3,  0,  6,  0,  0,  0,  0,  0],
#                     [0,  0,  3,  0,  3,  0,  0,  0,  0,  0],
#                     [0,  0,  2,  0,  1,  0,  0,  0,  0,  0],
#                     [0,  0,  2,  0,  1,  0,  0,  0,  0,  0],
#                     [0,  0,  2,  0,  2,  0,  0,  0,  0,  0]])

# harvest = np.array([[0,  5,  3,  3,  3,  3,  0,  2,  4,  0],
#                     [5,  0,  4,  5,  4,  2,  3,  6,  3,  4],
#                     [3,  4,  0,  4,  3,  4,  4,  0,  3,  0],
#                     [3,  5,  4,  0,  3,  4,  3,  4,  3,  3],
#                     [3,  4,  3,  3,  0,  8,  4,  0,  0,  0],
#                     [3,  2,  4,  4,  8,  0,  4,  0,  0,  0],
#                     [0,  3,  4,  3,  4,  4,  0,  0,  0,  0],
#                     [2,  6,  0,  4,  0,  0,  0,  0,  0,  0],
#                     [4,  3,  3,  3,  0,  0,  0,  0,  0,  3],
#                     [0,  4,  0,  3,  0,  0,  0,  0,  3,  0]])

# harvest = np.array([[0,  4,  3,  2,  3,  3,  2,  2,  3,  2],
#                     [4,  0,  3,  4,  4,  2,  2,  5,  2,  3],
#                     [3,  3,  0,  3,  3,  3,  3,  2,  2,  2],
#                     [2,  4,  3,  0,  3,  3,  3,  3,  2,  2],
#                     [3,  4,  3,  3,  0,  6,  3,  1,  1,  2],
#                     [3,  2,  3,  3,  6,  0,  3,  1,  2,  2],
#                     [2,  2,  3,  3,  3,  3,  0,  0,  1,  1],
#                     [2,  5,  2,  3,  1,  1,  0,  0,  1,  1],
#                     [3,  2,  2,  2,  1,  2,  1,  1,  0,  2],
#                     [2,  3,  2,  2,  2,  2,  1,  1,  2,  0]])
frequencias{('CD1', 'CD1'): 0, ('CD1', 'CD2'): 3, ('CD1', 'CD3'): 6, ('CD1', 'CD4'): 4, ('CD1', 'CD5'): 0, ('CD1', 'CD6'): 4, ('CD1', 'CD7'): 0, ('CD1', 'CD8'): 0, ('CD1', 'CD9'): 0, ('CD1', 'CD10'): 4, ('CD2', 'CD1'): 0, ('CD2', 'CD2'): 0, ('CD2', 'CD3'): 6, ('CD2', 'CD4'): 0, ('CD2', 'CD5'): 4, ('CD2', 'CD6'): 0, ('CD2', 'CD7'): 3, ('CD2', 'CD8'): 0, ('CD2', 'CD9'): 0, ('CD2', 'CD10'): 0, ('CD3', 'CD1'): 0, ('CD3', 'CD2'): 0, ('CD3', 'CD3'): 0, ('CD3', 'CD4'): 0, ('CD3', 'CD5'): 0, ('CD3', 'CD6'): 5, ('CD3', 'CD7'): 1, ('CD3', 'CD8'): 3, ('CD3', 'CD9'): 0, ('CD3', 'CD10'): 3, ('CD4', 'CD1'): 0, ('CD4', 'CD2'): 3, ('CD4', 'CD3'): 5, ('CD4', 'CD4'): 0, ('CD4', 'CD5'): 0, ('CD4', 'CD6'): 0, ('CD4', 'CD7'): 0, ('CD4', 'CD8'): 4, ('CD4', 'CD9'): 3, ('CD4', 'CD10'): 3, ('CD5', 'CD1'): 4, ('CD5', 'CD2'): 0, ('CD5', 'CD3'): 7, ('CD5', 'CD4'): 5, ('CD5', 'CD5'): 0, ('CD5', 'CD6'): 0, ('CD5', 'CD7'): 0, ('CD5', 'CD8'): 0, ('CD5', 'CD9'): 1, ('CD5', 'CD10'): 2, ('CD6', 'CD1'): 0, ('CD6', 'CD2'): 2, ('CD6', 'CD3'): 0, ('CD6', 'CD4'): 4, ('CD6', 'CD5'): 4, ('CD6', 'CD6'): 0, ('CD6', 'CD7'): 2, ('CD6', 'CD8'): 3, ('CD6', 'CD9'): 2, ('CD6', 'CD10'): 2, ('CD7', 'CD1'): 4, ('CD7', 'CD2'): 0, ('CD7', 'CD3'): 3, ('CD7', 'CD4'): 5, ('CD7', 'CD5'): 5, ('CD7', 'CD6'): 10, ('CD7', 'CD7'): 0, ('CD7', 'CD8'): 0, ('CD7', 'CD9'): 1, ('CD7', 'CD10'): 0, ('CD8', 'CD1'): 3, ('CD8', 'CD2'): 2, ('CD8', 'CD3'): 1, ('CD8', 'CD4'): 0, ('CD8', 'CD5'): 3, ('CD8', 'CD6'): 1, ('CD8', 'CD7'): 6, ('CD8', 'CD8'): 0, ('CD8', 'CD9'): 1, ('CD8', 'CD10'): 0, ('CD9', 'CD1'): 3, ('CD9', 'CD2'): 0, ('CD9', 'CD3'): 8, ('CD9', 'CD4'): 0, ('CD9', 'CD5'): 4, ('CD9', 'CD6'): 0, ('CD9', 'CD7'): 2, ('CD9', 'CD8'): 0, ('CD9', 'CD9'): 0, ('CD9', 'CD10'): 0, ('CD10', 'CD1'): 1, ('CD10', 'CD2'): 3, ('CD10', 'CD3'): 0, ('CD10', 'CD4'): 1, ('CD10', 'CD5'): 2, ('CD10', 'CD6'): 0, ('CD10', 'CD7'): 3, ('CD10', 'CD8'): 3, ('CD10', 'CD9'): 0, ('CD10', 'CD10'): 0}


harvest = np.array([[0,  0,  1,  1,  4,  4,  0],
                    [5,  0,  1,  6,  5,  3,  0],
                    [4,  5,  0,  4,  3,  0,  4],
                    [3,  0,  1,  0,  0,  1,  0],
                    [0,  0,  2,  3,  0,  1,  4],
                    [0,  0,  5,  4,  9,  0,  4],
                    [3,  3,  1,  3,  0,  2,  0]])

# NAO MEXER NESTE
# "FRA LHR CDG AMS MAD BCN FCO DUB VIE ZRH"
# harvest = np.array([[0,  0,  0,  0,  0,  0,  0,  0,  0,  0], FRA
#                     [0,  0,  0,  0,  0,  0,  0,  0,  0,  0], LHR
#                     [0,  0,  0,  0,  0,  0,  0,  0,  0,  0], CDG
#                     [0,  0,  0,  0,  0,  0,  0,  0,  0,  0], AMS
#                     [0,  0,  0,  0,  0,  0,  0,  0,  0,  0], MAD
#                     [0,  0,  0,  0,  0,  0,  0,  0,  0,  0], BCN
#                     [0,  0,  0,  0,  0,  0,  0,  0,  0,  0], FCO
#                     [0,  0,  0,  0,  0,  0,  0,  0,  0,  0], DUB
#                     [0,  0,  0,  0,  0,  0,  0,  0,  0,  0], VIE
#                     [0,  0,  0,  0,  0,  0,  0,  0,  0,  0]]) ZRH

fig, ax = plt.subplots()
im = ax.imshow(harvest)
print(im)
fig.colorbar(im)
# We want to show all ticks...
ax.set_xticks(np.arange(len(arrival_airports)))
ax.set_yticks(np.arange(len(departure_airports)))
# ... and label them with the respective list entries
ax.set_xticklabels(arrival_airports)
ax.set_yticklabels(departure_airports)
ax.xaxis.set_ticks_position('top')

# Loop over data dimensions and create text annotations.
for i in range(len(departure_airports)):
    for j in range(len(arrival_airports)):
        text = ax.text(j, i, harvest[i, j],
                       ha="center", va="center", color="w")

# ax.set_title("Network frequencies for optimum aircraft (112 seats)")
fig.tight_layout()
plt.show()

# import numpy as np
# import matplotlib
# import matplotlib.pyplot as plt
# from matplotlib import pyplot

# # sphinx_gallery_thumbnail_number = 2

# departure_airports = ["FRA", "LHR", "CDG", "AMS",
#                       "MAD", "BCN", "FCO", "DUB", "VIE", "ZRH"]
# arrival_airports = ["FRA", "LHR", "CDG", "AMS",
#                     "MAD", "BCN", "FCO", "DUB", "VIE", "ZRH"]

# harvest = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])

# fig1, (ax1, ax2) = pyplot.subplots(2, sharex = True, sharey = False)
# ax1.imshow(harvest, interpolation = 'none', aspect = 'auto')
# ax2.imshow(harvest, interpolation = 'bicubic', aspect = 'auto')

# # We want to show all ticks...
# ax1.set_xticks(np.arange(len(arrival_airports)))
# ax1.set_yticks(np.arange(len(departure_airports)))
# # ... and label them with the respective list entries
# ax2.set_xticklabels(arrival_airports)
# ax2.set_yticklabels(departure_airports)

# # Rotate the tick labels and set their alignment.
# plt.setp(ax1.get_xticklabels(), rotation=45, ha="right",
#          rotation_mode="anchor")

# # Loop over data dimensions and create text annotations.
# for i in range(len(departure_airports)):
#     for j in range(len(arrival_airports)):
#         text = ax1.text(j, i, harvest[i, j],
#                        ha="center", va="center", color="w")

# ax1.set_title("Harvest of local arrival_airports (in tons/year)")
# fig1.tight_layout()
# plt.show()
