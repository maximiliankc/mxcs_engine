''' Script for determining the best place to switch to limit calculation for msinc '''

import numpy as np
import matplotlib.pyplot as plt

THRESHOLD = 2**-32
RATIO = 0.4
SAMPLING_FREQUENCY = 44100

def calc_m(freq: float) -> int:
    ''' Calculate m factor for a given frequency '''
    period = int((RATIO/freq))
    m = 2*period + 1
    return m

def msinc_d(n: np.ndarray, f: float)->tuple[np.ndarray,np.ndarray]:
    ''' Calculates the periodic sinc function'''
    m = calc_m(f)
    top = np.sin(np.pi*m*f*n)
    topc = np.cos(np.pi*m*f*n)
    bottom = m*np.sin(np.pi*f*n)
    bottomc = np.cos(np.pi*f*n)
    y = np.empty_like(top)
    smallbottom = np.abs(bottom)<THRESHOLD
    ysin = top/bottom
    ycos = topc/bottomc
    y[smallbottom] = ycos[smallbottom]
    y[~smallbottom] = ysin[~smallbottom]
    return y, bottom

def msinc_s(n: np.ndarray, f: float)->tuple[np.ndarray,np.ndarray]:
    ''' Calculates msinc, but only sine component'''
    m = calc_m(f)
    top = np.sin(np.pi*m*f*n).astype(np.float32)
    bottom = m*np.sin(np.pi*f*n).astype(np.float32)
    y = top/bottom
    return y, bottom

def msinc_c(n: np.ndarray, f: float)->tuple[np.ndarray,np.ndarray]:
    ''' Calculates msinc, but only cosine component '''
    m = calc_m(f)
    top = np.cos(np.pi*m*f*n).astype(np.float32)
    bottom = np.cos(np.pi*f*n).astype(np.float32)
    y = top/bottom
    return y, bottom

def main():
    ''' Find The optimal threshold for the float version of msinc to match the double version '''
    n = np.arange(0, 2**16)
    # 21, 109
    freqs = 440*2**((np.arange(21, 109)-69)/12)
    sin_bottoms = np.array([])
    cos_errors = np.array([])
    sin_errors = np.array([])
    for freq in freqs:
        double_sig, _ = msinc_d(n, freq/SAMPLING_FREQUENCY)
        sin_sig, bottom = msinc_s(n, freq/SAMPLING_FREQUENCY)
        cos_sig, _ = msinc_c(n, freq/SAMPLING_FREQUENCY)

        cos_error = cos_sig - double_sig
        sin_error = sin_sig - double_sig
        adjusted_cos_error = np.copy(cos_error)
        adjusted_cos_error[np.abs(sin_error)<0.1] = np.nan

        sin_bottoms = np.append(sin_bottoms, bottom)
        cos_errors = np.append(cos_errors, cos_error)
        sin_errors = np.append(sin_errors, sin_error)

        # _, ax = plt.subplots()
        # # ax.plot(cos_error, label='Cosine Error')
        # ax.plot(sin_error, label='Sine Error')
        # ax.plot(adjusted_cos_error, label='Cosine Error', marker='x')

        # # ax.plot(double_sig, label='Double')
        # # ax.plot(sin_sig, label='Sine')
        # # ax.plot(cos_sig, label='Cosine')
        # ax.grid(True)
        # ax.set_title(f'f = {freq}')
        # ax.legend()
        # plt.show()

    _, ax2 = plt.subplots()
    check_errors = np.abs(sin_bottoms)<2**0
    ax2.scatter(sin_bottoms[check_errors], sin_errors[check_errors], label='Sine', marker='o')
    ax2.scatter(sin_bottoms[check_errors], cos_errors[check_errors], label='Cosine', marker='x')
    ax2.grid(True)
    ax2.legend()
    plt.show()

if __name__=='__main__':
    main()