''' Tests for voice '''
import ctypes
import unittest
import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sig
from .test_envelope import EnvelopeInterface
from .test_oscillator import OscillatorInterface


class VoiceInterface(EnvelopeInterface, OscillatorInterface):
    f = 0
    ''' ctypes wrapper around test shared object file'''
    def __init__(self):
        ''' Load in the test object file and define the function '''
        super().__init__()
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



class TestVoice(unittest.TestCase, VoiceInterface):
    f = 1000
    f_expected = 1000
    test_notes = [100, 400, 1000, 4000]
    env_test_note = 440
    fs = 48000
    debug = False
    freq_precision = 0.1

    def set_f(self, freq: float):
        ''' Set the expected frequency '''
        self.f = freq/self.fs
        self.f_expected = freq

    def run_self(self, presses: list, releases: list, N: int):
        ''' Run the implementation for the test '''
        return self.run_voice(presses, releases, N)

    def test_envelope(self):
        ''' Check that the envelope is being applied '''
        N = 1*self.fs # s
        self.set_f(self.env_test_note)
        for a, d, s, r in [(0.1, 0.05, -3., 0.1),
                           (0.01, 0.1, -20, 0.5),
                           (0.05, 0.2, -80, 0.4)
                           ]:
            with self.subTest(f'{a},{d},{s},{r}'):
                self.set_adsr(a, d, s, r)
                press_time = int(0.1*self.fs)
                release_time = int(0.4*self.fs)
                voice_vector = np.abs(sig.hilbert(self.run_self([press_time], [release_time], N)))
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

    def test_frequency(self):
        ''' Check the frequency of the voice '''
        N = self.calculate_length(self.freq_precision)
        self.set_adsr(0.001, 0.01, 1, 0.01)
        for freq in self.test_notes:
            self.set_f(freq)
            with self.subTest(f'{freq}'):
                press_time = 0
                release_time = int(N)
                vector = self.run_self([press_time], [release_time], N)
                f_vector = 20*np.log10(np.abs(np.fft.fft(vector))/N)[:N//2]
                pkidx = np.argmax(f_vector)
                freqs = self.fs*np.fft.fftfreq(N)[:N//2]
                f_measured = freqs[pkidx]
                if self.debug:
                    _, ax = plt.subplots()
                    t = np.arange(N)/self.fs
                    ax.plot(t, vector)
                    ax.grid()
                    ax.set_title(f'Output f={self.f_expected:.2f}')
                    ax.set_ylabel('Magnitude')
                    ax.set_xlabel('Time (s)')

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