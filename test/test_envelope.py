''' Tests for envelope generator '''
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
        self.testlib.test_envelope.argtypes = [ctypes.c_float, ctypes.c_float,
                                               ctypes.c_float, ctypes.c_float,
                                               ctypes.c_uint, uint_pointer,
                                               ctypes.c_uint, uint_pointer,
                                               ctypes.c_uint, float_pointer]

    def run(self, a: float, d: float, s: float, r: float,
            presses: np.ndarray, releases: np.ndarray, n: int) -> np.ndarray:
        ''' Run the Envelope Generator. Output is a float'''
        p_uint = ctypes.POINTER(ctypes.c_uint)
        out = np.zeros(n, dtype=np.single)
        out_p = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        presses_p = presses.astype(np.uintc, casting='safe').ctypes.data_as(p_uint)
        releases_p = releases.astype(np.uintc, casting='safe').ctypes.data_as(p_uint)
        self.testlib.test_envelope(ctypes.c_float(a), ctypes.c_float(d),
                                    ctypes.c_float(s), ctypes.c_float(r),
                                    ctypes.c_uint(len(presses)), presses_p,
                                    ctypes.c_uint(len(releases)), releases_p,
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
                           (0.05, 0.2, -80, 0.4)
                           ]:
            with self.subTest(f'{a},{d},{s},{r}'):
                a *= self.fs
                d *= self.fs
                r *= self.fs

                expected_a_grad = abs(self.B/a) if a > 1 else self.B
                expected_d_grad = s/d if d > 1 else s
                expected_r_grad = -(self.B+s)/r if r > 1 else -(self.B+s)
                threshold = np.min(np.abs([expected_a_grad, expected_d_grad, expected_r_grad]))/3
                pressTime = int(0.1*self.fs)
                releaseTime = int(0.4*self.fs)

                vector = self.implementation.run(a, d, s, r, np.array([pressTime], dtype=np.uint32),
                                                  np.array([releaseTime], dtype=np.uint32), N)
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
                        if vector[idx+1] > -self.B:
                            sustainIdxs.append(idx)
                ntIdxs, _ = sig.find_peaks(-secondDerivative, height=threshold)
                for idx in ntIdxs:
                    if derivative[idx-2] > threshold:
                        decayIdxs.append(idx)
                    else:
                        releaseIdxs.append(idx)
                if self.debug:
                    t = np.arange(N)/self.fs
                    attack_markers = vector[attackIdxs]
                    attack_times = t[attackIdxs]
                    decay_markers = vector[decayIdxs]
                    decay_times = t[decayIdxs]
                    sustain_markers = vector[sustainIdxs]
                    sustain_times = t[sustainIdxs]
                    release_markers = vector[releaseIdxs]
                    release_times = t[releaseIdxs]

                    _, ax = plt.subplots()
                    ax.plot(t, vector)
                    ax.scatter(attack_times, attack_markers)
                    ax.scatter(decay_times, decay_markers)
                    ax.scatter(sustain_times, sustain_markers)
                    ax.scatter(release_times, release_markers)
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

                # envelope should never exceed 0 dBFS
                self.assertLessEqual(np.max(vector), 0)

                # check there was an attack
                self.assertEqual(1, len(attackIdxs))
                # check when the attack occured
                self.assertAlmostEqual(pressTime, attackIdxs[0], delta=self.blockSize)
                # check attack gradient
                for aidx, didx in zip(attackIdxs, decayIdxs):
                    # check gradient error is within 1%
                    a_grad = (vector[didx] - vector[aidx])/(didx - aidx)
                    self.assertAlmostEqual(a_grad, expected_a_grad, delta=abs(0.01*expected_a_grad))
                # check there was a decay
                self.assertEqual(1, len(decayIdxs))
                # check when the attack occured
                self.assertAlmostEqual(pressTime+int(a), decayIdxs[0], delta=self.blockSize)
                # check decay gradient
                for didx, sidx in zip(decayIdxs, sustainIdxs):
                    d_grad = (vector[sidx] - vector[didx])/(sidx - didx)
                    self.assertAlmostEqual(d_grad, expected_d_grad, delta=abs(0.01*expected_d_grad))
                # check there was a sustain
                self.assertEqual(1, len(sustainIdxs))
                # check when the sustain occured
                self.assertAlmostEqual(pressTime+int(a)+int(d), sustainIdxs[0],
                                        delta=self.blockSize)
                # check sustain level
                for sidx, ridx in zip(sustainIdxs, releaseIdxs):
                    s_max = np.max(vector[sidx:ridx])
                    self.assertLess(s_max, s+1)
                    s_min = np.min(vector[sidx:ridx])
                    self.assertGreater(s_min, s-1)
                # check there was a release
                self.assertEqual(1, len(releaseIdxs))
                # check when the release occured
                self.assertAlmostEqual(releaseTime, releaseIdxs[0], delta=self.blockSize)
                # check release gradient
                for ridx in releaseIdxs:
                    r_grad = (vector[ridx + int(r/2)] - vector[ridx])/(int(r/2))
                    self.assertAlmostEqual(r_grad, expected_r_grad, delta=abs(0.01*expected_r_grad))

    def test_double_press(self):
        ''' Check that level increases after a note is pressed '''
        N = 2*self.fs
        a, d, s, r = (0.1, 0.1, -20, 0.2)
        s_len = 0.5*self.fs
        a *= self.fs
        d *= self.fs
        r *= self.fs

        # all relative to the first
        first_press = 0.1*self.fs
        test_ids = ['Attack', 'Decay', 'Sustain', 'Release']
        second_presses = np.array([a/2, a + d/2, a + d + s_len/2, a + d + s_len + r/2])\
            + first_press
        releases = np.array([a + d + s_len, a + d + s_len + 1*self.fs]) + first_press

        for second_press, test_id in zip(second_presses, test_ids):
            with self.subTest(test_id):
                presses = np.array([first_press, second_press])
                vector = self.implementation.run(a, d, s, r, presses.astype(np.uint32),
                                                  releases.astype(np.uint32), N)
                if self.debug:
                    vector = 20*np.log10(vector)
                    t = np.arange(N)/self.fs
                    _, ax = plt.subplots()
                    ax.axvline(second_press/self.fs)
                    ax.axvline((second_press + self.blockSize)/self.fs)
                    ax.axvline((second_press - self.blockSize)/self.fs)
                    ax.plot(t, vector)
                    ax.set_xlabel('Time (s)')
                    ax.set_ylabel('Magnitude (dB)')
                    ax.set_title(f'Envelope ({a/self.fs}, {d/self.fs}, {s}, {r/self.fs})')
                    ax.grid()
                    plt.show()
                self.assertGreater(vector[int(second_press+self.blockSize)],
                                    vector[int(second_press-self.blockSize)])


def main():
    ''' For Debugging/Testing '''
    env_test = TestEnvelope()
    env_test.setUp()
    env_test.debug = True
    env_test.test_basic_envelope()
    env_test.test_double_press()

if __name__=='__main__':
    main()
