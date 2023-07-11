''' Tests for Band limited impulse train functions
    copyright Maximilian Cornwell 2023 '''
import ctypes
import numpy as np

from .constants import sampling_frequency

class BlitInterface:
    ''' Interface for BLIT functions '''
    def __init__(self):
        ''' Load in the test object file and define the function '''
        self.testlib = ctypes.CDLL('test.so')
        self.float_pointer = ctypes.POINTER(ctypes.c_float)
        self.testlib.blit_m.argtypes = [ctypes.c_float]
        self.testlib.blit_m.restype = ctypes.c_float
        self.testlib.msinc.argtypes = [self.float_pointer, self.float_pointer,
                                        self.float_pointer, self.float_pointer,
                                        self.float_pointer, ctypes.c_int16]

    def run_msinc(self, freq: float, mod_ratio: int, num_samples: int) -> np.ndarray:
        ''' wrapper around msinc function, generates its own co/sines '''
        n = np.arange(num_samples)
        lf_sin = np.sin(np.pi*freq*n/sampling_frequency)
        lf_cos = np.cos(np.pi*freq*n/sampling_frequency)
        hf_sin = np.sin(np.pi*mod_ratio*freq*n/sampling_frequency)
        hf_cos = np.cos(np.pi*mod_ratio*freq*n/sampling_frequency)
        out = np.zeros(n)
        p_lf_sin = lf_sin.ctypes.data_as(self.float_pointer)
        p_lf_cos = lf_cos.ctypes.data_as(self.float_pointer)
        p_hf_sin = hf_sin.ctypes.data_as(self.float_pointer)
        p_hf_cos = hf_cos.ctypes.data_as(self.float_pointer)
        p_out = out.ctypes.data_as(self.float_pointer)
        self.testlib.msinc(p_out, p_lf_sin, p_lf_cos, p_hf_sin, p_hf_cos, mod_ratio)
        return p_out

    def run_blit_m(self, freqs: list) -> list:
        ''' Wrapper around msinc function '''
        return [self.testlib.msinc(f) for f in freqs]
