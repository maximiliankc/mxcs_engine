# see https://ccrma.stanford.edu/~stilti/papers/blit.pdf
# and http://www.music.mcgill.ca/~gary/307/week5/node14.html
import numpy as np
import matplotlib.pyplot as p
import scipy.signal as s
from scipy import io
import math

threshold = 2**-32

def blit(n, f):
    M = 2*math.trunc(0.5/f) + 1
    top = np.sin(np.pi*M*f*n)
    topc = np.cos(np.pi*M*f*n)
    bottom = M*np.sin(np.pi*f*n)
    bottomc = np.cos(np.pi*f*n)
    y = np.empty_like(top)
    smallbottom = (bottom<threshold)*(bottom>-threshold)
    ysin = top/bottom
    ycos = topc/bottomc
    y[smallbottom] = ycos[smallbottom]
    y[~smallbottom] = ysin[~smallbottom]
    return y

def bpblit(n, f):
    M = 2*math.trunc(0.25/f)
    top = np.sin(2*np.pi*M*f*n)
    topc = np.cos(2*np.pi*M*f*n)
    bottom = M*np.sin(2*np.pi*f*n)
    bottomc = np.cos(2*np.pi*f*n)
    y = np.empty_like(top)
    smallbottom = (bottom<threshold)*(bottom>-threshold)
    ysin = top/bottom
    ycos = topc/bottomc
    y[smallbottom] = ycos[smallbottom]
    y[~smallbottom] = ysin[~smallbottom]
    return y

def blSawtooth(n, f):
    x = blit(n, f)
    y = leakyIntegrator(x)
    return y

def blSquare(n, f):
    x = 2*bpblit(n, f)
    y = leakyIntegrator(x)
    return y

def blTriangle(n, f):
    x = 2*f*blSquare(n, f)
    y = leakyIntegrator(x)
    return y

def leakyIntegrator(x):
    r = 0.9999
    b = [1]
    a = [1, -r]
    y = s.lfilter(b, a, x) # figure out some good filter coefficients to remove dc
    return y

def main():
    N = 2**18
    n = np.arange(N)
    fs = 44100

    freqs = 27.5*2**np.arange(8)

    for f in freqs:
        _, tAx = p.subplots()
        _, fAx = p.subplots()

        combos = [('blit', blit),
                  ('bpblit', bpblit),
                  ('Sawtooth', blSawtooth),
                  ('Triangle', blTriangle),
                  ('Square', blSquare),
                 ]

        for (leg, generator) in combos:
            fnorm = f/fs
            y = generator(n, fnorm)

            print(f'{leg} average: {np.mean(y)}')

            max = np.max(np.abs(y))
            io.wavfile.write(f'{leg}_({int(f)}).wav', fs, y/max)

            Y = np.fft.fft(y)
            tAx.plot(n/fs, y, label=leg)
            fAx.plot(fs*n/N, np.abs(Y), label=leg)
            tAx.legend()
            tAx.grid(True)
            tAx.set_xlabel('Time')
            tAx.set_ylabel('Magnitude')
            fAx.legend()
            fAx.grid(True)
            fAx.set_xlabel('Frequency')
            fAx.set_ylabel('Magnitude')
            tAx.set_title(f'frequency = {f} Hz, time domain')
            fAx.set_title(f'frequency = {f} Hz, freq domain')

        p.show()

if __name__ == "__main__":
    main()
