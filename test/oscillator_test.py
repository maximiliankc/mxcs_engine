import ctypes
import numpy as np
import matplotlib.pyplot as plt

class OscillatorInterface:
    def __init__(self):
        ''' Load in the test object file and define the function '''
        self.block_size = 16
        self.testlib = ctypes.CDLL('test.so')
        float_pointer = ctypes.POINTER(ctypes.c_float)
        self.testlib.test_oscillator.argtypes = [ctypes.c_float, ctypes.c_int, float_pointer, float_pointer]

    def run(self, f: float, n: int):
        sinOut = (n*ctypes.c_float)(*n*[0])
        cosOut = (n*ctypes.c_float)(*n*[0])
        print(sinOut)
        self.testlib.test_oscillator(ctypes.c_float(f), ctypes.c_int(n), sinOut, cosOut)
        return np.array(sinOut), np.array(cosOut)

def main():
    osc = OscillatorInterface()
    fs = 48000
    f = 200
    n = 100*osc.block_size
    sin, cos = osc.run(f/fs, n)
    t = np.arange(n)
    _, ax = plt.subplots()
    ax.plot(t, sin, label='sin')
    ax.plot(t, cos, label='cos')
    ax.legend()
    ax.set_xlabel('Sample')
    ax.grid()
    plt.show()


if __name__=='__main__':
    main()
