import ctypes
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sig
import unittest

class OscillatorInterface:
    def __init__(self):
        ''' Load in the test object file and define the function '''
        self.block_size = 16
        self.testlib = ctypes.CDLL('test.so')
        float_pointer = ctypes.POINTER(ctypes.c_float)
        self.testlib.test_oscillator.argtypes = [ctypes.c_float, ctypes.c_int, float_pointer, float_pointer]

    def run(self, f: float, n: int) -> np.ndarray:
        ''' Run the Oscillator. Output is a complex exponential at frequency f with length n'''
        cosOut = (n*ctypes.c_float)(*n*[0])
        sinOut = (n*ctypes.c_float)(*n*[0])
        self.testlib.test_oscillator(ctypes.c_float(f), ctypes.c_int(n), cosOut, sinOut)
        return np.array(cosOut) + 1j*np.array(sinOut)

class TestOscillator(unittest.TestCase):
    debug = False # controls whether plots will be made
    fs = 48000

    def setUp(self) -> None:
        self.implementation = OscillatorInterface()

    def testSine(self) -> None:
        N = self.implementation.block_size*2**8
        freqs = np.fft.fftshift(np.fft.fftfreq(N))*self.fs
        for f in [100, 120]:
            vector = self.implementation.run(2*np.pi*f/self.fs, N) # TODO pick a length based on required certainty?
            f_vector = np.fft.fftshift(np.fft.fft(vector))/(N**0.5)
            power = np.abs(vector)**2
            pkidx, _  = sig.find_peaks(np.abs(f_vector))
            if self.debug:
                t = np.arange(N)/self.fs
                _, tax = plt.subplots()
                tax.plot(t, np.real(vector), label='Real')
                tax.plot(t, np.imag(vector), label='Imaginary')
                tax.plot(t, power, label='Power')
                tax.legend()
                tax.set_xlabel('Time')
                tax.set_title('Time Domain')
                tax.grid()

                _, fax = plt.subplots()
                fax.plot(freqs, np.abs(f_vector), label='Data')
                fax.scatter(freqs[pkidx], np.abs(f_vector[pkidx]), label='Peak')
                fax.grid(True)
                fax.legend()
                fax.set_xlabel('Frequency (Hz)')
                fax.set_title('Frequency Domain')


                plt.show()


def main():
    ''' For debugging/plotting '''
    osc_test = TestOscillator()
    osc_test.setUp()
    osc_test.debug = True
    osc_test.testSine()

if __name__=='__main__':
    main()
