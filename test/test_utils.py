''' Tests for utility functions '''
import ctypes
import unittest
import matplotlib.pyplot as plt
import numpy as np


class UtilsInterface:
    ''' ctypes wrapper around test shared object file'''
    def __init__(self):
        ''' Load in the test object file and define the function '''
        self.testlib = ctypes.CDLL('test.so')
        float_pointer = ctypes.POINTER(ctypes.c_float)
        # n (number of samples), io (float)
        self.testlib.test_db2mag.argtypes = [ctypes.c_uint, float_pointer]

    def run_db2mag(self, data: np.ndarray) -> None:
        ''' Run the Envelope Generator. Output is a float'''
        io_p = data.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        self.testlib.test_db2mag(ctypes.c_uint(len(data)), io_p)


class TestUtils(unittest.TestCase):
    ''' Tests for Utils'''
    debug = False

    def setUp(self) -> None:
        ''' Set up function, loads in the utils interface '''
        self.implementation = UtilsInterface()

    def test_db2mag(self) -> None:
        ''' Tests db2mag function across a range of values '''
        data = np.linspace(-100, 100, 200, dtype=np.float32)
        ref = 10**(data/20)
        self.implementation.run_db2mag(data)
        error = 100*(data-ref)/ref
        # within 0.0001%, arbitrary value
        self.assertAlmostEqual(np.max(np.abs(error)), 0, delta=0.0001)

        if self.debug:
            _, ax1 = plt.subplots()
            ax1.semilogy(data, label='Calculated')
            ax1.semilogy(ref, ls=':', label='Reference')
            ax1.grid()
            ax1.set_ylabel('Output')
            ax1.set_title('db2mag')
            ax1.legend()

            _, ax2 = plt.subplots()
            ax2.plot(error)
            ax2.grid()
            ax2.set_ylabel('Output')
            ax2.set_title('Percent Error')

            plt.show()



def main():
    ''' For Debugging/Testing '''
    env_test = TestUtils()
    env_test.setUp()
    env_test.debug = True
    env_test.test_db2mag()

if __name__=='__main__':
    main()
