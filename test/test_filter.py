''' Tests for filters
    copyright Maximilian Cornwell 2024 '''
import ctypes
import unittest

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sig

DFI = 0
DFII = 1
TDFI = 2
TDFII = 3


class FilterInterface:
    ''' Interface class for filter interfaces '''
    testlib = ctypes.CDLL('test.so')

    def setUp(self):
        ''' Load in the test object file and define the function '''
        float_pointer = ctypes.POINTER(ctypes.c_float)
        # order, memory, a, b, ioLength, input, output
        self.testlib.test_filter.argtypes = [ctypes.c_uint, ctypes.c_uint,
                                             float_pointer, float_pointer, float_pointer,
                                             ctypes.c_uint, float_pointer, float_pointer]

    def run_filter(self, b: np.ndarray, a: np.ndarray, samples_in: np.ndarray, filter_type=DFI) -> np.ndarray:
        ''' Run the filter '''
        p_float = ctypes.POINTER(ctypes.c_float)
        order = max(len(b), len(a)) - 1
        b = np.pad(b, (0, order + 1 - len(b)))
        a = np.pad(a, (0, order + 1 - len(a)))
        b_p = np.array(b, dtype=np.single).ctypes.data_as(p_float)
        a_p = np.array(a, dtype=np.single).ctypes.data_as(p_float)
        io_length = len(samples_in)
        samples_in = np.array(samples_in, dtype=np.single)
        samples_in_p = samples_in.ctypes.data_as(p_float)
        memory = np.empty(2*order, dtype=np.single) if filter_type in [DFI, TDFI] else np.empty(order, dtype=np.single)
        memory_p = memory.ctypes.data_as(p_float)
        samples_out = np.empty(io_length, dtype=np.single)
        samples_out_p = samples_out.ctypes.data_as(p_float)
        self.testlib.test_filter(filter_type, order, memory_p, b_p, a_p, io_length, samples_in_p, samples_out_p)
        return samples_out


class TestFilter(FilterInterface, unittest.TestCase):
    ''' Tests for filter implementations '''
    debug = False

    def test_response(self):
        ''' Check that response to white noise matches scipy filter implementation '''
        n = 128
        input_sig = np.random.default_rng(1234).normal(0, 0.5, n)
        # input_sig = np.zeros(16)
        # input_sig[0] = 1

        # for filter_type in [DFI, DFII, TDFI, TDFII]:
        for filter_type in [TDFII]:
            for a, b in ([([1, 0], [1, 0]),
                          ([1, 0], [0, 1]),
                          ([1, 0, 0], [0, 0, 1]),
                          ([1, 0, 0, 0], [0, 0, 0, 1]),
                          ([1, 0.5], [1, 0]),
                          ([1, 0, 0.5], [1, 0, 0]),
                          ([1, 0, 0, 0.5], [1, 0, 0, 0]),
                        ]):
                ref = sig.lfilter(b, a, input_sig)
                out = self.run_filter(b, a, input_sig, filter_type=filter_type)
                if self.debug:
                    error = ref - out
                    _, ax = plt.subplots()
                    ax.plot(input_sig, ls=':', label='input')
                    ax.plot(ref, ls=':', label='reference')
                    ax.plot(out, ls=':', label='output')
                    ax.plot(error, ls=':', label='error')
                    ax.plot()
                    ax.grid(True)
                    ax.legend()
                    ax.set_ylabel('Magnitude')
                    ax.set_xlabel('Time (samples)')
                    ax.set_title(f'{b=}, {a=} {filter_type=}')
                    plt.show()
                np.testing.assert_allclose(ref, out, atol=2**-23)


def main():
    ''' For Debugging/Testing '''
    filter_test = TestFilter()
    filter_test.setUp()
    filter_test.debug = True
    filter_test.test_response()

if __name__=='__main__':
    main()
