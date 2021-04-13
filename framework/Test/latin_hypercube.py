import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from smt.sampling_methods import LHS

# xlimits = np.array([[70, 130], [75, 100],[25, 50],[15,35],[-5,-2],[32,40],[45,65],[10,20],[27,30],[1350,1500],[14,20],[50,120],[4,6],[1000,2500]])
xlimits =  np.array([[70, 130], [75, 120],[25, 50],[15,30],[-5,-2],[32,45],[45,65],[10,25],[27,30],[1350,1500],[14,25],[70,220],[4,6],[1000,3500],[39000,43000],[78,82],[1,1],[1,1],[1,1],[1,1]])
sampling = LHS(xlimits=xlimits)

num = 10
Initial_population = sampling(num)
Initial_population = [[round(y) for y in x] for x in Initial_population]


print(Initial_population)
# print(x.shape)
# fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
# plt.plot(x[:, 0], x[:, 1], "o")
# plt.xlabel("x")
# plt.ylabel("y")
# plt.show()

fig = plt.figure()
ax = Axes3D(fig)
ax.scatter(x[:, 0], x[:, 1], x[:, 2], "o")
plt.show()