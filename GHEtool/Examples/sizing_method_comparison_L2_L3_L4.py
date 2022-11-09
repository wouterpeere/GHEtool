"""
This document is an example of the different sizing methods in GHEtool.
The example load profile is for a profile limited in the first year of operation.
"""
# import all the relevant functions
from GHEtool import *
import time
import pygfunction as gt
import numpy as np

# initiate ground data
data = GroundData(3, 10, 0.12)

# initiate pygfunction borefield model
borefield_gt = gt.boreholes.rectangle_field(10, 10, 6, 6, 110, 1, 0.075)

# initiate borefield
borefield = Borefield(100)

# set ground data in borefield
borefield.set_ground_parameters(data)

# set pygfunction borefield model
borefield.set_borefield(borefield_gt)

# load the hourly profile
borefield.load_hourly_profile("hourly_profile.csv", header=True, separator=";", first_column_heating=True)

### size the borefield
# according to L2
L2_start = time.time()
borefield.convert_hourly_to_monthly()
depth_L2 = borefield.size(100, L2_sizing=True)

L2_stop = time.time()

# according to L3
L3_start = time.time()
borefield.convert_hourly_to_monthly()
#borefield.determine_peak_length_from_hourly_data()
borefield.calculate_temperatures(100, False)
#borefield.set_length_peak(6)
Tb = borefield.Tb
Temp_res = np.minimum(np.maximum(borefield.results_peak_cooling, borefield.results_peak_heating), borefield.results_peak_heating)
# depth_L3 = borefield.size(100, L3_sizing=True)
L3_stop = time.time()

# according to L4
L4_start = time.time()
borefield.calculate_temperatures(100, True)
#depth_L4 = borefield.size(100, L4_sizing=True)
Tb2 = np.array([borefield.Tb[borefield.HOURLY_LOAD_ARRAY[t] + 729] for t in range(12)])
Tb3 = np.array([borefield.Tb[borefield.HOURLY_LOAD_ARRAY[t] + 729 + 8760 * 99] for t in range(12)])
Temp_res2 = np.array([borefield.results_peak_heating[borefield.HOURLY_LOAD_ARRAY[t] + 729] for t in range(12)])
Temp_res3 = np.array([borefield.results_peak_heating[borefield.HOURLY_LOAD_ARRAY[t] + 729 + 8760 * 99] for t in range(12)])
assert np.allclose(Tb[:12], Tb2)
assert np.allclose(Tb[12*99:], Tb3)
print(Temp_res[:12], Temp_res2)
assert np.allclose(Temp_res[:12], Temp_res2)
assert np.allclose(Temp_res[12*99:], Temp_res3)
L4_stop = time.time()

### print results
print("The sizing according to L2 took", round((L2_stop-L2_start) * 1000, 4), "ms and was", depth_L2, "m.")
#print("The sizing according to L3 took", round((L3_stop-L3_start) * 1000, 4), "ms and was", depth_L3, "m.")
#print("The sizing according to L4 took", round((L4_stop-L4_start) * 1000, 4), "ms and was", depth_L4, "m.")

#borefield.plot_load_duration()
#borefield.print_temperature_profile(plot_hourly=True)
