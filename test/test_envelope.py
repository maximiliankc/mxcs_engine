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
    ''' Test for envelope generator '''
    debug = False
    fs = 48000 # Hz
    B = 100
    blockSize = 16

    def setUp(self) -> None:
        self.implementation = EnvelopeInterface()

    def test_basic_envelope(self):
        ''' Tests a basic single envelope '''
        N = 1*self.fs # s
        for a, d, s, r in [(0.1, 0.05, -3., 0.1),
                           (0.01, 0.1, -20, 0.5),
                           (0.2, 0.3, -80, 0.4)
                           ]:
            a *= self.fs
            d *= self.fs
            r *= self.fs

            expectedAGrad = abs(self.B/a) if a > 1 else self.B
            expectedDGrad = s/d if d > 1 else s
            expectedRGrad = -(self.B+s)/r if r > 1 else -(self.B+s)
            threshold = np.min(np.abs([expectedAGrad, expectedDGrad, expectedRGrad]))/3

            vector = self.implementation.run(a, d, s, r, np.array([int(0.1*self.fs)], dtype=np.uint32), np.array([int(0.4*self.fs)], dtype=np.uint32), N)
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
                ax.set_title(f'Envelope ({a/self.fs}, {d/self.fs}, {s}, {r/self.fs})')
                ax.grid()
                _, ax1 = plt.subplots()
                ax1.plot(t, derivative, label='First Derivative')
                ax1.plot(t, secondDerivative, label='Second Derivative')
                ax1.set_xlabel('Time (s)')
                ax1.set_ylabel('Magnitude (dB)')
                ax1.set_title(f'Derivatives ({a/self.fs}, {d/self.fs}, {s}, {r/self.fs})')
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
            for sidx, ridx in zip(sustainIdxs, releaseIdxs):
                sMax = np.max(vector[sidx:ridx])
                self.assertLess(sMax, s+1)
                s_min = np.min(vector[sidx:ridx])
                self.assertGreater(s_min, s-1)
            # check release gradient
            for ridx in releaseIdxs:
                r_grad = (vector[ridx + int(r/2)] - vector[ridx])/(int(r/2))
                self.assertAlmostEqual(r_grad, expectedRGrad, delta=abs(0.01*expectedRGrad))

    def test_double_press(self):
        ''' Check that level increases after a note is pressed '''
        N = 2*self.fs
        a, d, s, r = (0.1, 0.1, -20, 0.2)
        s_len = 0.5*self.fs
        a *= self.fs
        d *= self.fs
        r *= self.fs

        # all relative to the first
        # during attack, during decay, during sustain, during release
        firstPress = 0.1*self.fs
        secondPresses = np.array([a/2, a + d/2, a + d + s_len/2, a + d + s_len + r/2]) + firstPress
        releases = np.array([a + d + s_len, a + d + s_len + 1*self.fs]) + firstPress

        for secondPress in secondPresses:
            presses = np.array([firstPress, secondPress])
            vector = self.implementation.run(a, d, s, r, presses.astype(np.uint32), releases.astype(np.uint32), N)
            self.assertGreater(vector[int(secondPress+self.blockSize)],vector[int(secondPress-self.blockSize)])
            if self.debug:
                vector = 20*np.log10(vector)
                t = np.arange(N)/self.fs
                _, ax = plt.subplots()
                ax.axvline(secondPress/self.fs)
                ax.axvline((secondPress + self.blockSize)/self.fs)
                ax.axvline((secondPress - self.blockSize)/self.fs)
                ax.plot(t, vector)
                ax.set_xlabel('Time (s)')
                ax.set_ylabel('Magnitude (dB)')
                ax.set_title(f'Envelope ({a/self.fs}, {d/self.fs}, {s}, {r/self.fs})')
                ax.grid()
                plt.show()

def main():
    ''' For Debugging/Testing '''
    env_test = TestEnvelope()
    env_test.setUp()
    env_test.debug = True
    # env_test.test_basic_envelope()
    env_test.test_double_press()

if __name__=='__main__':
    main()
