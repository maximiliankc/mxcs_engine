import ctypes
import unittest
import matplotlib.pyplot as plt
import numpy as np

class EnvelopeInterface:
    ''' ctypes wrapper around test shared object file'''
    def __init__(self):
        ''' Load in the test object file and define the function '''
        self.testlib = ctypes.CDLL('test.so')
        float_pointer = ctypes.POINTER(ctypes.c_float)
        uint_pointer = ctypes.POINTER(ctypes.c_uint)
        # a, d, s, r, presses, pressNs, releases, releaseNs, n, envOut
        self.testlib.test_envelope.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_float,
                                               ctypes.c_uint, uint_pointer,
                                               ctypes.c_uint, uint_pointer,
                                               ctypes.c_uint, float_pointer]

    def run(self, a: float, d: float, s: float, r: float, presses: np.ndarray, releases: np.ndarray, n: int) -> np.ndarray:
        ''' Run the Envelope Generator. Output is a float'''
        out = np.zeros(n, dtype=np.single)
        out_p = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        presses_p = presses.astype(np.uintc, casting='safe').ctypes.data_as(ctypes.POINTER(ctypes.c_uint))
        releases_p = releases.astype(np.uintc, casting='safe').ctypes.data_as(ctypes.POINTER(ctypes.c_uint))
        self.testlib.test_envelope(ctypes.c_float(a), ctypes.c_float(d), ctypes.c_float(s), ctypes.c_float(r),
                                   ctypes.c_uint(len(presses)), presses_p, ctypes.c_uint(len(releases)), releases_p,
                                   ctypes.c_uint(len(out)), out_p)
        return out


class TestEnvelope(unittest.TestCase):
    ''' '''
    debug = False
    fs = 48000 # Hz

    def setUp(self) -> None:
        self.implementation = EnvelopeInterface()

    def test_basic_envelope(self):
        N = 1*self.fs # s
        a = 0.1*self.fs # s
        d = 0.05*self.fs # s
        s = 0.5*self.fs # magnitude
        r = 0.1*self.fs # s
        vector = self.implementation.run(a, d, s, r, np.array([int(0.1*self.fs)], dtype=np.uint32), np.array([int(0.4*self.fs)], dtype=np.uint32), N)
        if self.debug:
            t = np.arange(N)/self.fs
            _, ax = plt.subplots()
            ax.plot(t, vector)
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Magnitude')
            ax.set_title('Envelope')
            ax.grid('True')
            plt.show()


def main():
    ''' For Debugging/Testing '''
    env_test = TestEnvelope()
    env_test.setUp()
    env_test.debug = True
    env_test.test_basic_envelope()

if __name__=='__main__':
    main()
