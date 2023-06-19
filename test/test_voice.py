''' Tests for voice '''
import ctypes
import unittest
import numpy as np
import scipy.signal as sig
from .test_envelope import EnvelopeTools, EnvelopeInterface


class VoiceInterface:
    ''' ctypes wrapper around test shared object file'''
    def __init__(self):
        ''' Load in the test object file and define the function '''
        self.testlib = ctypes.CDLL('test.so')
        float_pointer = ctypes.POINTER(ctypes.c_float)
        uint_pointer = ctypes.POINTER(ctypes.c_uint)
        # a, d, s, r, f, presses, pressNs, releases, releaseNs, n, envOut
        self.testlib.test_voice.argtypes = [ctypes.c_float, ctypes.c_float,
                                               ctypes.c_float, ctypes.c_float,
                                               ctypes.c_float,
                                               ctypes.c_uint, uint_pointer,
                                               ctypes.c_uint, uint_pointer,
                                               ctypes.c_uint, float_pointer]

    def run(self, a: float, d: float, s: float, r: float, f: float,
            presses: np.ndarray, releases: np.ndarray, n: int) -> np.ndarray:
        ''' Run the Voice. Output is a float'''
        p_uint = ctypes.POINTER(ctypes.c_uint)
        out = np.zeros(n, dtype=np.single)
        out_p = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        presses_p = presses.astype(np.uintc, casting='safe').ctypes.data_as(p_uint)
        releases_p = releases.astype(np.uintc, casting='safe').ctypes.data_as(p_uint)
        self.testlib.test_voice(ctypes.c_float(a), ctypes.c_float(d),
                                    ctypes.c_float(s), ctypes.c_float(r),
                                    ctypes.c_float(f),
                                    ctypes.c_uint(len(presses)), presses_p,
                                    ctypes.c_uint(len(releases)), releases_p,
                                    ctypes.c_uint(len(out)), out_p)
        return out

class TestVoice(unittest.TestCase, EnvelopeTools):
    f = 1000
    fs = 48000

    def run_v_implementation(self, presses, releases, N):
        ''' Run the implementation '''
        f = self.f/self.fs
        vector = self.implementation.run(self.a, self.d, self.s, self.r, f,
                                          presses.astype(np.uint32), releases.astype(np.uint32), N)
        vector = sig.hilbert(vector)
        return np.abs(vector)

    def setUp(self) -> None:
        self.v_implementation = VoiceInterface()
        self.e_implementation = EnvelopeInterface()

    def test_envelope(self):
        pass

def main():
    ''' For Debugging/Testing '''
    voice_test = TestVoice()
    voice_test.setUp()
    voice_test.debug = True
    voice_test.test_envelope()

if __name__=='__main__':
    main()