''' Tests for oscillator implementation
    copyright Maximilian Cornwell 2023 '''
import ctypes
import math
import unittest

from test.constants import sampling_frequency, block_size

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig


class OscillatorInterface:
    ''' ctypes wrapper around test shared object file'''
    freq = 0
    testlib = ctypes.CDLL('test.so')

    def setUp(self):
        ''' Load in the test object file and define the function '''
        float_pointer = ctypes.POINTER(ctypes.c_float)
        self.testlib.test_oscillator.argtypes = [ctypes.c_float, ctypes.c_int,
                                                 float_pointer, float_pointer]
        self.testlib.test_lut_oscillator.argtypes = [ctypes.c_float, ctypes.c_int,
                                                     float_pointer, float_pointer]

    def run_osc(self, n_samples: int) -> np.ndarray:
        ''' Run the Oscillator. Output is a complex exponential at frequency f with length n'''
        cos_out = np.zeros(n_samples, dtype=np.single)
        cos_out_p = cos_out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        sin_out = np.zeros(n_samples, dtype=np.single)
        sin_out_p = sin_out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        self.testlib.test_oscillator(self.freq, n_samples, cos_out_p, sin_out_p)
        return cos_out + 1j*sin_out

    def run_lut_osc(self, n_samples: int) -> np.ndarray:
        ''' Run the Oscillator. Output is a complex exponential at frequency f with length n'''
        cos_out = np.zeros(n_samples, dtype=np.single)
        cos_out_p = cos_out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        sin_out = np.zeros(n_samples, dtype=np.single)
        sin_out_p = sin_out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        self.testlib.test_lut_oscillator(self.freq, n_samples, cos_out_p, sin_out_p)
        return cos_out + 1j*sin_out

    def set_f(self, freq: float, fs: float):
        ''' set the frequency to freq '''
        self.freq = freq/fs

    def calculate_length(self, precision: float):
        ''' Calculate the length of sample required for a particular frequency resolution '''
        return int(2**math.ceil(math.log2((sampling_frequency/precision))))


class TestOscillator(OscillatorInterface, unittest.TestCase):
    ''' Test Suite for Oscillator, checks frequency accuracy and amplitude accuracy/consistency.
        Uses an interface to the OscillatorInterface '''
    debug = False # controls whether plots will be made
    test_frequencies = 440*2**((np.arange(21, 109)-69)/12)
    freq_accuracy = 0.5 # cents
    power_accuracy = 0.001
    peak_thresh = -96

    def osc_call(self, n_samples: int) -> np.ndarray:
        ''' Call for the specific oscillator implementation '''
        return self.run_osc(n_samples)

    def test_sine_frequency(self) -> None:
        ''' Checks that the oscillator produces a range of test frequencies.
            Checks accuracy is within the desired precision, scales capture window to suit'''
        for freq in self.test_frequencies:
            with self.subTest(f'{freq:.2f} Hz'):
                f_u = freq*2**(self.freq_accuracy/1200)
                f_l = freq*2**(-self.freq_accuracy/1200)
                precision = f_u-f_l
                # precision is FS/n_samples
                # convert the precision to an fft length
                n_samples = self.calculate_length(precision)
                freqs = np.fft.fftshift(np.fft.fftfreq(n_samples))*sampling_frequency
                self.set_f(freq, sampling_frequency)
                vector = self.run_osc(n_samples)
                f_vector = 20*np.log10(np.abs(np.fft.fftshift(np.fft.fft(vector)))/n_samples)
                pkidx, _  = sig.find_peaks(f_vector, height=self.peak_thresh, prominence=1)
                f_measured = freqs[pkidx]

                if self.debug:
                    _, fax = plt.subplots()
                    fax.plot(freqs, f_vector, label='Data')
                    fax.scatter(freqs[pkidx], f_vector[pkidx], label='Peak')
                    fax.grid()
                    fax.legend()
                    fax.set_xlabel('Frequency (Hz)')
                    fax.set_title(f'Frequency Domain (f_0 = {freq:.2f} Hz)')
                    plt.show()

                self.assertEqual(1, len(f_measured))
                cents = 1200*np.log2(f_measured/freq)
                self.assertLess(cents, self.freq_accuracy)

    def test_sine_amplitude(self):
        ''' Checks that the amplitude of the sinusoid is correct '''
        n_samples = sampling_frequency*30
        freq = 1000
        self.set_f(freq, sampling_frequency)
        vector = self.run_osc(n_samples)[:-block_size]
        power = np.abs(vector)**2
        if self.debug:
            time = np.arange(n_samples-block_size)/sampling_frequency
            _, tax = plt.subplots()
            tax.plot(time, np.real(vector), label='Real')
            tax.plot(time, np.imag(vector), label='Imaginary')
            tax.plot(time, power, label='Power')
            tax.legend()
            tax.set_xlabel('Time')
            tax.set_title('Time Domain')
            tax.grid()
            plt.show()

        self.assertAlmostEqual(np.min(power), 1., delta=self.power_accuracy)
        self.assertAlmostEqual(np.max(power), 1., delta=self.power_accuracy)

class TestLutOscillator(TestOscillator):
    ''' Test Suite for LUT version of oscillator '''
    peak_thresh = -66
    power_accuracy = 0.001

    def osc_call(self, n_samples: int) -> np.ndarray:
        ''' Call for the specific oscillator implementation '''
        return self.run_lut_osc(n_samples)


def main():
    ''' For debugging/plotting '''
    osc_test = TestLutOscillator()
    osc_test.setUp()
    osc_test.debug = True
    osc_test.test_sine_frequency()
    osc_test.test_sine_amplitude()

if __name__=='__main__':
    main()
