"""
This document is an example on how to import hourly load profiles into GHEtool.
It uses the hourly_profile.csv data.
"""
import pygfunction as gt

from GHEtool import *

# initiate ground data
data = GroundConstantTemperature(3, 10, 2.4 * 10 ** 6)
borefield_gt = gt.borefield.Borefield.rectangle_field(10, 12, 6, 6, 110, 1, 0.075)

# initiate borefield
borefield = Borefield()

# set ground data in borefield
borefield.ground_data = data

# set Rb
borefield.Rb = 0.12

# set borefield
borefield.set_borefield(borefield_gt)

# load the hourly profile
load = HourlyGeothermalLoad()
load.load_hourly_profile("hourly_profile.csv", header=True, separator=";")
borefield.load = load

# size the borefield and plot the resulting temperature evolution
depth = borefield.size(100, L2_sizing=True)
print(depth)
borefield.print_temperature_profile()
