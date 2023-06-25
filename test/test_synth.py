import ctypes
import numpy as np

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


class TestSynth(TestVoice, SynthInterface):
    note = 64

    def run_self(self, presses: list, releases: list, N: int):
        notes = len(presses)*[self.note]
        return self.run_synth(presses, notes, releases, N)


def main():
    ''' For Debugging/Testing '''
    synth_test = TestSynth()
    synth_test.debug = True
    synth_test.test_envelope()
    # synth_test.test_frequency()

if __name__=='__main__':
    main()