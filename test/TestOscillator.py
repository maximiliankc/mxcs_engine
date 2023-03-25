import ctypes
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sig
import unittest
import math

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
    test_frequencies = 440*2**((np.arange(21, 109)-69)/12)
    accuracy = 0.5 # cents

    def setUp(self) -> None:
        self.implementation = OscillatorInterface()

    def testSineFrequency(self) -> None:

        for f in self.test_frequencies:
            with self.subTest(f'{f:.2f} Hz'):
                fu = f*2**(self.accuracy/1200)
                fl = f*2**(-self.accuracy/1200)
                precision = (fu-fl)
                # precision is FS/N
                # convert the precision to an fft length
                N = int(2**math.ceil(math.log2((self.fs/precision))))
                freqs = np.fft.fftshift(np.fft.fftfreq(N))*self.fs
                vector = self.implementation.run(f/self.fs, N) # TODO pick a length based on required certainty?
                f_vector = 20*np.log10(np.abs(np.fft.fftshift(np.fft.fft(vector)))/N)
                pkidx, _  = sig.find_peaks(f_vector, height=-96, prominence=1)
                f_measured = freqs[pkidx]

                if self.debug:
                    _, fax = plt.subplots()
                    fax.plot(freqs, f_vector, label='Data')
                    fax.scatter(freqs[pkidx], f_vector[pkidx], label='Peak')
                    fax.grid(True)
                    fax.legend()
                    fax.set_xlabel('Frequency (Hz)')
                    fax.set_title(f'Frequency Domain (f_0 = {f:.2f} Hz)')
                    plt.show()

                self.assertEqual(1, len(f_measured))
                cents = 1200*np.log2(f_measured/f)
                self.assertLess(cents, self.accuracy)

    def testSineAmplitude(self):
        N = self.implementation.block_size*2**8
        for f in [100, 120]:
            vector = self.implementation.run(2*np.pi*f/self.fs, N) # TODO pick a length based on required certainty?
            power = np.abs(vector)**2
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

                plt.show()

def main():
    ''' For debugging/plotting '''
    osc_test = TestOscillator()
    osc_test.setUp()
    osc_test.debug = True
    osc_test.testSineFrequency()
    osc_test.testSineAmplitude()

if __name__=='__main__':
    main()
