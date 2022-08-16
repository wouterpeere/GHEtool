"""

"""

from GHEtool import Borefield
from GHEtool.VariableClasses import GroundData
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

start_imbalance = 200

# define load
monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
monthly_load_heating = monthly_load_heating_percentage * start_imbalance * 10 ** 3
monthly_load_cooling = monthly_load_cooling_percentage * 150 * 10 ** 3
peak_cooling = np.array([0., 0., 22., 44., 83., 117., 134., 150., 100., 23., 0., 0.])
peak_heating = np.array([300., 268., 191., 103., 75., 0., 0., 38., 76., 160., 224., 255.])

# define borefield
borefield = Borefield(simulation_period=20,
                      peak_heating=peak_heating,
                      peak_cooling=peak_cooling,
                      baseload_heating=monthly_load_heating,
                      baseload_cooling=monthly_load_cooling)

data = GroundData(110,           # depth (m)
                  6,             # borehole spacing (m)
                  3,             # conductivity of the soil (W/mK)
                  10,            # Ground temperature at infinity (degrees C)
                  0.2,           # equivalent borehole resistance (K/W)
                  13,            # width of rectangular field (#)
                  13)            # length of rectangular field (#)

borefield.set_ground_parameters(data)
depth = []

### method 1 add imbalance equally to all months
range_imbalance = np.array([1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5])

for i in range_imbalance:
    delta_imbalance = start_imbalance * (i - 1)
    delta_month = delta_imbalance / 12
    delta_peak = np.ones(12) * delta_month
    borefield.set_baseload_heating(monthly_load_heating + np.ones(12) * delta_month)
    borefield.set_peak_heating(peak_heating + np.ones(12) * delta_month)
    depth.append(borefield.size())

print(linregress(range_imbalance * start_imbalance - 150, depth))

plt.figure()
plt.plot(range_imbalance * start_imbalance - 150, depth)
plt.xlabel("Imbalance [MWh/y]")
plt.ylabel("Depth [m]")
plt.show()

### method 2 scale monthly load and increase peak accordingly
depth = []
range_imbalance = np.array([1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5])

for i in range_imbalance:
    delta_peak = monthly_load_heating * (i - 1) / 730.
    borefield.set_baseload_heating(monthly_load_heating * i)
    borefield.set_peak_heating(peak_heating + delta_peak)
    depth.append(borefield.size())

print(linregress(range_imbalance * start_imbalance - 150, depth))

plt.figure()
plt.plot(range_imbalance * start_imbalance - 150, depth)
plt.xlabel("Imbalance [MWh/y]")
plt.ylabel("Depth [m]")
plt.show()

### method 3 scale load linearly
depth = []
range_imbalance = np.array([1, 1.5, 2, 2.5, 3, 3.5, 4])

for i in range_imbalance:
    print(i)
    borefield.set_baseload_heating(monthly_load_heating * i)
    borefield.set_peak_heating(peak_heating * i)
    depth.append(borefield.size())

print(linregress(range_imbalance * start_imbalance - 150, depth))

plt.figure()
plt.plot(range_imbalance * start_imbalance - 150, depth)
plt.xlabel("Imbalance [MWh/y]")
plt.ylabel("Depth [m]")
plt.show()


# rectangular fields
list_or_rectangular_fields = np.array(((8, 8),
                                      (8, 12),
                                      (8, 14),
                                      (8, 16),
                                      (8, 18),
                                      (10, 10),
                                      (12, 12),
                                      (14, 14),
                                      (16, 16),
                                      (18, 18),
                                      (20, 20)))

