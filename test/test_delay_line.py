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
        uint32_pointer = ctypes.POINTER(ctypes.c_uint32)
        float_pointer = ctypes.POINTER(ctypes.c_float)
        self.testlib.test_delay_line.argtypes = [float_pointer, float_pointer, uint32_pointer,
                                                 ctypes.c_uint, float_pointer, ctypes.c_uint]
