import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from smt.sampling_methods import LHS

xlimits = np.array([[70, 130], [75, 100],[25, 50],[15,35],[-5,-2],[32,40],[45,65],[10,20],[27,30],[1350,1500],[14,20],[50,120],[4,6],[1000,2500]])
sampling = LHS(xlimits=xlimits)

num = 10
x = int(sampling(num)


print(int(x))
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