''' Tests for Band limited impulse train functions
    copyright Maximilian Cornwell 2023 '''
import ctypes
import unittest
import matplotlib.pyplot as plt
import numpy as np

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
        ''' wrapper around msinc function, generates its own co/sines '''
        out = np.zeros(num_samples, dtype=np.single)
        p_out = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        self.testlib.test_blit(p_out, ctypes.c_float(freq/sampling_frequency), len(out))
        return out

    def run_blit_m(self, freqs: list) -> list:
        ''' Wrapper around msinc function '''
        return [self.testlib.test_blit_m(ctypes.c_float(f/sampling_frequency)) for f in freqs]


class TestBlit(unittest.TestCase, BlitInterface):
    debug = False

    def test_blit_m(self):
        freqs = np.arange(10, 16000, 10)
        ref_ratio = 2*np.trunc(0.5*sampling_frequency/freqs) + 1
        calc_ratio = self.run_blit_m(freqs)

        error = ref_ratio-calc_ratio

        if self.debug:
            _, ax1 = plt.subplots()
            ax1.plot(calc_ratio, label='Calculated')
            ax1.plot(ref_ratio, ls=':', label='Reference')
            ax1.grid()
            ax1.set_ylabel('Output')
            ax1.set_title('blit_m')
            ax1.legend()

            _, ax2 = plt.subplots()
            ax2.plot(error)
            ax2.grid()
            ax2.set_ylabel('Output')
            ax2.set_title('Error')

            plt.show()

        self.assertEqual(np.median(error), 0)
        self.assertLessEqual(np.max(abs(error)), 2)

    def test_blit(self):
        num_samples = 20*block_size
        freq = 200
        vector = self.run_blit(freq, num_samples)
        time = np.arange(num_samples)/sampling_frequency

        if self.debug:
            _, ax1 = plt.subplots()
            ax1.plot(vector)
            ax1.grid(True)
            plt.show()


def main():
    ''' For Debugging/Testing '''
    blit_test = TestBlit()
    blit_test.debug = True
    blit_test.test_blit_m()
    blit_test.test_blit()

if __name__=='__main__':
    main()
