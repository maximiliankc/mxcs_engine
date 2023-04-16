''' inverse_sqrt - trying out a couple of approximations for oscillator normalisation '''

import numpy as np
import matplotlib.pyplot as plt

x = np.arange(0.9, 1.1, 0.001)
_, ax = plt.subplots()
ax.plot(x, x**(-0.5), ls=':')
y = 1 - 0.5*(x-1)
ax.plot(x, y)
y1 = 1 - 0.5*(x-1) + 0.375*(x-1)**2
ax.plot(x, y1)

_, ax2 = plt.subplots()
z = y*x**0.5
z1 = y1*x**0.5
ax2.plot(x, z)
ax2.plot(x, z1)
plt.show()
