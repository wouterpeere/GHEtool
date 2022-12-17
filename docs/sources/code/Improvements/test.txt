import random
import time
import numpy as np


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx

array = np.linspace(0, 200, 25)
threshold = 8

start_time = time.time()

for i in range(20):
    elem = random.randint(0, 200)

    val, idx = find_nearest(array, elem)

    if idx == 0:
        if val - elem < threshold:
            print("interpol")
            idx_new = idx
        else:
            idx_new = idx + 1
            val_nex = array[idx+1]
            if val_nex-val < threshold:
                print("interpol")

    if val == array[-1]:
        if elem - val < threshold:
            idx_new = idx
            print("interpol")
        else:
            idx_new = idx - 1
            val_prev = array[idx-1]
            if val - val_prev < threshold:
                print("interpol")

    if val > elem:
        idx_new = idx
    else:
        idx_new = idx + 1

    array = np.insert(array, idx_new, elem)


print(array)