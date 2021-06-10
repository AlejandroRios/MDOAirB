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
