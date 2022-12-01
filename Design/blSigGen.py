# see https://ccrma.stanford.edu/~stilti/papers/blit.pdf
# and http://www.music.mcgill.ca/~gary/307/week5/node14.html
import numpy as np
import matplotlib.pyplot as p
import scipy.signal as s
from scipy import io
import math

threshold = 2**-32

def msinc(n: np.ndarray, f: float, M: int)->np.ndarray:
    ''' Calculates the periodic sinc function'''
    n = n + 2
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

def blit(n: np.ndarray, f: float)->np.ndarray:
    ''' Band limited impulse train '''
    M = 2*math.trunc(0.5/f) + 1
    y = msinc(n, f, M)
    return y

def bpblit(n: np.ndarray, f:float)->np.ndarray:
    ''' Bi-polar Band Limited Impulse Train'''
    M = 2*math.trunc(0.25/f)
    y = msinc(n, 2*f, M)
    return y

def blSawtooth(n: np.ndarray, f: float)->np.ndarray:
    ''' Band Limited Sawtooth Wave '''
    x = 2*blit(n, f)
    y = leakyIntegrator(x)
    return y

def blSquare(n: np.ndarray, f: float)->np.ndarray:
    ''' Band limited Square Wave '''
    x = 2*bpblit(n, f)
    y = leakyIntegrator(x)
    return y

def blTriangle(n: np.ndarray, f: float)->np.ndarray:
    ''' Band Limited Triangle wave '''
    x = 4*f*blSquare(n, f)
    y = leakyIntegrator(x)
    return y

def leakyIntegrator(x: np.ndarray, r:float=0.999)->np.ndarray:
    ''' A leaky integrator combined with a low pass filter,
     r controls the radius of the zeros, r closer to one will
     lower the cutoff frequency, but increase the size and duration
      of initial transients '''
    b = [1, -1]
    a = [1, -2*r, r**2]
    y = s.lfilter(b, a, x) # figure out some good filter coefficients to remove dc
    return y

def main():
    N = 2**16
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
