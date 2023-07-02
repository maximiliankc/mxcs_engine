''' Tests for voice
    copyright Maximilian Cornwell 2023  '''
import ctypes
import unittest
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sig

from .constants import sampling_frequency
from .test_envelope import EnvelopeInterface
from .test_oscillator import OscillatorInterface


class VoiceInterface(EnvelopeInterface, OscillatorInterface):
    ''' Interface class for voice module '''
    def __init__(self):
        ''' Load in the test object file and define the function '''
        super().__init__()
        float_pointer = ctypes.POINTER(ctypes.c_float)
        uint_pointer = ctypes.POINTER(ctypes.c_uint)
        # a, d, s, r, f, presses, pressNs, releases, releaseNs, n_samples, envOut
        self.testlib.test_voice.argtypes = [ctypes.c_float, ctypes.c_float,
                                               ctypes.c_float, ctypes.c_float,
                                               ctypes.c_float,
                                               ctypes.c_uint, uint_pointer,
                                               ctypes.c_uint, uint_pointer,
                                               ctypes.c_uint, float_pointer]

    def run_voice(self, presses: list, releases: list, n_samples: int) -> np.ndarray:
        ''' Run the Voice. Output is a float'''
        p_uint = ctypes.POINTER(ctypes.c_uint)
        out = np.zeros(n_samples, dtype=np.single)
        out_p = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        presses_p = np.array(presses, dtype=np.uintc).ctypes.data_as(p_uint)
        releases_p = np.array(releases, dtype=np.uintc).ctypes.data_as(p_uint)
        self.testlib.test_voice(ctypes.c_float(self.attack), ctypes.c_float(self.decay),
                                    ctypes.c_float(self.sustain), ctypes.c_float(self.release),
                                    ctypes.c_float(self.freq),
                                    ctypes.c_uint(len(presses)), presses_p,
                                    ctypes.c_uint(len(releases)), releases_p,
                                    ctypes.c_uint(len(out)), out_p)
        return out



class TestVoice(unittest.TestCase, VoiceInterface):
    ''' Test implementations for voice module'''
    freq = 1000
    f_expected = 1000
    test_notes = [100, 400, 1000, 4000]
    env_test_note = 440
    fs = 44100
    debug = False
    freq_precision = 0.1

    def set_f(self, freq: float):
        ''' Set the expected frequency '''
        self.freq = freq/sampling_frequency
        self.f_expected = freq

    def run_self(self, presses: list, releases: list, n_samples: int):
        ''' Run the implementation for the test '''
        return self.run_voice(presses, releases, n_samples)

    def test_envelope(self):
        ''' Check that the envelope is being applied '''
        n_samples = 1*sampling_frequency # s
        self.set_f(self.env_test_note)
        for attack, decay, sustain, release in [(0.1, 0.05, -3., 0.1),
                                                (0.01, 0.1, -20, 0.5),
                                                (0.05, 0.2, -80, 0.4)
                                                ]:
            with self.subTest(f'{attack},{decay},{sustain},{release}'):
                self.set_adsr(attack, decay, sustain, release)
                press_time = int(0.1*sampling_frequency)
                release_time = int(0.4*sampling_frequency)
                voice_vector = np.abs(sig.hilbert(self.run_self([press_time], [release_time], n_samples)))
                env_vector = self.run_env([press_time], [release_time], n_samples)
                rms_error = (np.mean((voice_vector-env_vector)**2))**0.5
                if self.debug:
                    _, ax1 = plt.subplots()
                    time = np.arange(n_samples)/sampling_frequency
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
        self.set_adsr(0.001, 0.01, 1, 0.01)
        for freq in self.test_notes:
            self.set_f(freq)
            with self.subTest(f'{freq}'):
                press_time = 0
                release_time = int(n_samples)
                vector = self.run_self([press_time], [release_time], n_samples)
                f_vector = 20*np.log10(np.abs(np.fft.fft(vector))/n_samples)[:n_samples//2]
                pkidx = np.argmax(f_vector)
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
                self.assertAlmostEqual(f_measured, self.f_expected, delta=self.freq_precision)


def main():
    ''' For Debugging/Testing '''
    voice_test = TestVoice()
    voice_test.debug = True
    voice_test.test_envelope()
    voice_test.test_frequency()

if __name__=='__main__':
    main()
