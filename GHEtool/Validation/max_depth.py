"""
This file contains the reasoning behind the sizing method when the field is limited by injection (i.e. cooling)
and there is a non-constant ground temperature. This is based on the assumption that the difference between the
maximum peak temperature in injection and the average, undistrubed ground temperature scales like 1/depth.

This can be understood since the main contributor to the peak temperature is the peak load, which, in the sizing,
is expressed as a load per meter (W/m), so it scales like 1/depth.
"""

from GHEtool import *
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

ground_data = GroundFluxTemperature(3, 10)
fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
borefield = Borefield()
borefield.create_rectangular_borefield(5, 4, 6, 6, 110, 4, 0.075)
borefield.set_ground_parameters(ground_data)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
borefield.sizing_setup(use_constant_Rb=False)
borefield.set_max_ground_temperature(17)
borefield.set_min_ground_temperature(3)
hourly_load = HourlyGeothermalLoad()
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly data\\auditorium.csv"), header=True, separator=";",
                              col_cooling=0, col_heating=1)
borefield.load = hourly_load

Tg_array = []
max_Tf_array = []
depth_array = range(20, 450, 20)

for depth in depth_array:
    print(f'The current depth is {depth} m.')
    borefield.calculate_temperatures(depth)
    Tg_array.append(borefield.ground_data.calculate_Tg(depth))
    max_Tf_array.append(np.max(borefield.results_peak_cooling))

def f(x, a, b):
    return a/x + b

# fit to 1/x curve
diff = np.array(max_Tf_array) - np.array(Tg_array)

prev_gfunctions = borefield.gfunction_calculation_object.previous_gfunctions
g_value_differences = []
for idx, prev in enumerate(prev_gfunctions):
    g_values = borefield.gfunction(borefield.load.time_L3, depth_array[idx])
    g_value_differences.append(np.diff(g_values, prepend=0))

plt.figure()
for idx, diff in enumerate(g_value_differences):
    plt.plot(diff, label=depth_array[idx])
plt.legend()
plt.show()

popt, pcov = curve_fit(f, depth_array, diff)
print(popt, pcov)

plt.figure()
plt.plot(depth_array, Tg_array, label='Ground')
plt.plot(depth_array, max_Tf_array, label='Fluid')
plt.hlines(borefield.Tf_max, 0, depth_array[-1])
plt.xlabel('Depth [m]')
plt.ylabel('Temperature [deg C]')
plt.legend()
# plt.show()

plt.figure()
plt.plot(diff, label='diff')
plt.plot(f(np.array(depth_array), *popt), label='fitted')
plt.legend()
plt.show()
