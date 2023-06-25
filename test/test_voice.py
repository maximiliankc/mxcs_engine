''' Tests for voice '''
import ctypes
import unittest
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sig
from .test_envelope import EnvelopeInterface


class VoiceInterface(EnvelopeInterface):
    f = 0
    ''' ctypes wrapper around test shared object file'''
    def __init__(self):
        ''' Load in the test object file and define the function '''
        float_pointer = ctypes.POINTER(ctypes.c_float)
        uint_pointer = ctypes.POINTER(ctypes.c_uint)
        # a, d, s, r, f, presses, pressNs, releases, releaseNs, n, envOut
        self.testlib.test_voice.argtypes = [ctypes.c_float, ctypes.c_float,
                                               ctypes.c_float, ctypes.c_float,
                                               ctypes.c_float,
                                               ctypes.c_uint, uint_pointer,
                                               ctypes.c_uint, uint_pointer,
                                               ctypes.c_uint, float_pointer]

    def run_voice(self, presses: list, releases: list, n: int) -> np.ndarray:
        ''' Run the Voice. Output is a float'''
        p_uint = ctypes.POINTER(ctypes.c_uint)
        out = np.zeros(n, dtype=np.single)
        out_p = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        presses_p = np.array(presses, dtype=np.uintc).ctypes.data_as(p_uint)
        releases_p = np.array(releases, dtype=np.uintc).ctypes.data_as(p_uint)
        self.testlib.test_voice(ctypes.c_float(self.a), ctypes.c_float(self.d),
                                    ctypes.c_float(self.s), ctypes.c_float(self.r),
                                    ctypes.c_float(self.f),
                                    ctypes.c_uint(len(presses)), presses_p,
                                    ctypes.c_uint(len(releases)), releases_p,
                                    ctypes.c_uint(len(out)), out_p)
        return out

    def set_f(self, freq: float):
        self.f = freq/self.fs

class TestVoice(unittest.TestCase, VoiceInterface):
    f = 1000
    fs = 48000
    debug = False

    def test_envelope(self):
        ''' Check that the envelope is being applied '''
        N = 1*self.fs # s
        for a, d, s, r in [(0.1, 0.05, -3., 0.1),
                           (0.01, 0.1, -20, 0.5),
                           (0.05, 0.2, -80, 0.4)
                           ]:
            with self.subTest(f'{a},{d},{s},{r}'):
                self.set_adsr(a, d, s, r)
                self.set_f(440)
                press_time = int(0.1*self.fs)
                release_time = int(0.4*self.fs)
                voice_vector = np.abs(sig.hilbert(self.run_voice([press_time], [release_time], N)))
                env_vector = self.run_env([press_time], [release_time], N)
                rms_error = (np.mean((voice_vector-env_vector)**2))**0.5
                if self.debug:
                    _, ax = plt.subplots()
                    t = np.arange(N)/self.fs
                    ax.plot(t, voice_vector, label='voice')
                    ax.plot(t, env_vector, label='envelope')
                    ax.legend()
                    ax.grid()
                    ax.set_title('Voice and Envelope')
                    ax.set_ylabel('Magnitude')
                    ax.set_xlabel('Time (s)')

                    _, ax2 = plt.subplots()
                    ax2.plot(t, voice_vector-env_vector)
                    ax2.grid()
                    ax2.set_title(f'Voice/Envelope error, rmse = {rms_error}')
                    ax2.set_xlabel('Time (s)')
                    ax2.set_ylabel('Error')

                    plt.show()
                self.assertLess(rms_error, 0.01)



def main():
    ''' For Debugging/Testing '''
    voice_test = TestVoice()
    voice_test.setUp()
    voice_test.debug = True
    voice_test.test_envelope()

if __name__=='__main__':
    main()