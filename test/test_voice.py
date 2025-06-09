''' Tests for voice
    copyright Maximilian Cornwell 2023  '''
import ctypes
import unittest

from test.constants import sampling_frequency, sampling_frequencies
from test.test_envelope import EnvelopeInterface
from test.test_oscillator import OscillatorInterface

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sig


generators = {'sine': 0,
              'blit': 1,
              'bp_blit': 2}

upper_frequencies = {'sine': 0.5,
                     'blit': 0.4,
                     'bp_blit': 0.2}

class VoiceInterface(EnvelopeInterface, OscillatorInterface):
    ''' Interface class for voice module '''
    generator = 'sine'

    def setUp(self):
        ''' Load in the test object file and define the function '''
        EnvelopeInterface.setUp(self)
        OscillatorInterface.setUp(self)
        float_pointer = ctypes.POINTER(ctypes.c_float)
        uint_pointer = ctypes.POINTER(ctypes.c_uint)
        # a, d,
        # s, r,
        # f, gen,
        # presses, pressNs,
        # releases, releaseNs,
        # n_samples, fs,
        # envOut
        self.testlib.test_voice.argtypes = [ctypes.c_float, ctypes.c_float,
                                               ctypes.c_float, ctypes.c_float,
                                               ctypes.c_float, ctypes.c_uint,
                                               ctypes.c_uint, uint_pointer,
                                               ctypes.c_uint, uint_pointer,
                                               ctypes.c_uint, ctypes.c_float,
                                               float_pointer]

    def run_voice_module(self, presses: list, releases: list, n_samples: int, fs: float) -> np.ndarray:
        ''' Run the Voice. Output is a float'''
        p_uint = ctypes.POINTER(ctypes.c_uint)
        out = np.zeros(n_samples, dtype=np.single)
        out_p = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        presses_p = np.array(presses, dtype=np.uintc).ctypes.data_as(p_uint)
        releases_p = np.array(releases, dtype=np.uintc).ctypes.data_as(p_uint)
        self.testlib.test_voice(self.attack_seconds, self.decay_seconds,
                                    self.sustain, self.release_seconds,
                                    self.freq, generators[self.generator],
                                    len(presses), presses_p,
                                    len(releases), releases_p,
                                    len(out), fs,
                                    out_p)
        return out


class TestVoice(VoiceInterface, unittest.TestCase):
    ''' Test implementations for voice module'''
    freq = 1000
    f_expected = 1000
    test_notes = [100, 400, 1000, 4000]
    env_test_note = 440
    debug = False
    freq_precision = 0.1

    def set_f(self, freq: float, fs: float):
        ''' Set the expected frequency '''
        self.freq = freq/fs
        self.f_expected = freq

    def run_voice(self, presses: list, releases: list, n_samples: int, fs: float):
        ''' Run the implementation for the test '''
        return self.run_voice_module(presses, releases, n_samples, fs)

    def test_envelope(self):
        ''' Check that the envelope is being applied '''
        for fs in sampling_frequencies:
            n_samples = 1*fs # s
            self.set_f(self.env_test_note, fs)
            for attack, decay, sustain, release in [(0.1, 0.05, -3., 0.1),
                                                    (0.01, 0.1, -20, 0.5),
                                                    (0.05, 0.2, -80, 0.4)
                                                    ]:
                with self.subTest(f'{attack},{decay},{sustain},{release}'):
                    self.set_adsr(attack, decay, sustain, release, sampling_frequency)
                    press_time = int(0.1*fs)
                    release_time = int(0.4*fs)
                    voice_vector = np.abs(sig.hilbert(self.run_voice([press_time],
                                                                    [release_time],
                                                                    n_samples, fs)))
                    env_vector = self.run_env([press_time], [release_time], n_samples, fs)
                    rms_error = (np.mean((voice_vector-env_vector)**2))**0.5
                    if self.debug:
                        _, ax1 = plt.subplots()
                        time = np.arange(n_samples)/fs
                        ax1.plot(time, voice_vector, label='voice')
                        ax1.plot(time, env_vector, label='envelope')
                        ax1.legend()
                        ax1.grid()
                        ax1.set_title('Voice and Envelope')
                        ax1.set_ylabel('Magnitude')
                        ax1.set_xlabel('Time (s)')

                        _, ax2 = plt.subplots()
                        ax2.plot(time, voice_vector-env_vector)
                        ax2.grid()
                        ax2.set_title(f'Voice/Envelope error, rmse = {rms_error}')
                        ax2.set_xlabel('Time (s)')
                        ax2.set_ylabel('Error')

                        plt.show()
                    self.assertLess(rms_error, 0.01)

    def test_frequency(self):
        ''' Check the frequency of the voice '''
        n_samples = self.calculate_length(self.freq_precision)
        self.set_adsr(0.001, 0.01, 1, 0.01, sampling_frequency)
        for gen in ['sine', 'blit', 'bp_blit']:
            self.generator = gen
            for freq in self.test_notes:
                self.set_f(freq, sampling_frequency)
                if self.f_expected < upper_frequencies[gen]*sampling_frequency:
                    with self.subTest(f'{freq}'):
                        press_time = 0
                        release_time = int(n_samples)
                        vector = self.run_voice([press_time], [release_time], n_samples, sampling_frequency)
                        f_vector = 20*np.log10(np.abs(np.fft.fft(vector))/n_samples)[:n_samples//2]
                        max_mag = np.max(f_vector)
                        peaks, _  = sig.find_peaks(f_vector, height=max_mag-30)
                        pkidx = peaks[0]
                        freqs = sampling_frequency*np.fft.fftfreq(n_samples)[:n_samples//2]
                        f_measured = freqs[pkidx]
                        if self.debug:
                            _, ax1 = plt.subplots()
                            time = np.arange(n_samples)/sampling_frequency
                            ax1.plot(time, vector)
                            ax1.grid()
                            ax1.set_title(f'Output f={self.f_expected:.2f}')
                            ax1.set_ylabel('Magnitude')
                            ax1.set_xlabel('Time (s)')

                            _, ax2 = plt.subplots()
                            ax2.plot(freqs, f_vector, label='Frequency Response')
                            ax2.scatter(freqs[pkidx], f_vector[pkidx], label='Peak')
                            ax2.legend()
                            ax2.set_xlabel('Frequency (Hz)')
                            ax2.set_ylabel('Magnitude')
                            ax2.set_title(f'Target: {self.f_expected:.2f}, Measured: {f_measured:.2f}')
                            ax2.grid()
                            plt.show()
                        self.assertAlmostEqual(f_measured,
                                               self.f_expected,
                                               delta=self.freq_precision)


def main():
    ''' For Debugging/Testing '''
    voice_test = TestVoice()
    voice_test.setUp()
    # voice_test.debug = True
    voice_test.test_envelope()
    voice_test.test_frequency()

if __name__=='__main__':
    main()
