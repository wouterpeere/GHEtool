"""
This document is an example on how to import hourly load profiles into GHEtool.
It uses the hourly_profile.csv data.
"""
import pygfunction as gt

# import all the relevant functions
from GHEtool import *

# initiate ground data
data = GroundData(3, 10, 0.12, 2.4*10**6)
borefield_gt = gt.boreholes.rectangle_field(10, 12, 6, 6, 110, 1, 0.075)

# initiate borefield
borefield = Borefield()

# set ground data in borefield
borefield.set_ground_parameters(data)

# set borefield
borefield.set_borefield(borefield_gt)

# load the hourly profile
borefield.load_hourly_profile("hourly_profile.csv", header=True, separator=";", first_column_heating=True)
borefield.convert_hourly_to_monthly()

# size the borefield and plot the resulting temperature evolution
depth = borefield.size(100, L2_sizing=True)
print(depth)
borefield.print_temperature_profile()
