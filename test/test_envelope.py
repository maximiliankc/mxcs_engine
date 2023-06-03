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
        B = 100
        for a, d, s, r in [(0.1, 0.05, 0.75, 0.1),
                           (0.01, 0.1, 0.8, 0.5),
                           (0.2, 0.3, 0.1, 0.4)
                           ]:
            a *= self.fs
            d *= self.fs
            r *= self.fs

            expectedAGrad = abs(B/a) if a > 1 else B
            expectedDGrad = 20*np.log10(s)/d if d > 1 else 20*np.log10(s)
            expectedRGrad = -(B+20*np.log10(s))/r if r > 1 else -(B+20*np.log10(s))
            threshold = np.min(np.abs([expectedAGrad, expectedDGrad, expectedRGrad]))/3

            a_coef = 10**(B/(20*a))
            d_coef = 10**(20*np.log10(s)/(20*d))
            r_coef = 10**(-(B+20*np.log10(s))/(20*r))

            vector = self.implementation.run(a_coef, d_coef, s, r_coef, np.array([int(0.1*self.fs)], dtype=np.uint32), np.array([int(0.4*self.fs)], dtype=np.uint32), N)
            vector = 20*np.log10(vector)
            vector[vector<-100] = -100

            # find derivates for use detecting state changes
            derivative = np.diff(vector, prepend=[-100])
            secondDerivative = np.diff(derivative, prepend=[0])
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
                    if vector[idx+1] > -B:
                        sustainIdxs.append(idx)
            ntIdxs, _ = sig.find_peaks(-secondDerivative, height=threshold)
            for idx in ntIdxs:
                if derivative[idx-2] > threshold:
                    decayIdxs.append(idx)
                else:
                    releaseIdxs.append(idx)
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
                ax.set_ylabel('Magnitude (dB)')
                ax.set_title('Envelope')
                ax.grid()
                _, ax1 = plt.subplots()
                ax1.plot(t, derivative, label='First Derivative')
                ax1.plot(t, secondDerivative, label='Second Derivative')
                ax1.set_xlabel('Time (s)')
                ax1.set_ylabel('Magnitude (dB)')
                ax1.set_title('Derivatives')
                ax1.legend()
                ax1.grid()
                plt.show()

            # check attack gradient
            for aidx, didx in zip(attackIdxs, decayIdxs):
                # check gradient error is within 1%
                aGrad = (vector[didx] - vector[aidx])/(didx - aidx)
                self.assertAlmostEqual(aGrad, expectedAGrad, delta=abs(0.01*expectedAGrad))
            # check decay gradient
            for didx, sidx in zip(decayIdxs, sustainIdxs):
                dGrad = (vector[sidx] - vector[didx])/(sidx - didx)
                self.assertAlmostEqual(dGrad, expectedDGrad, delta=abs(0.01*expectedDGrad))
            # check sustain level
            s = 20*np.log10(s) # put s in dB
            for sidx, ridx in zip(sustainIdxs, releaseIdxs):
                sMax = np.max(vector[sidx:ridx])
                self.assertLess(sMax, s+1)
                s_min = np.min(vector[sidx:ridx])
                self.assertGreater(s_min, s-1)
            # check release gradient
            for ridx in releaseIdxs:
                r_grad = (vector[ridx + int(r/2)] - vector[ridx])/(int(r/2))
                self.assertAlmostEqual(r_grad, expectedRGrad, delta=abs(0.01*expectedRGrad))


def main():
    ''' For Debugging/Testing '''
    env_test = TestEnvelope()
    env_test.setUp()
    env_test.debug = True
    env_test.test_basic_envelope()

if __name__=='__main__':
    main()
