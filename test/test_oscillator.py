''' Tests for oscillator implementation '''
import ctypes
import math
import unittest
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig


class OscillatorInterface:
    ''' ctypes wrapper around test shared object file'''
    def __init__(self):
        ''' Load in the test object file and define the function '''
        self.testlib = ctypes.CDLL('test.so')
        float_pointer = ctypes.POINTER(ctypes.c_float)
        self.testlib.test_oscillator.argtypes = [ctypes.c_float, ctypes.c_int,
                                                 float_pointer, float_pointer]

    def run(self, f: float, n: int) -> np.ndarray:
        ''' Run the Oscillator. Output is a complex exponential at frequency f with length n'''
        cosOut = (n*ctypes.c_float)(*n*[0])
        sinOut = (n*ctypes.c_float)(*n*[0])
        self.testlib.test_oscillator(ctypes.c_float(f), ctypes.c_int(n), cosOut, sinOut)
        return np.array(cosOut) + 1j*np.array(sinOut)


class TestOscillator(unittest.TestCase):
    ''' Test Suite for Oscillator, checks frequency accuracy and amplitude accuracy/consistency.
        Uses an interface to the OscillatorInterface '''
    debug = False # controls whether plots will be made
    fs = 48000 # Hz
    test_frequencies = 440*2**((np.arange(21, 109)-69)/12)
    freq_accuracy = 0.5 # cents
    power_accuracy = 0.001

    def setUp(self) -> None:
        self.implementation = OscillatorInterface()

    def test_sine_frequency(self) -> None:
        ''' Checks that the oscillator produces a range of test frequencies.
            Checks accuracy is within the desired precision, scales capture window to suit'''
        for f in self.test_frequencies:
            with self.subTest(f'{f:.2f} Hz'):
                fu = f*2**(self.freq_accuracy/1200)
                fl = f*2**(-self.freq_accuracy/1200)
                precision = fu-fl
                # precision is FS/N
                # convert the precision to an fft length
                N = int(2**math.ceil(math.log2((self.fs/precision))))
                freqs = np.fft.fftshift(np.fft.fftfreq(N))*self.fs
                vector = self.implementation.run(f/self.fs, N)
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
                self.assertLess(cents, self.freq_accuracy)

    def test_sine_amplitude(self):
        ''' Checks that the amplitude of the sinusoid is '''
        N = self.fs*30
        f = 1000
        vector = self.implementation.run(2*np.pi*f/self.fs, N)
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
        self.assertAlmostEqual(np.min(power), 1., delta=self.power_accuracy)
        self.assertAlmostEqual(np.max(power), 1., delta=self.power_accuracy)

def main():
    ''' For debugging/plotting '''
    osc_test = TestOscillator()
    osc_test.setUp()
    osc_test.debug = True
    osc_test.test_sine_frequency()
    osc_test.test_sine_amplitude()

if __name__=='__main__':
    main()
