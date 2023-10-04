''' Explore generating signals from a triangle wave
    Expect some aliasing, but maybe not too much '''

import numpy as np
import matplotlib.pyplot as plt

def triangle_wave(samples: int, frequency: float, fs: float):
    out = np.empty(samples)
    level = 0
    slope = 4*frequency/fs
    for n in range(samples):
        out[n] = level
        level += slope
        if abs(level) > 1:
            level = 2-level if level > 0 else -2-level
            slope = -slope
    return out

def main():
    N = 2**14
    fs = 44100
    for f in [100, 13289.75]:
        x = triangle_wave(N, f, fs)
        t = np.arange(N)/fs
        _, tax = plt.subplots()
        tax.plot(t, x)
        tax.set_ylabel('Level')
        tax.set_xlabel('Time (s)')
        tax.grid(True)

        xf = np.fft.fft(x)
        freqs = np.fft.fftfreq(N)*fs
        _, fax = plt.subplots()
        fax.plot(freqs, 20*np.log10(np.abs(xf)))
        fax.set_ylabel('Level (dBFS)')
        fax.set_xlabel('Frequency (Hz)')
        fax.grid(True)
        plt.show()




if __name__=='__main__':
    main()
