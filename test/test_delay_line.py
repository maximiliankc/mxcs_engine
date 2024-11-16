''' Tests for delay line
    copyright Maximilian Cornwell 2024 '''
import ctypes
import unittest
import matplotlib.pyplot as plt
import numpy as np

class DelayLineInterface:
    ''' Interface for delay line test function '''
    testlib = ctypes.CDLL('test.so')

    def setUp(self):
        ''' Configure ctypes interface for delay line '''
        uint32_pointer = ctypes.POINTER(ctypes.c_uint32)
        float_pointer = ctypes.POINTER(ctypes.c_float)
        self.testlib.test_delay_line.argtypes = [float_pointer, float_pointer, uint32_pointer,
                                                 ctypes.c_uint, float_pointer, ctypes.c_uint]

    def run_delay_line(self, data_in: list, delays: list, line_length: int) -> np.ndarray:
        ''' Actually run the delay line '''
        p_float = ctypes.POINTER(ctypes.c_float)
        p_uint32 = ctypes.POINTER(ctypes.c_uint32)
        data_in = np.array(data_in, dtype=np.single)
        p_data_in = data_in.ctypes.data_as(p_float)
        data_out = np.zeros_like(data_in)
        p_data_out = data_out.ctypes.data_as(p_float)
        delays = np.array(delays, dtype=np.uint32)
        p_delays = delays.ctypes.data_as(p_uint32)
        memory = np.empty(line_length, dtype=np.single)
        p_memory = memory.ctypes.data_as(p_float)
        self.testlib.test_delay_line(p_data_in, p_data_out, p_delays,\
                                     len(data_in), p_memory, line_length)

        return data_out


class TestDelayLine(DelayLineInterface, unittest.TestCase):
    '''Tests For the Delay Line'''
    debug = False

    def test_basic(self):
        ''' Test a basic signal '''
        test_length = 32
        signal_in = np.arange(test_length, dtype=np.single)
        for delay in [0, 1, 2, 4, 8, 16, 32, 64, 128]:
            delays_in = delay*np.ones(test_length)
            signal_out = self.run_delay_line(signal_in, delays_in, delay+1)
            model_out = np.append(np.zeros(delay), signal_in)[:test_length]
            if self.debug:
                _, [ax, e_ax] = plt.subplots(2, 1)
                ax.plot(signal_in, label='In')
                ax.plot(signal_out, label='Out')
                ax.plot(model_out, label='Model Out', ls=':')
                ax.legend()
                ax.grid(True)
                e_ax.plot(model_out - signal_out, label='Error')
                e_ax.grid(True)
                e_ax.legend()
                plt.show()

            self.assertTrue((model_out == signal_out).all(), 'Model delay is equal to Implementation')

    def test_random_delays(self):
        ''' Does some basic testing of the delay Line '''
        test_length = 128
        for line_lengths in [1, 100, 128, 10000]:
            random_generator = np.random.default_rng(1234)
            samples_in = random_generator.uniform(-1, 1, size=test_length).astype(dtype=np.single)
            delays_in = random_generator.uniform(0, line_lengths-1, size=test_length).astype(dtype=np.uint32)
            test_out = self.run_delay_line(samples_in, delays_in, line_lengths)
            delay_idxs = np.arange(test_length) - delays_in + line_lengths
            model_out = np.append(np.zeros(line_lengths), samples_in)[delay_idxs]
            if self.debug:
                _, [abs_ax, er_ax] = plt.subplots(2, 1)
                abs_ax.plot(test_out, label='Calculated')
                abs_ax.plot(model_out, label='Model')
                er_ax.plot(model_out-test_out)
                abs_ax.set_ylabel('Magnitude')
                er_ax.set_ylabel('Error')
                abs_ax.grid(True)
                er_ax.grid(True)
                plt.show()

            self.assertTrue((model_out == test_out).all(), 'Model delay is equal to Implementation')


def main():
    ''' For Debugging/Testing '''
    delay_test = TestDelayLine()
    delay_test.setUp()
    delay_test.debug = True
    delay_test.test_basic()
    delay_test.test_random_delays()


if __name__=='__main__':
    main()
