''' Tests for filters
    copyright Maximilian Cornwell 2024 '''
import ctypes
import unittest

from test.constants import sampling_frequency

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sig


DFI = 0
DFII = 1
TDFI = 2
TDFII = 3
BIQUAD = 4


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
        self.testlib.test_lowpass.argtypes = [ctypes.c_float, ctypes.c_float,
                                              ctypes.c_uint,
                                              float_pointer, float_pointer]
        self.testlib.test_highpass.argtypes = [ctypes.c_float, ctypes.c_float,
                                               ctypes.c_uint,
                                               float_pointer, float_pointer]

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

    def run_lp(self, freq: float, q: float, samples_in: np.ndarray) -> np.ndarray:
        ''' Run the biquad in lowpass configuration '''
        io_length = len(samples_in)
        p_float = ctypes.POINTER(ctypes.c_float)
        samples_in = np.array(samples_in, dtype=np.single)
        samples_in_p = samples_in.ctypes.data_as(p_float)
        samples_out = np.empty(io_length, dtype=np.single)
        samples_out_p = samples_out.ctypes.data_as(p_float)
        self.testlib.test_lowpass(freq, q, io_length, samples_in_p, samples_out_p)
        return samples_out

    def run_hp(self, freq: float, q: float, samples_in: np.ndarray) -> np.ndarray:
        ''' Run the biquad in highpass configuration '''
        io_length = len(samples_in)
        p_float = ctypes.POINTER(ctypes.c_float)
        samples_in = np.array(samples_in, dtype=np.single)
        samples_in_p = samples_in.ctypes.data_as(p_float)
        samples_out = np.empty(io_length, dtype=np.single)
        samples_out_p = samples_out.ctypes.data_as(p_float)
        self.testlib.test_highpass(freq, q, io_length, samples_in_p, samples_out_p)
        return samples_out


class TestFilter(FilterInterface, unittest.TestCase):
    ''' Tests for filter implementations '''
    debug = False

    def test_response(self):
        ''' Check that response to white noise matches scipy filter implementation '''
        n = 128*16
        input_sig = np.random.default_rng(1234).normal(0, 0.5, n)

        # for filter_type in [DFI, DFII, TDFI, TDFII, BIQUAD]:
        for filter_type in [BIQUAD]:
            for a, b in ([([1, 0], [1, 0]),
                          ([1, 0], [0, 1]),
                          ([1, 0, 0], [0, 0, 1]),
                          ([1, 0, 0, 0], [0, 0, 0, 1]),
                          ([1, 0.5], [1, 0]),
                          ([1, 0, 0.5], [1, 0, 0]),
                          ([1, 0, 0, 0.5], [1, 0, 0, 0]),
                        ]):
                with self.subTest(f'{filter_type=}, {a=}, {b=}'):
                    if filter_type == BIQUAD:
                        b = np.array(b)
                        b.resize(3)
                        a = np.array(a)
                        a.resize(3)
                    ref = sig.lfilter(b, a, input_sig)
                    out = self.run_filter(b, a, input_sig, filter_type=filter_type)
                    if self.debug:
                        error = ref - out
                        fig, ax = plt.subplots()
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
                        plt.close(fig)
                    np.testing.assert_allclose(ref, out, atol=2**-23)

    def test_biquads(self):
        N = 128*2**6
        input_sig = np.zeros(N)
        input_sig[0] = 1
        freqs, p_impulse = sig.periodogram(input_sig, sampling_frequency, detrend=None)
        for f in [100, 500, 1000, 5000, 10000, 20000]:
            for q in [0.5, 2**0.5, 1, 5, 10, 20]:
                for ftype, filt in [('lp', self.run_lp), ('hp', self.run_hp)]:
                    output_sig = filt(f, q, input_sig)
                    _, p_xx = sig.periodogram(output_sig, sampling_frequency, detrend=None)
                    h = 20*np.log10(p_xx/p_impulse)
                    if self.debug:
                        fig_t, [ax_t, ax_f] = plt.subplots(2, 1)
                        ax_t.plot(np.arange(N)/sampling_frequency, output_sig, label=ftype)
                        ax_f.semilogx(freqs, h, label=ftype)
                    with self.subTest(f'{ftype}, {f=}, {q=:2f}'):
                        if self.debug:
                            ax_t.grid(True)
                            ax_f.grid(True)
                            ax_t.set_xlabel('Time (s)')
                            ax_f.set_xlabel('Frequency (Hz)')
                            ax_t.set_title(f'{f=}, {q=}')
                            if ftype == 'lp':
                                f_passpand = [0, f/10]
                                ax_f.fill_between(f_passpand, -3, 3, color='g', alpha=0.3)
                                if f < 10*sampling_frequency:
                                    x = -80*np.log10(freqs[freqs>10*f]/f) # slope should be -80 db/decade (?)
                                    ax_f.fill_between(freqs[freqs>10*f], x+3, -100, color='g', alpha=0.3)
                            if ftype == 'hp':
                                x = 80*np.log10(freqs[freqs<f/10]/f) # slope should be 80 db/decade (?)
                                ax_f.fill_between(freqs[freqs<f/10], x+3, -100, color='g', alpha=0.3)
                                if 10*f < sampling_frequency:
                                    f_passpand = [10*f, sampling_frequency]
                                    ax_f.fill_between(f_passpand, -3, 3, color='g', alpha=0.3)
                            ax_f.set_xlim(left=20)
                            ax_f.set_ylim(bottom=-100)
                            ax_t.set_title(f'{ftype}, {f=}, {q=:.2f}')
                            plt.show()
                            plt.close(fig_t)
                        if ftype == 'lp':
                            np.testing.assert_allclose(h[freqs<f/10], 0, atol=3)
                            if f/10 > sampling_frequency:
                                x = -80*np.log10(freqs[freqs>10*f]/f) # slope should be -80 db/decade (?)
                                np.testing.assert_array_less(h[freqs>10*f], x+3, err_msg=f'lp {q=}, {f=}')
                        if ftype == 'hp':
                            x = 80*np.log10(freqs[freqs<f/10]/f) # slope should be 80 db/decade (?)
                            np.testing.assert_array_less(h[freqs<f/10][2:], x[2:]+3, err_msg=f'hp {q=}, {f=}') # ignore dc
                            if 10*f < sampling_frequency:
                                np.testing.assert_allclose(h[freqs>10*f], 0, atol=3)




def main():
    ''' For Debugging/Testing '''
    filter_test = TestFilter()
    filter_test.setUp()
    filter_test.debug = True
    filter_test.test_response()
    filter_test.test_biquads()

if __name__=='__main__':
    main()
