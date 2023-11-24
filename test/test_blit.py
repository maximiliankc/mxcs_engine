''' Tests for Band limited impulse train functions
    copyright Maximilian Cornwell 2023 '''
import ctypes
import unittest
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sig

from .constants import sampling_frequency, block_size

class BlitInterface:
    ''' Interface for BLIT functions '''
    testlib = ctypes.CDLL('test.so')

    def __init__(self):
        ''' Load in the test object file and define the function '''
        float_pointer = ctypes.POINTER(ctypes.c_float)
        self.testlib.test_blit_m.argtypes = [ctypes.c_float]
        self.testlib.test_blit_m.restype = ctypes.c_float
        self.testlib.test_blit.argtypes = [float_pointer, ctypes.c_float, ctypes.c_int]

    def run_blit(self, freq: float, num_samples: int) -> np.ndarray:
        ''' wrapper around blit test function, generates its own co/sines '''
        out = np.zeros(num_samples, dtype=np.single)
        p_out = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        self.testlib.test_blit(p_out, ctypes.c_float(freq/sampling_frequency), len(out))
        return out

    def run_bp_blit(self, freq: float, num_samples: int) -> np.ndarray:
        ''' wrapper around bpblit test function, generates its own co/sines '''
        out = np.zeros(num_samples, dtype=np.single)
        p_out = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        self.testlib.test_bp_blit(p_out, ctypes.c_float(freq/sampling_frequency), len(out))
        return out

    def run_blit_m(self, freqs: list) -> list:
        ''' Wrapper around msinc function '''
        return [self.testlib.test_blit_m(ctypes.c_float(f/sampling_frequency)) for f in freqs]


class TestBlit(unittest.TestCase, BlitInterface):
    ''' Test class for BLIT '''
    debug = False

    def test_blit_m(self):
        ''' Test m calculation for blit '''
        freqs = np.arange(10, 16000, 10)
        ref_ratio = 2*np.trunc(0.4*sampling_frequency/freqs) + 1
        calc_ratio = self.run_blit_m(freqs)

        error = ref_ratio-calc_ratio

        if self.debug:
            _, ax1 = plt.subplots()
            ax1.plot(freqs, calc_ratio, label='Calculated')
            ax1.plot(freqs, ref_ratio, ls=':', label='Reference')
            ax1.grid()
            ax1.set_ylabel('Output')
            ax1.set_xlabel('Frequency')
            ax1.set_title('blit_m')
            ax1.legend()

            _, ax2 = plt.subplots()
            ax2.plot(freqs,error)
            ax2.grid()
            ax2.set_ylabel('Error')
            ax2.set_xlabel('Frequency')
            ax2.set_title('Error')

            plt.show()

        self.assertEqual(np.median(error), 0)
        self.assertLessEqual(np.max(abs(error)), 2)

    def test_blit_freq(self):
        ''' Test blit frequencies'''
        num_samples = 2**14
        test_freqs = 440*2**((np.arange(21, 109, 4)-69)/12)
        for gen, ratio in [(self.run_blit, 1),
                           (self.run_bp_blit, 2)]:
            for freq in test_freqs:
                vector = gen(freq, num_samples)
                time = np.arange(num_samples)/sampling_frequency
                fdomain = 20*np.log10(np.abs(np.fft.rfft(vector*sig.windows.hann(num_samples))/(num_samples**0.5)))
                freqs = np.arange(1+num_samples//2)*sampling_frequency/num_samples
                max_mag = np.max(fdomain)
                peaks, _  = sig.find_peaks(fdomain, height=max_mag-60)
                spacing = np.diff(freqs[peaks])
                mean_spacing = np.mean(spacing)

                if self.debug:
                    _, axt = plt.subplots()
                    axt.plot(time, vector)
                    axt.grid(True)
                    axt.set_xlabel('Time (s)')
                    axt.set_ylabel('Magnitude')
                    axt.set_title(f'BLIT (time domain) ({freq:.2f} Hz)')

                    _, axf = plt.subplots()
                    axf.plot(freqs, fdomain-max_mag)
                    axf.scatter(freqs[peaks], fdomain[peaks]-max_mag, c='tab:green', marker='x', label='peaks')
                    axf.grid(True)
                    axf.legend()
                    axf.set_xlabel('Frequency')
                    axf.set_ylabel('Magnitude (dB)')
                    axf.set_title(f'BLIT (frequency domain) ({freq} Hz)')

                    _, axh = plt.subplots()
                    axh.hist(spacing)
                    axh.axvline(mean_spacing, c='k', label='Mean Frequency')
                    axh.axvline(ratio*freq, c='k',ls=':', label='Target Frequency')
                    axh.set_xlabel('Frequency (Hz)')
                    axh.set_title(f'BLIT Frequency Spacing Histogram ({freq} Hz)')
                    axh.legend()
                    axh.grid(True)

                    plt.show()
                resolution = sampling_frequency/num_samples
                self.assertAlmostEqual(freq, freqs[peaks[0]], delta=resolution, msg='BLIT fundamental frequency')
                self.assertAlmostEqual(ratio*freq, mean_spacing, delta=0.01*freq, msg='BLIT harmonic spacing equal to target')


    def test_blit_amp(self):
        ''' Check the amplitude across frequencies '''
        def get_mag(frequency: float, num_samples: int)->float:
            vector = self.run_blit(frequency, num_samples)
            return np.mean(vector**2)**0.5

        samples = 2**12
        test_freqs = 440*2**((np.arange(21, 109, 4)-69)/12)
        amps = np.array([get_mag(f, samples) for f in test_freqs])

        if self.debug:
            _, ax = plt.subplots()
            ax.plot(np.log(test_freqs), np.log(amps))
            ax.plot(np.log(test_freqs), 0.5*np.log(test_freqs))
            ax.set_xlabel('Frequency')
            ax.set_ylabel('Amplitude')
            ax.set_title('Average Amplitude over Frequency Range')
            ax.grid(True)
            plt.show()


def main():
    ''' For Debugging/Testing '''
    blit_test = TestBlit()
    blit_test.debug = True
    blit_test.test_blit_m()
    blit_test.test_blit_freq()
    blit_test.test_blit_amp()

if __name__=='__main__':
    main()
