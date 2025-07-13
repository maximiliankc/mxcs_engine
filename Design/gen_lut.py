import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig


bits = 12
points = 2**bits

t = np.arange(points)
lut = np.sin((t/points)*2*np.pi, dtype=np.float32)

N = 8
with open('SineTable.h', 'w') as table_file:
    print("#ifndef SINE_TABLE_H", file=table_file)
    print("#define SINE_TABLE_H", file=table_file)
    print("", file=table_file)
    print(f"const unsigned int table_bits = {bits};", file=table_file)
    print(f"const unsigned int table_length = {points};", file=table_file)
    print("const float sine_table[table_length] = {\n    ", end='', file=table_file)
    for n, sample in enumerate(lut):
        if n == points-1:
            print(f"{sample:.16e}}};", file=table_file)
        elif (n + 1) % N == 0:
            print(f"{sample:.16e},\n    ", end='', file=table_file)
        else:
            print(f"{sample:.16e}, ", end='', file=table_file)
    print("", file=table_file)
    print("#endif // SINE_TABLE_H", file=table_file)
    print("", file=table_file)
