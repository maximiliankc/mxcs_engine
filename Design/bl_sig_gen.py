''' Band limited signal generator file
    copyright Maximilian Cornwell 2023
    Band limiited impulse train code based on
    https://ccrma.stanford.edu/~stilti/papers/blit.pdf
    and http://www.music.mcgill.ca/~gary/307/week5/node14.html '''
import math
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as s
from scipy import io

THRESHOLD = 2**-32

def msinc(n: np.ndarray, f: float, m: int)->(np.ndarray,np.ndarray):
    ''' Calculates the periodic sinc function'''
    top = np.exp(1j*np.pi*m*f*n)
    bottom = np.exp(1j*np.pi*f*n)
    top_phase = np.angle(top)
    bottom_phase = np.angle(bottom)
    phase_error = m*bottom_phase - top_phase

    phase_error = phase_error % 2*np.pi
    y = np.real(np.empty_like(top))
    smallbottom = (np.imag(bottom)<THRESHOLD/m)*(np.imag(bottom)>-THRESHOLD/m)
    ysin = np.imag(top)/(m*np.imag(bottom))
    ycos = np.real(top)/np.real(bottom)
    y[smallbottom] = ycos[smallbottom]
    y[~smallbottom] = ysin[~smallbottom]
    return y, phase_error%(2*np.pi)

def blit(n: np.ndarray, f: float)->(np.ndarray,np.ndarray):
    ''' Band limited impulse train '''
    m = 2*math.trunc(0.4/f) + 1
    y, phase_error = msinc(n, f, m)
    return y, phase_error

def bp_blit(n: np.ndarray, f:float)->(np.ndarray,np.ndarray):
    ''' Bi-polar Band Limited Impulse Train'''
    f = 2*f
    m = 2*math.trunc(0.4/f)
    y, phase_error = msinc(n, f, m)
    return y, phase_error

def bl_sawtooth(n: np.ndarray, f: float)->(np.ndarray,np.ndarray):
    ''' Band Limited Sawtooth Wave '''
    x, phase_error = blit(n, f)
    y = leaky_integrator(2*x)
    return y, phase_error

def bl_square(n: np.ndarray, f: float)->(np.ndarray,np.ndarray):
    ''' Band limited Square Wave '''
    x, phase_error = bp_blit(n, f)
    y = leaky_integrator(2*x)
    return y, phase_error

def bl_triangle(n: np.ndarray, f: float)->(np.ndarray,np.ndarray):
    ''' Band Limited Triangle wave '''
    x, phase_error = bl_square(n, f)
    y = leaky_integrator(4*f*x)
    return y, phase_error

def leaky_integrator(x: np.ndarray, r:float=0.999)->np.ndarray:
    ''' A leaky integrator combined with a low pass filter,
     r controls the radius of the poles, r closer to one will
     lower the cutoff frequency, but increase the size and duration
      of initial transients '''
    b = [1, -1]
    a = [1, -2*r, r**2]
    y = s.lfilter(b, a, x) # figure out some good filter coefficients to remove dc
    return y

def main():
    ''' Function for exploring band limited signal generators '''
    n_samples = 2**16
    n = np.arange(n_samples)
    fs = 44100

    freqs = 27.5*2**(np.arange(16)/2)

    for f in freqs:
        _, t_ax = plt.subplots()
        _, e_ax = plt.subplots()
        _, f_ax = plt.subplots()

        combos = [('blit', blit),
                  ('bpblit', bp_blit),
                  ('Sawtooth', bl_sawtooth),
                  ('Triangle', bl_triangle),
                  ('Square', bl_square),
                 ]

        for (leg, generator) in combos:
            fnorm = f/fs
            y, phase_error = generator(n, fnorm)

            max_val = np.max(np.abs(y))
            io.wavfile.write(f'{leg}_({int(f)}).wav', fs, y/max_val)

            y_f = np.fft.fft(y)
            t_ax.plot(n/fs, y, label=leg)
            e_ax.plot(n/fs, phase_error, label=leg)
            f_ax.plot(fs*n/n_samples, 20*np.log10(np.abs(y_f)), label=leg)
            t_ax.legend()
            t_ax.grid(True)
            t_ax.set_xlabel('Time')
            t_ax.set_ylabel('Magnitude')
            e_ax.legend()
            e_ax.grid(True)
            e_ax.set_xlabel('Time')
            e_ax.set_ylabel('Error (rad)')
            f_ax.legend()
            f_ax.grid(True)
            f_ax.set_xlabel('Frequency')
            f_ax.set_ylabel('Magnitude')
            t_ax.set_title(f'frequency = {f} Hz, time domain')
            e_ax.set_title(f'frequency = {f} Hz, phase error')
            f_ax.set_title(f'frequency = {f} Hz, freq domain')

            dc = np.abs(y_f[0])/(n_samples**0.5)
            print(f'dc at {f} Hz = {dc} (freq), = {np.mean(y)} (time)')

        plt.show()

if __name__ == "__main__":
    main()
