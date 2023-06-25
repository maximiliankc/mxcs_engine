''' Tests for envelope generator '''
import ctypes
import unittest
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sig

class EnvelopeInterface:
    ''' ctypes wrapper around test function and tools for interacting with it'''
    blockSize = 16
    fs = 48000 # Hz
    B = 100
    a = 0
    d = 0
    s = 0
    r = 0
    testlib = ctypes.CDLL('test.so')

    def __init__(self):
        ''' Load in the test object file and define the function '''
        float_pointer = ctypes.POINTER(ctypes.c_float)
        uint_pointer = ctypes.POINTER(ctypes.c_uint)
        # a, d, s, r, presses, pressNs, releases, releaseNs, n, envOut
        self.testlib.test_envelope.argtypes = [ctypes.c_float, ctypes.c_float,
                                               ctypes.c_float, ctypes.c_float,
                                               ctypes.c_uint, uint_pointer,
                                               ctypes.c_uint, uint_pointer,
                                               ctypes.c_uint, float_pointer]

    def run_env(self, presses: list, releases: list, n: int) -> np.ndarray:
        ''' Run the Envelope Generator. Output is a float'''
        p_uint = ctypes.POINTER(ctypes.c_uint)
        out = np.zeros(n, dtype=np.single)
        out_p = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        presses_p = np.array(presses, dtype=np.uintc).ctypes.data_as(p_uint)
        releases_p = np.array(releases, dtype=np.uintc).ctypes.data_as(p_uint)
        self.testlib.test_envelope(ctypes.c_float(self.a), ctypes.c_float(self.d),
                                    ctypes.c_float(self.s), ctypes.c_float(self.r),
                                    ctypes.c_uint(len(presses)), presses_p,
                                    ctypes.c_uint(len(releases)), releases_p,
                                    ctypes.c_uint(len(out)), out_p)
        return out

    def set_adsr(self, a: float, d: float, s: float, r: float):
        ''' Configure adsr values '''
        self.a = a*self.fs
        self.d = d*self.fs
        self.s = s
        self.r = r*self.fs

    def calculate_gradients(self):
        ''' Calculate gradients from adsr values '''
        a_grad = abs(self.B/self.a) if self.a > 1 else self.B
        d_grad = self.s/self.d if self.d > 1 else self.s
        r_grad = -(self.B+self.s)/self.r if self.r > 1 else -(self.B+self.s)
        return a_grad, d_grad, r_grad


class TestEnvelope(unittest.TestCase, EnvelopeInterface):
    ''' Test for envelope generator '''
    debug = False

    def check_attack(self, vector, attackIdxs, decayIdxs, pressTime):
        exp_a_grad, _, _ = self.calculate_gradients()
        # check there was an attack
        self.assertEqual(1, len(attackIdxs))
        # check when the attack occured
        self.assertAlmostEqual(pressTime, attackIdxs[0], delta=self.blockSize)
        # check attack gradient
        for aidx, didx in zip(attackIdxs, decayIdxs):
            # check gradient error is within 1%
            a_grad = (vector[didx] - vector[aidx])/(didx - aidx)
            self.assertAlmostEqual(a_grad, exp_a_grad, delta=abs(0.01*exp_a_grad))

    def check_decay(self, vector, decayIdxs, sustainIdxs, pressTime):
        _, exp_d_grad, _ = self.calculate_gradients()
        # check there was a decay
        self.assertEqual(1, len(decayIdxs))
        # check when the attack occured
        self.assertAlmostEqual(pressTime+int(self.a), decayIdxs[0], delta=self.blockSize)
        # check decay gradient
        for didx, sidx in zip(decayIdxs, sustainIdxs):
            d_grad = (vector[sidx] - vector[didx])/(sidx - didx)
            self.assertAlmostEqual(d_grad, exp_d_grad, delta=abs(0.01*exp_d_grad))

    def check_sustain(self, vector, sustainIdxs, releaseIdxs, pressTime):
        # check there was a sustain
        self.assertEqual(1, len(sustainIdxs))
        # check when the sustain occured
        self.assertAlmostEqual(pressTime+int(self.a)+int(self.d), sustainIdxs[0],
                                delta=self.blockSize)
        # check sustain level
        for sidx, ridx in zip(sustainIdxs, releaseIdxs):
            s_max = np.max(vector[sidx:ridx])
            self.assertLess(s_max, self.s+1)
            s_min = np.min(vector[sidx:ridx])
            self.assertGreater(s_min, self.s-1)

    def check_release(self, vector, releaseIdxs, releaseTime):
        _, _, exp_r_grad = self.calculate_gradients()
        # check there was a release
        self.assertEqual(1, len(releaseIdxs))
        # check when the release occured
        self.assertAlmostEqual(releaseTime, releaseIdxs[0], delta=self.blockSize)
        # check release gradient
        for ridx in releaseIdxs:
            r_grad = (vector[ridx + int(self.r/2)] - vector[ridx])/(int(self.r/2))
            self.assertAlmostEqual(r_grad, exp_r_grad, delta=abs(0.01*exp_r_grad))

    def test_basic_envelope(self):
        ''' Tests a basic single envelope '''
        N = 1*self.fs # s
        for a, d, s, r in [(0.1, 0.05, -3., 0.1),
                           (0.01, 0.1, -20, 0.5),
                           (0.05, 0.2, -80, 0.4)
                           ]:
            with self.subTest(f'{a},{d},{s},{r}'):
                self.set_adsr(a, d, s, r)
                exp_a_grad, exp_d_grad, exp_r_grad = self.calculate_gradients()
                threshold = np.min(np.abs([exp_a_grad, exp_d_grad, exp_r_grad]))/3
                pressTime = int(0.1*self.fs)
                releaseTime = int(0.4*self.fs)

                vector = self.run_env([pressTime], [releaseTime], N)
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
                    ax.set_title(f'Envelope ({a}, {d}, {s}, {r})')
                    ax.grid()
                    _, ax1 = plt.subplots()
                    ax1.plot(t, derivative, label='First Derivative')
                    ax1.plot(t, secondDerivative, label='Second Derivative')
                    ax1.set_xlabel('Time (s)')
                    ax1.set_ylabel('Magnitude (dB)')
                    ax1.set_title(f'Derivatives ({a}, {d}, {s}, {r})')
                    ax1.legend()
                    ax1.grid()
                    plt.show()

                # envelope should never exceed 0 dBFS
                self.assertLessEqual(np.max(vector), 0)

                self.check_attack(vector, attackIdxs, decayIdxs, pressTime)
                self.check_decay(vector, decayIdxs, sustainIdxs, pressTime)
                self.check_sustain(vector, sustainIdxs, releaseIdxs, pressTime)
                self.check_release(vector, releaseIdxs, releaseTime)

    def test_double_press(self):
        ''' Check that level increases after a note is pressed '''
        N = 2*self.fs
        a, d, s, r = (0.1, 0.1, -20, 0.2)
        s_len = 0.5*self.fs
        self.set_adsr(a, d, s, r)
        # all relative to the first
        first_press = 0.1*self.fs
        test_ids = ['Attack', 'Decay', 'Sustain', 'Release']
        second_presses = np.array([self.a/2, self.a + self.d/2,
                                    self.a + self.d + s_len/2,
                                    self.a + self.d + s_len + self.r/2])\
                        + first_press
        releases = np.array([self.a + self.d + s_len,
                             self.a + self.d + s_len + 1*self.fs]) + first_press

        for second_press, test_id in zip(second_presses, test_ids):
            with self.subTest(test_id):
                presses = [first_press, second_press]
                vector = self.run_env(presses, releases, N)
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
                    ax.set_title(f'Envelope ({self.a/self.fs}, {self.d/self.fs}, {self.s}, {self.r/self.fs})')
                    ax.grid()
                    plt.show()
                self.assertGreater(vector[int(second_press+self.blockSize)],
                                    vector[int(second_press-self.blockSize)])


def main():
    ''' For Debugging/Testing '''
    env_test = TestEnvelope()
    env_test.debug = True
    env_test.test_basic_envelope()
    env_test.test_double_press()

if __name__=='__main__':
    main()
