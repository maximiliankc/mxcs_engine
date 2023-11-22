''' Band limited signal generator file
    copyright Maximilian Cornwell 2023
    Band limiited impulse train code based on
    https://ccrma.stanford.edu/~stilti/papers/blit.pdf
    and http://www.music.mcgill.ca/~gary/307/week5/node14.html '''
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as s
from scipy import io
import math

threshold = 2**-32

def msinc(n: np.ndarray, f: float, M: int)->(np.ndarray,np.ndarray):
    ''' Calculates the periodic sinc function'''
    top = np.exp(1j*np.pi*M*f*n)
    bottom = np.exp(1j*np.pi*f*n)
    top_phase = np.angle(top)
    bottom_phase = np.angle(bottom)
    phase_error = M*bottom_phase - top_phase

    phase_error = phase_error % 2*np.pi
    y = np.real(np.empty_like(top))
    smallbottom = (np.imag(bottom)<threshold/M)*(np.imag(bottom)>-threshold/M)
    ysin = np.imag(top)/(M*np.imag(bottom))
    ycos = np.real(top)/np.real(bottom)
    y[smallbottom] = ycos[smallbottom]
    y[~smallbottom] = ysin[~smallbottom]
    return y, phase_error%(2*np.pi)

def blit(n: np.ndarray, f: float)->(np.ndarray,np.ndarray):
    ''' Band limited impulse train '''
    M = 2*math.trunc(0.4/f) + 1
    y, phase_error = msinc(n, f, M)
    return y, phase_error

def bpblit(n: np.ndarray, f:float)->(np.ndarray,np.ndarray):
    ''' Bi-polar Band Limited Impulse Train'''
    f = 2*f
    M = 2*math.trunc(0.4/f)
    y, phase_error = msinc(n, f, M)
    return y, phase_error

def blSawtooth(n: np.ndarray, f: float)->(np.ndarray,np.ndarray):
    ''' Band Limited Sawtooth Wave '''
    x, phase_error = blit(n, f)
    y = leakyIntegrator(2*x)
    return y, phase_error

def blSquare(n: np.ndarray, f: float)->(np.ndarray,np.ndarray):
    ''' Band limited Square Wave '''
    x, phase_error = bpblit(n, f)
    y = leakyIntegrator(2*x)
    return y, phase_error

def blTriangle(n: np.ndarray, f: float)->(np.ndarray,np.ndarray):
    ''' Band Limited Triangle wave '''
    x, phase_error = blSquare(n, f)
    y = leakyIntegrator(4*f*x)
    return y, phase_error

def leakyIntegrator(x: np.ndarray, r:float=0.999)->np.ndarray:
    ''' A leaky integrator combined with a low pass filter,
     r controls the radius of the poles, r closer to one will
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

    freqs = 27.5*2**(np.arange(16)/2)

    for f in freqs:
        _, tAx = plt.subplots()
        _, eAx = plt.subplots()
        _, fAx = plt.subplots()

        combos = [('blit', blit),
                #   ('bpblit', bpblit),
                #   ('Sawtooth', blSawtooth),
                #   ('Triangle', blTriangle),
                #   ('Square', blSquare),
                 ]

        for (leg, generator) in combos:
            fnorm = f/fs
            y, phase_error = generator(n, fnorm)

            max_val = np.max(np.abs(y))
            io.wavfile.write(f'{leg}_({int(f)}).wav', fs, y/max_val)

            Y = np.fft.fft(y)
            tAx.plot(n/fs, y, label=leg)
            eAx.plot(n/fs, phase_error, label=leg)
            fAx.plot(fs*n/N, 20*np.log10(np.abs(Y)), label=leg)
            tAx.legend()
            tAx.grid(True)
            tAx.set_xlabel('Time')
            tAx.set_ylabel('Magnitude')
            eAx.legend()
            eAx.grid(True)
            eAx.set_xlabel('Time')
            eAx.set_ylabel('Error (rad)')
            fAx.legend()
            fAx.grid(True)
            fAx.set_xlabel('Frequency')
            fAx.set_ylabel('Magnitude')
            tAx.set_title(f'frequency = {f} Hz, time domain')
            eAx.set_title(f'frequency = {f} Hz, phase error')
            fAx.set_title(f'frequency = {f} Hz, freq domain')

            dc = np.abs(Y[0])/(N**0.5)
            print(f'dc at {f} Hz = {dc} (freq), = {np.mean(y)} (time)')

        plt.show()

if __name__ == "__main__":
    main()
