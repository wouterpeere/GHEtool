"""
This document is an example of load optimisation.
First an hourly profile is imported and a fixed borefield size is set.
Then, based on a load-duration curve, the heating and cooling load is altered in order to fit as much load as possible on the field.
The results are returned.

"""
# import all the relevant functions
from GHEtool import *

if __name__ == "__main__":

    # initiate ground data
    data = GroundData(110, 6, 3, 10, 0.2, 10, 10)

    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(data)

    # load the hourly profile
    borefield.load_hourly_profile("Hourly_Profile.csv", header=True, separator=";", first_column_heating=True)

    # optimise the load for a 10x10 field (see data above) and a fixed depth of 150m.
    borefield.optimise_load_profile(depth=150, print_results=True)

    # print resulting external peak cooling profile
    print(borefield.peak_cooling_external)

    # print resulting monthly load for an external heating source
    print(borefield.monthly_load_heating_external)
