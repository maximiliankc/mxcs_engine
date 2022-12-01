import numpy as np
import matplotlib.pyplot as p
import scipy.signal as s

def main():
    fs = 48000
    r = 0.999
    [w, H_ideal] = s.freqz([1], [1, -1], 2048)
    [w, H_leaky] = s.freqz([1, -1], [1, -2*r, r**2], 2048)
    f = w*fs/(2*np.pi)

    _, ax = p.subplots()
    ax.semilogx(f, mag2db(H_ideal), label='ideal')
    ax.semilogx(f, mag2db(H_leaky), label='leaky')
    ax.grid(True)
    ax.legend()

    p.show()

def mag2db(x:np.ndarray)->np.ndarray:
    return 20*np.log10(abs(x))

if __name__ == "__main__":
    main()