''' Interface and tests for modulator functionality '''
from test.constants import block_size, sampling_frequencies

import ctypes
import unittest
import numpy as np

import matplotlib.pyplot as plt



class ModulatorInterface:
    ''' ctypes wrapper around test shared object file'''
    testlib = ctypes.CDLL('test.so')

    def setUp(self):
        ''' Load in the test object file and define the function '''
        float_pointer = ctypes.POINTER(ctypes.c_float)
        self.testlib.test_modulator.argtypes = [ctypes.c_float, ctypes.c_float,
                                                ctypes.c_uint, float_pointer, ctypes.c_float]

    def run_mod_module(self, freq: float, ratio: float, n_samples: int, fs: float) -> np.ndarray:
        ''' Run the Modulator. Modulates a constant signal'''
        out = np.zeros(n_samples, dtype=np.single)
        out_p = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        self.testlib.test_modulator(freq, ratio, n_samples, out_p, fs)
        return out

class TestModulator(ModulatorInterface, unittest.TestCase):
    ''' test class for modulator'''
    debug = False
    tolerance = 0.01
    check_abs = False

    def run_mod(self, freq: float, ratio: float, n_samples: int, fs: float) -> np.ndarray:
        ''' Run the modulation module '''
        return self.run_mod_module(freq, ratio, n_samples, fs)

    def test_model(self):
        ''' Compare modulator performance against model '''
        n_samples = 100*block_size
        for fs in sampling_frequencies:
            time = np.arange(n_samples)/fs
            for freq in [0, 0.5, 1, 5, 10]:
                for ratio in [0, 0.25, 0.5, 0.75, 1]:
                    with self.subTest(f'f{freq}r{ratio}'):
                        vector = self.run_mod(freq, ratio, n_samples, fs)
                        expected = 1-ratio + ratio*np.cos(2*np.pi*freq*time)
                        expected = np.abs(expected) if self.check_abs else expected
                        error = expected - vector
                        if self.debug:
                            _, ax1 = plt.subplots()
                            ax1.plot(time, vector, label='vector')
                            ax1.plot(time, expected, ls=':', label='expected')
                            ax1.legend()
                            ax1.grid(True)
                            ax1.set_xlabel('Time (s)')
                            ax1.set_ylabel('Magnitude')
                            ax1.set_title(f'Modulator f={freq}, r={ratio}, {fs=}')
                            _, ax2 = plt.subplots()
                            ax2.plot(time, error)
                            ax2.fill_between(time[len(error)//10:-len(error)//10], self.tolerance, -self.tolerance, color='tab:green', alpha=0.3)
                            ax2.grid(True)
                            ax2.set_xlabel('Time (s)')
                            ax2.set_ylabel('Magnitude')
                            ax2.set_title(f'Modulator Error f={freq}, r={ratio}, {fs=}')
                            plt.show()
                        error = error[len(error)//10:-len(error)//10]
                        max_error = np.max(np.abs(error))
                        self.assertAlmostEqual(max_error, 0, delta=self.tolerance)



def main():
    ''' For debugging/plotting '''
    mod_test = TestModulator()
    mod_test.setUp()
    mod_test.debug = True
    mod_test.test_model()

if __name__=="__main__":
    main()
