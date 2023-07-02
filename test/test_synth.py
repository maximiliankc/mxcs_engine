''' Test and interface classes for synthesiser module
    copyright Maximilian Cornwell 2023 '''
import ctypes
import numpy as np
import scipy.signal as sig
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt

from .test_voice import VoiceInterface, TestVoice

class SynthInterface(VoiceInterface):
    ''' Interface for the synth '''
    def __init__(self):
        ''' Load in the test object file and define the function '''
        super().__init__()
        float_pointer = ctypes.POINTER(ctypes.c_float)
        uint_pointer = ctypes.POINTER(ctypes.c_uint)
        uint8_pointer = ctypes.POINTER(ctypes.c_uint8)
        # a, d, s, r, presses, pressNs, pressNotes, releases, releaseNs, n, envOut
        self.testlib.test_synth.argtypes = [ctypes.c_float, ctypes.c_float,
                                                ctypes.c_float, ctypes.c_float,
                                                ctypes.c_uint, uint_pointer, uint8_pointer,
                                                ctypes.c_uint, uint_pointer,
                                                ctypes.c_uint, float_pointer]
        self.testlib.test_frequency_table.argtypes = [float_pointer]

    def run_synth(self, presses: list, p_notes: list, releases: list, r_notes: list, n_samples: int) -> np.ndarray:
        ''' Run the Synth. Output is a float'''
        p_uint = ctypes.POINTER(ctypes.c_uint)
        p_uint8 = ctypes.POINTER(ctypes.c_uint8)
        out = np.zeros(n_samples, dtype=np.single)
        out_p = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        presses_p = np.array(presses, dtype=np.uintc).ctypes.data_as(p_uint)
        p_notes_p = np.array(p_notes, dtype=np.uint8).ctypes.data_as(p_uint8)
        r_notes_p = np.array(r_notes, dtype=np.uint8).ctypes.data_as(p_uint8)
        releases_p = np.array(releases, dtype=np.uintc).ctypes.data_as(p_uint)
        self.testlib.test_synth(ctypes.c_float(self.attack), ctypes.c_float(self.decay),
                                    ctypes.c_float(self.sustain), ctypes.c_float(self.release),
                                    ctypes.c_uint(len(presses)), presses_p, p_notes_p,
                                    ctypes.c_uint(len(releases)), releases_p, r_notes_p,
                                    ctypes.c_uint(len(out)), out_p)
        return out

    def run_frequency_table(self):
        ''' Reads the calculated frequency table '''
        table = np.zeros(128, dtype=np.single)
        table_p = table.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        self.testlib.test_frequency_table(table_p)
        return table


class TestSynth(TestVoice, SynthInterface):
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

    def set_f(self, freq: int):
        self.note = freq
        self.f_expected = self.midi_to_freq(freq)

    def run_self(self, presses: list, releases: list, n_samples: int):
        notes = len(presses)*[self.note]
        return self.run_synth(presses, notes, releases, notes, n_samples)

    def test_frequency_table(self):
        ''' Check the accuracy of the frequeny table '''
        reference = self.midi_to_freq(np.arange(128))
        device = self.run_frequency_table()*self.fs
        error_cents = 1200*np.log2(reference/device)
        if self.debug:
            _, ax1 = plt.subplots()
            ax1.plot(np.arange(128), reference, label='Target')
            ax1.plot(np.arange(128), device, label='Device')
            ax1.legend()
            ax1.grid(True)
            ax1.set_xlabel('MIDI note')
            ax1.set_ylabel('Frequency (Hz)')
            ax1.set_title('Error')

            _, ax2 = plt.subplots()
            ax2.plot(np.arange(128), error_cents)
            ax2.grid(True)
            ax2.set_xlabel('MIDI note')
            ax2.set_ylabel('Error (cents)')
            ax2.set_title('Error')
            plt.show()
        # check the frequency is within half a cent of the desired note
        self.assertLess(np.max(np.abs(error_cents)), 0.5)

    def play_notes(self):
        ''' Play a series of notes, show a spectrogram, save as a wav '''
        n_samples = self.fs*60
        for release_delay in [0.5, 1.5]:
            self.set_adsr(0.1, 0.1, -10, 0.1)
            presses = list(range(50))
            releases = [x+release_delay for x in presses]
            notes = [(2*p) % 24 + 50 for p in presses]
            presses = [p*self.fs for p in presses]
            releases = [r*self.fs for r in releases]
            out = self.run_synth(presses, notes, releases, notes, n_samples)
            wav.write(f'Test_Signal_{release_delay}.wav', self.fs, out)
            out = sig.resample_poly(out, 1, 4)
            freq, time, s_xx = sig.spectrogram(out, fs=self.fs/4, nperseg=2**12, noverlap=2**10)
            _, ax1 = plt.subplots()
            ax1.pcolormesh(time, freq, s_xx)
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Frequency (Hz)')
            _, ax2 = plt.subplots()
            time = np.arange(n_samples)/self.fs
            ax2.plot(time[:4*self.fs], out[:4*self.fs], label='signal')
            ax2.plot(time[:4*self.fs], np.abs(sig.hilbert(out[:4*self.fs])), label='envelope')
            ax2.set_xlabel('Time (s)')
            ax2.set_ylabel('Magnitude')
            ax2.grid(True)
            ax2.legend()
            plt.show()



def main():
    ''' For Debugging/Testing '''
    synth_test = TestSynth()
    synth_test.debug = True
    synth_test.test_envelope()
    synth_test.test_frequency()
    synth_test.test_frequency_table()
    synth_test.play_notes()

if __name__=='__main__':
    main()
