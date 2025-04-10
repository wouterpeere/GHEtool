import numpy as np
import time
from scp.ethyl_alcohol import EthylAlcohol

data = (
    (1.4740e00, -4.7450e-02, 4.3140e-04, -3.0230e-06),
    (1.5650e-02, -4.1060e-05, -5.1350e-06, 7.0040e-08),
    (-8.4350e-04, 1.6400e-05, -1.0910e-07, -1.9670e-09),
    (7.5520e-06, -1.1180e-07, 1.8990e-09, 0),
    (1.5290e-07, -9.4810e-10, 0, 0),
    (-4.1300e-09, 0, 0, 0),
)

N = 100_000
concentration = 20
x_xm = [0.2 ** p for p in range(6)]
y_ym = [8 ** p for p in range(4)]
range = np.linspace(5, 50, N)
# method 1, iter
et = EthylAlcohol(0.2)
start = time.time_ns()
for i in range:
    et.viscosity(i)

print("Method 1: ", time.time_ns() - start)
start = time.time_ns()
res = [et.viscosity(i) for i in range]

print("Method 1':", time.time_ns() - start)

# method 2
et = EthylAlcohol(0.2)

start = time.time_ns()
ar = np.linspace(5, 50, 500)
array = np.array([et.viscosity(i) for i in ar])
res2 = np.interp(range, ar, array)
print("Method 2: ", time.time_ns() - start)

# method 3
start = time.time_ns()
et = EthylAlcohol(0.2)

matrix = np.array(data)
x_matrix = np.dot(np.array(x_xm), matrix)
start = time.time_ns()
coef = np.power(np.repeat(range.reshape((N, 1)), 4, axis=1), [0, 1, 2, 3])
np.dot(coef, x_matrix)
print("Method 3: ", time.time_ns() - start)
