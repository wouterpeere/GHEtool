"""
This document is an example on how to import hourly load profiles into GHEtool.
"""
# import all the relevant functions
from GHEtool import *

if __name__ == "__main__":

    # initiate ground data
    data = GroundData(110, 6, 3, 10, 0.12, 10, 12, 2.4*10**6)

    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(data)

    # load the hourly profile
    borefield.load_hourly_profile("hourly_profile.csv", header=True, separator=";", first_column_heating=True)
    borefield.convert_hourly_to_monthly()

    # size the borefield and plot the resulting temperature evolution
    depth = borefield.size(100)
    print(depth)
    borefield.print_temperature_profile()
