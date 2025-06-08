''' Test and interface classes for synthesiser module
    copyright Maximilian Cornwell 2023 '''
import ctypes

from test.constants import sampling_frequencies
from test.test_voice import VoiceInterface, TestVoice, generators
from test.test_modulator import TestModulator

import numpy as np
import scipy.signal as sig
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt


class SynthInterface(VoiceInterface):
    ''' Interface for the synth '''
    mod_depth = 0
    mod_freq = 0

    def setUp(self):
        ''' Load in the test object file and define the function '''
        super().setUp()
        float_pointer = ctypes.POINTER(ctypes.c_float)
        uint_pointer = ctypes.POINTER(ctypes.c_uint)
        uint8_pointer = ctypes.POINTER(ctypes.c_uint8)
        # a, d,
        # s, r,
        # modDepth, modFreq,
        # generator, fs
        # presses, pressNs, pressNotes,
        # releases, releaseNs, releaseNotes,
        # n, envOut
        self.testlib.test_synth.argtypes = [ctypes.c_float, ctypes.c_float,
                                                ctypes.c_float, ctypes.c_float,
                                                ctypes.c_float, ctypes.c_float,
                                                ctypes.c_uint, ctypes.c_float,
                                                ctypes.c_uint, uint_pointer, uint8_pointer,
                                                ctypes.c_uint, uint_pointer, uint8_pointer,
                                                ctypes.c_uint, float_pointer]
        self.testlib.test_frequency_table.argtypes = [float_pointer, ctypes.c_float]

    def run_synth(self, presses: list, p_notes: list, releases: list, r_notes: list, n_samples: int, fs: float) -> np.ndarray:
        ''' Run the Synth. Output is a float'''
        p_uint = ctypes.POINTER(ctypes.c_uint)
        p_uint8 = ctypes.POINTER(ctypes.c_uint8)
        out = np.zeros(n_samples, dtype=np.single)
        out_p = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        presses_p = np.array(presses, dtype=np.uintc).ctypes.data_as(p_uint)
        p_notes_p = np.array(p_notes, dtype=np.uint8).ctypes.data_as(p_uint8)
        r_notes_p = np.array(r_notes, dtype=np.uint8).ctypes.data_as(p_uint8)
        releases_p = np.array(releases, dtype=np.uintc).ctypes.data_as(p_uint)
        self.testlib.test_synth(self.attack_seconds, self.decay_seconds,
                                    self.sustain, self.release_seconds,
                                    self.mod_depth, self.mod_freq,
                                    generators[self.generator], fs,
                                    len(presses), presses_p, p_notes_p,
                                    len(releases), releases_p, r_notes_p,
                                    len(out), out_p)
        return out

    def run_frequency_table(self, fs):
        ''' Reads the calculated frequency table '''
        table = np.zeros(128, dtype=np.single)
        table_p = table.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        self.testlib.test_frequency_table(table_p, fs)
        return table


class TestSynth(SynthInterface, TestVoice, TestModulator):
    ''' Test suite for synthesiser module'''
    note = 64
    test_notes = [13*n for n in range(9)] + [127]
    env_test_note = 69

    @staticmethod
    def midi_to_freq(note):
        ''' Converts a midi note to a frequency
            formula from:
            https://newt.phys.unsw.edu.au/jw/notes.html'''
        return 440*2**((note-69)/12)

    def set_f(self, freq: int, fs: float):
        self.note = freq
        self.f_expected = self.midi_to_freq(freq)

    def run_voice(self, presses: list, releases: list, n_samples: int, fs: float):
        notes = len(presses)*[self.note]
        self.mod_freq = 0
        self.mod_depth = 0
        return self.run_synth(presses, notes, releases, notes, n_samples, fs)

    def run_mod(self, freq: float, ratio: float, n_samples: int, fs: float):
        self.mod_freq = freq
        self.mod_depth = ratio
        self.set_adsr(10**-6, 10**-6, 0, 10**-6, fs)
        vector = sig.hilbert(self.run_synth([0], [64], [0], [0], n_samples, fs))
        self.check_abs = True
        return np.abs(vector)

    def test_frequency_table(self):
        ''' Check the accuracy of the frequeny table '''
        for fs in [44100, 48000]:
            reference = self.midi_to_freq(np.arange(128))
            device = self.run_frequency_table(fs)*fs
            error_cents = 1200*np.log2(reference/device)
            if self.debug:
                _, ax1 = plt.subplots()
                ax1.semilogy(np.arange(128), reference, label='Target')
                ax1.semilogy(np.arange(128), device, label='Device')
                ax1.legend()
                ax1.grid(True)
                ax1.set_xlabel('MIDI note')
                ax1.set_ylabel('Frequency (Hz)')
                ax1.set_title(f'Error ({fs=})')

                _, ax2 = plt.subplots()
                ax2.plot(np.arange(128), error_cents)
                ax2.grid(True)
                ax2.set_xlabel('MIDI note')
                ax2.set_ylabel('Error (cents)')
                ax2.set_title(f'Error ({fs=})')
                plt.show()
            # check the frequency is within half a cent of the desired note
            self.assertLess(np.max(np.abs(error_cents)), 0.5)

    def play_notes(self):
        ''' Play a series of notes, show a spectrogram, save as a wav '''
        sampling_frequency = 44100
        n_samples = sampling_frequency*60
        for gen in generators:
            self.generator = gen
            for release_delay, mod_depth, mod_freq in zip([0.5, 1.5, 1], [0.5, 1, 0.25], [0.5, 3, 1]):
                self.set_adsr(0.1, 0.1, -5, 0.1, sampling_frequency)
                self.mod_freq = mod_freq
                self.mod_depth = mod_depth
                presses = list(range(50))
                releases = [x+release_delay for x in presses]
                notes = [(2*p) % 24 + 50 for p in presses]
                presses = [p*sampling_frequency for p in presses]
                releases = [r*sampling_frequency for r in releases]
                out = self.run_synth(presses, notes, releases, notes, n_samples, sampling_frequency)
                wav.write(f'Test_Signal_{release_delay}_{mod_depth}_{mod_freq}_{gen}.wav', sampling_frequency, out)
                out = sig.resample_poly(out, 1, 4)
                freq, time, s_xx = sig.spectrogram(out, fs=sampling_frequency/4, nperseg=2**12, noverlap=2**10)
                _, ax1 = plt.subplots()
                ax1.pcolormesh(time, freq, s_xx)
                ax1.set_xlabel('Time (s)')
                ax1.set_ylabel('Frequency (Hz)')
                ax1.set_title(f'Release delay: {release_delay}, Mod Depth: {mod_depth}, Mod Freq {mod_freq}')
                _, ax2 = plt.subplots()
                time = np.arange(n_samples)/sampling_frequency
                ax2.plot(time[:4*sampling_frequency], out[:4*sampling_frequency], label='signal')
                ax2.plot(time[:4*sampling_frequency], np.abs(sig.hilbert(out[:4*sampling_frequency])), label='envelope')
                ax2.set_xlabel('Time (s)')
                ax2.set_ylabel('Magnitude')
                ax2.set_title(f'{gen}, Release delay: {release_delay}, Mod Depth: {mod_depth}, Mod Freq {mod_freq}')
                ax2.grid(True)
                ax2.legend()
                plt.show()

    #   TODO: add integration tests for filters


def main():
    ''' For Debugging/Testing '''
    synth_test = TestSynth()
    synth_test.setUp()
    synth_test.debug = True
    # synth_test.test_model()
    # synth_test.test_envelope()
    # synth_test.test_frequency()
    synth_test.test_frequency_table()
    # synth_test.play_notes()

if __name__=='__main__':
    main()
