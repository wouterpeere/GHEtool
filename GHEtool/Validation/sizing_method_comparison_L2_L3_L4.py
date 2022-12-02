"""
This document is an example of the different sizing methods in GHEtool.
The example load profile is for a profile limited in the first year of operation.
"""
# import all the relevant functions
from GHEtool import *
import time
import pygfunction as gt

# initiate ground data
data = GroundData(3, 10, 0.12)

# initiate borefield
borefield = Borefield()

# set ground data in borefield
borefield.set_ground_parameters(data)

# set the borefield
borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 1, 0.075)

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
depth_L3 = borefield.size(100, L3_sizing=True)
L3_stop = time.time()

# according to L4
L4_start = time.time()
depth_L4 = borefield.size(100, L4_sizing=True)
L4_stop = time.time()

### print results
print("The sizing according to L2 took", round((L2_stop-L2_start) * 1000, 4), "ms and was", depth_L2, "m.")
print("The sizing according to L3 took", round((L3_stop-L3_start) * 1000, 4), "ms and was", depth_L3, "m.")
print("The sizing according to L4 took", round((L4_stop-L4_start) * 1000, 4), "ms and was", depth_L4, "m.")

borefield.plot_load_duration()
borefield.print_temperature_profile(plot_hourly=True)
