''' Exploring leaky implemenation
    copyright Maximilian Cornwell 2023'''

import numpy as np
import matplotlib.pyplot as p
import scipy.signal as s

def main():
    fs = 44100
    r = 0.99
    [w, H_ideal] = s.freqz([1], [1, -1], 2**14, fs=44100)
    [w, H_leaky] = s.freqz([1, -1], [1, -2*r, r**2], 2**14, fs=44100)

    H_ideal = H_ideal[:2**9]
    H_leaky = H_leaky[:2**9]
    w = w[:2**9]

    _, ax = p.subplots()
    ax.plot(w, mag2db(H_ideal), label='ideal')
    ax.plot(w, mag2db(H_leaky), label='leaky')
    ax.grid(True)
    ax.legend()

    _, ax2 = p.subplots()
    ax2.plot(w, mag2db(H_ideal) - mag2db(H_leaky))
    ax2.set_title('Leaky Integrator Error')
    ax2.grid(True)
    ax2.legend()

    p.show()

def mag2db(x:np.ndarray)->np.ndarray:
    return 20*np.log10(abs(x))

if __name__ == "__main__":
    main()