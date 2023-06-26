import ctypes
import numpy as np
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

    def run_synth(self, presses: list, notes: list, releases: list, n: int) -> np.ndarray:
        ''' Run the Synth. Output is a float'''
        p_uint = ctypes.POINTER(ctypes.c_uint)
        p_uint8 = ctypes.POINTER(ctypes.c_uint8)
        out = np.zeros(n, dtype=np.single)
        out_p = out.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        presses_p = np.array(presses, dtype=np.uintc).ctypes.data_as(p_uint)
        press_notes_p = np.array(notes, dtype=np.uint8).ctypes.data_as(p_uint8)
        releases_p = np.array(releases, dtype=np.uintc).ctypes.data_as(p_uint)
        self.testlib.test_synth(ctypes.c_float(self.a), ctypes.c_float(self.d),
                                    ctypes.c_float(self.s), ctypes.c_float(self.r),
                                    ctypes.c_uint(len(presses)), presses_p, press_notes_p,
                                    ctypes.c_uint(len(releases)), releases_p,
                                    ctypes.c_uint(len(out)), out_p)
        return out

    def run_frequency_table(self):
        ''' Reads the calculated frequency table '''
        table = np.zeros(128, dtype=np.single)
        table_p = table.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        self.testlib.test_frequency_table(table_p)
        return table


class TestSynth(TestVoice, SynthInterface):
    note = 64
    test_notes = [13*n for n in range(9)] + [127]
    env_test_note = 69

    @staticmethod
    def midi_to_freq(note):
        ''' Converts a midi note to a frequency '''
        return 440*2**((note-69)/12)

    def set_f(self, freq: int):
        self.note = freq
        self.f_expected = self.midi_to_freq(freq)

    def run_self(self, presses: list, releases: list, N: int):
        notes = len(presses)*[self.note]
        return self.run_synth(presses, notes, releases, N)

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
            ax1.set_ylabel('Error (cents)')
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


def main():
    ''' For Debugging/Testing '''
    synth_test = TestSynth()
    synth_test.debug = True
    synth_test.test_envelope()
    synth_test.test_frequency()
    synth_test.test_frequency_table()

if __name__=='__main__':
    main()
