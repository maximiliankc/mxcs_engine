''' Tests for envelope generator
    copyright Maximilian Cornwell 2023  '''
import ctypes
import unittest
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sig
from .constants import sampling_frequency, block_size

class EnvelopeInterface:
    ''' ctypes wrapper around test function and tools for interacting with it '''
    base = 100
    attack = 0
    decay = 0
    sustain = 0
    release = 0
    testlib = ctypes.CDLL('test.so')

    def __init__(self):
        ''' Load in the test object file and define the function '''
        float_pointer = ctypes.POINTER(ctypes.c_float)
        uint_pointer = ctypes.POINTER(ctypes.c_uint)
        # attack, decay, sustain, release, presses, pressNs, releases, releaseNs, n, envOut
        self.testlib.test_envelope.argtypes = [ctypes.c_float, ctypes.c_float,
                                               ctypes.c_float, ctypes.c_float,
                                               ctypes.c_uint, uint_pointer,
                                               ctypes.c_uint, uint_pointer,
                                               ctypes.c_uint, float_pointer]

    def run_env(self, presses: list, releases: list, n_samples: int) -> np.ndarray:
        ''' Run the Envelope Generator. Output is attack float'''
        p_uint = ctypes.POINTER(ctypes.c_uint)
        out = np.zeros(n_samples, dtype=np.single)
        out_p = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        presses_p = np.array(presses, dtype=np.uintc).ctypes.data_as(p_uint)
        releases_p = np.array(releases, dtype=np.uintc).ctypes.data_as(p_uint)
        self.testlib.test_envelope(ctypes.c_float(self.attack), ctypes.c_float(self.decay),
                                    ctypes.c_float(self.sustain), ctypes.c_float(self.release),
                                    ctypes.c_uint(len(presses)), presses_p,
                                    ctypes.c_uint(len(releases)), releases_p,
                                    ctypes.c_uint(len(out)), out_p)
        return out

    def set_adsr(self, attack: float, decay: float, sustain: float, release: float):
        ''' Configure adsr values '''
        self.attack = attack*sampling_frequency
        self.decay = decay*sampling_frequency
        self.sustain = sustain
        self.release = release*sampling_frequency

    def calculate_gradients(self):
        ''' Calculate gradients from adsr values '''
        a_grad = abs(self.base/self.attack) if self.attack > 1 else self.base
        d_grad = self.sustain/self.decay if self.decay > 1 else self.sustain
        r_grad = -(self.base+self.sustain)/self.release if self.release > 1\
            else -(self.base+self.sustain)
        return a_grad, d_grad, r_grad


class TestEnvelope(unittest.TestCase, EnvelopeInterface):
    ''' Test for envelope generator '''
    debug = False

    def check_attack(self, vector, attack_idxs, decay_idxs, press_time):
        ''' Do checks for attack. Vector is data, idxs indexes where events were detected.
            press time is when press occured '''
        exp_a_grad, _, _ = self.calculate_gradients()
        # check there was an attack
        self.assertEqual(1, len(attack_idxs))
        # check when the attack occured
        self.assertAlmostEqual(press_time, attack_idxs[0], delta=block_size)
        # check attack gradient
        for aidx, didx in zip(attack_idxs, decay_idxs):
            # check gradient error is within 1%
            a_grad = (vector[didx] - vector[aidx])/(didx - aidx)
            self.assertAlmostEqual(a_grad, exp_a_grad, delta=abs(0.01*exp_a_grad))

    def check_decay(self, vector, decay_idxs, sustain_idxs, press_time):
        ''' Do checks for decay. Vector is data, idxs indexes where events were detected.
            press time is when press occured '''
        _, exp_d_grad, _ = self.calculate_gradients()
        # check there was attack decay
        self.assertEqual(1, len(decay_idxs))
        # check when the attack occured
        self.assertAlmostEqual(press_time+int(self.attack), decay_idxs[0], delta=block_size)
        # check decay gradient
        for didx, sidx in zip(decay_idxs, sustain_idxs):
            d_grad = (vector[sidx] - vector[didx])/(sidx - didx)
            self.assertAlmostEqual(d_grad, exp_d_grad, delta=abs(0.01*exp_d_grad))

    def check_sustain(self, vector, sustain_idxs, release_idxs, press_time):
        ''' Do checks for decay. Vector is data, idxs indexes where events were detected.
            press time is when press occured '''
        # check there was attack sustain
        self.assertEqual(1, len(sustain_idxs))
        # check when the sustain occured
        self.assertAlmostEqual(press_time+int(self.attack)+int(self.decay), sustain_idxs[0],
                                delta=block_size)
        # check sustain level
        for sidx, ridx in zip(sustain_idxs, release_idxs):
            s_max = np.max(vector[sidx:ridx])
            self.assertLess(s_max, self.sustain+1)
            s_min = np.min(vector[sidx:ridx])
            self.assertGreater(s_min, self.sustain-1)

    def check_release(self, vector, release_idxs, release_time):
        ''' Do checks for decay. Vector is data, idxs indexes where events were detected.
            Release time is when release occured '''
        _, _, exp_r_grad = self.calculate_gradients()
        # check there was attack release
        self.assertEqual(1, len(release_idxs))
        # check when the release occured
        self.assertAlmostEqual(release_time, release_idxs[0], delta=block_size)
        # check release gradient
        for ridx in release_idxs:
            r_grad = (vector[ridx + int(self.release/2)] - vector[ridx])/(int(self.release/2))
            self.assertAlmostEqual(r_grad, exp_r_grad, delta=abs(0.01*exp_r_grad))

    def test_basic_envelope(self):
        ''' Tests attack basic single envelope '''
        n_samples = 1*sampling_frequency # sustain
        for attack, decay, sustain, release in [(0.1, 0.05, -3., 0.1),
                           (0.01, 0.1, -20, 0.5),
                           (0.05, 0.2, -80, 0.4)
                           ]:
            with self.subTest(f'{attack},{decay},{sustain},{release}'):
                self.set_adsr(attack, decay, sustain, release)
                exp_a_grad, exp_d_grad, exp_r_grad = self.calculate_gradients()
                threshold = np.min(np.abs([exp_a_grad, exp_d_grad, exp_r_grad]))/3
                press_time = int(0.1*sampling_frequency)
                release_time = int(0.4*sampling_frequency)

                vector = self.run_env([press_time], [release_time], n_samples)
                vector = 20*np.log10(vector)
                vector[vector<-100] = -100

                # find derivates for use detecting state changes
                derivative = np.diff(vector, prepend=[-100])
                second_derivative = np.diff(derivative, prepend=[0])
                attack_idxs = []
                decay_idxs = []
                sustain_idxs = []
                release_idxs = []
                # find state transition point from peaks of second derivative:
                pt_idxs, _  = sig.find_peaks(second_derivative, height=threshold)
                for idx in pt_idxs:
                    if derivative[idx+1] > threshold:
                        attack_idxs.append(idx)
                    elif derivative[idx-1] < -threshold:
                        if vector[idx+1] > -self.base:
                            sustain_idxs.append(idx)
                nt_idxs, _ = sig.find_peaks(-second_derivative, height=threshold)
                for idx in nt_idxs:
                    if derivative[idx-2] > threshold:
                        decay_idxs.append(idx)
                    else:
                        release_idxs.append(idx)
                if self.debug:
                    time = np.arange(n_samples)/sampling_frequency
                    attack_markers = vector[attack_idxs]
                    attack_times = time[attack_idxs]
                    decay_markers = vector[decay_idxs]
                    decay_times = time[decay_idxs]
                    sustain_markers = vector[sustain_idxs]
                    sustain_times = time[sustain_idxs]
                    release_markers = vector[release_idxs]
                    release_times = time[release_idxs]

                    _, ax1 = plt.subplots()
                    ax1.plot(time, vector)
                    ax1.scatter(attack_times, attack_markers)
                    ax1.scatter(decay_times, decay_markers)
                    ax1.scatter(sustain_times, sustain_markers)
                    ax1.scatter(release_times, release_markers)
                    ax1.set_xlabel('Time (sustain)')
                    ax1.set_ylabel('Magnitude (dB)')
                    ax1.set_title(f'Envelope ({attack}, {decay}, {sustain}, {release})')
                    ax1.grid()
                    _, ax2 = plt.subplots()
                    ax2.plot(time, derivative, label='First Derivative')
                    ax2.plot(time, second_derivative, label='Second Derivative')
                    ax2.set_xlabel('Time (sustain)')
                    ax2.set_ylabel('Magnitude (dB)')
                    ax2.set_title(f'Derivatives ({attack}, {decay}, {sustain}, {release})')
                    ax2.legend()
                    ax2.grid()
                    plt.show()

                # envelope should never exceed 0 dBFS
                self.assertLessEqual(np.max(vector), 0)

                self.check_attack(vector, attack_idxs, decay_idxs, press_time)
                self.check_decay(vector, decay_idxs, sustain_idxs, press_time)
                self.check_sustain(vector, sustain_idxs, release_idxs, press_time)
                self.check_release(vector, release_idxs, release_time)

    def test_double_press(self):
        ''' Check that there is an attack when a double press occurs '''
        n_samples = 2*sampling_frequency
        attack, decay, sustain, release = (0.1, 0.1, -20, 0.2)
        s_len = 0.5*sampling_frequency
        self.set_adsr(attack, decay, sustain, release)
        # all relative to the first
        first_press = 0.1*sampling_frequency
        test_ids = ['Attack', 'Decay', 'Sustain', 'Release']
        second_presses = np.array([self.attack/2, self.attack + self.decay/2,
                                    self.attack + self.decay + s_len/2,
                                    self.attack + self.decay + s_len + self.release/2])\
                        + first_press
        releases = np.array([self.attack + self.decay + s_len,
                             self.attack + self.decay + s_len + 1*sampling_frequency]) + first_press

        for second_press, test_id in zip(second_presses, test_ids):
            with self.subTest(test_id):
                presses = [first_press, second_press]
                vector = self.run_env(presses, releases, n_samples)
                if self.debug:
                    vector = 20*np.log10(vector)
                    time = np.arange(n_samples)/sampling_frequency
                    _, ax1 = plt.subplots()
                    ax1.axvline(second_press/sampling_frequency)
                    ax1.axvline((second_press + block_size)/sampling_frequency)
                    ax1.axvline((second_press - block_size)/sampling_frequency)
                    ax1.plot(time, vector)
                    ax1.set_xlabel('Time (sustain)')
                    ax1.set_ylabel('Magnitude (dB)')
                    ax1.set_title(f'Envelope ({self.attack/sampling_frequency}, {self.decay/sampling_frequency}, {self.sustain}, {self.release/sampling_frequency})')
                    ax1.grid()
                    plt.show()
                press_region = vector[int(second_press-block_size):int(second_press+block_size)]
                press_minimum = np.min(press_region)
                # make sure the minima isn't at the end of the press region
                self.assertGreater(press_region[-1], press_minimum)


def main():
    ''' For Debugging/Testing '''
    env_test = TestEnvelope()
    env_test.debug = True
    # env_test.test_basic_envelope()
    env_test.test_double_press()

if __name__=='__main__':
    main()
