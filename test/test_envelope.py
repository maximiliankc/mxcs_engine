import ctypes
import unittest
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sig

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
        s = 0.75 # magnitude
        r = 0.1*self.fs # s
        vector = self.implementation.run(a, d, s, r, np.array([int(0.1*self.fs)], dtype=np.uint32), np.array([int(0.4*self.fs)], dtype=np.uint32), N)
        # detect start time
        # on press is the only time the note should start increasing
        derivative = np.diff(vector, prepend=[0])
        secondDerivative = np.diff(derivative, prepend=[0])
        threshold = max(derivative)/10
        attackIdxs = []
        decayIdxs = []
        sustainIdxs = []
        releaseIdxs = []
        # find state transition point from peaks of second derivative:
        ptIdxs, _  = sig.find_peaks(secondDerivative, height=threshold)
        for idx in ptIdxs:
            if derivative[idx+1] > threshold:
                attackIdxs.append(idx)
            elif derivative[idx-1] < -threshold:
                if vector[idx+1] > 0:
                    sustainIdxs.append(idx)
        ntIdxs, _ = sig.find_peaks(-secondDerivative, height=threshold)
        for idx in ntIdxs:
            if derivative[idx-2] > threshold:
                decayIdxs.append(idx)
            else:
                releaseIdxs.append(idx)
        # check attack gradient
        for aidx, didx in zip(attackIdxs, decayIdxs):
            # check gradient error is within 1%
            a_grad = (vector[didx] - vector[aidx])/(didx - aidx)
            self.assertAlmostEqual(a_grad, 1/a, delta=abs(0.01/a))
        # check decay gradient
        for didx, sidx in zip(decayIdxs, sustainIdxs):
            d_grad = (vector[sidx] - vector[didx])/(sidx - didx)
            self.assertAlmostEqual(d_grad, (s-1)/d, delta=abs(0.01*(s-1)/d))
        # check sustain level
        for sidx, ridx in zip(sustainIdxs, releaseIdxs):
            s_max = np.max(vector[sidx:ridx])
            self.assertLess(s_max, s+0.01*s)
            s_min = np.min(vector[sidx:ridx])
            self.assertGreater(s_min, s-0.01*s)
        # check release gradient
        for ridx in releaseIdxs:
            r_grad = (vector[ridx + int(r/2)] - vector[ridx])/(int(r/2))
            self.assertAlmostEqual(r_grad, (-s)/r, delta=abs(0.01*s/r))
        if self.debug:
            t = np.arange(N)/self.fs
            attackMarkers = vector[attackIdxs]
            attackTimes = t[attackIdxs]
            decayMarkers = vector[decayIdxs]
            decayTimes = t[decayIdxs]
            sustainMarkers = vector[sustainIdxs]
            sustainTimes = t[sustainIdxs]
            releaseMarkers = vector[releaseIdxs]
            releaseTimes = t[releaseIdxs]

            _, ax = plt.subplots()
            ax.plot(t, vector)
            ax.scatter(attackTimes, attackMarkers)
            ax.scatter(decayTimes, decayMarkers)
            ax.scatter(sustainTimes, sustainMarkers)
            ax.scatter(releaseTimes, releaseMarkers)
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Magnitude')
            ax.set_title('Envelope')
            ax.grid()
            _, ax1 = plt.subplots()
            ax1.plot(t, derivative, label='First Derivative')
            ax1.plot(t, secondDerivative, label='Second Derivative')
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Magnitude')
            ax1.set_title('Derivatives')
            ax1.legend()
            ax1.grid()
            plt.show()


def main():
    ''' For Debugging/Testing '''
    env_test = TestEnvelope()
    env_test.setUp()
    env_test.debug = True
    env_test.test_basic_envelope()

if __name__=='__main__':
    main()
