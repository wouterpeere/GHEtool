"""
This file is an example on how to use the functionality of GHEtool of sizing a borefield by length and width.
"""
# import all the relevant functions
from GHEtool import Borefield, GroundData
import numpy as np

if __name__ == "__main__":
    # set ground data
    data = GroundData(110, 6, 3, 10, 0.2, 10, 12, 2.4 * 10**6)

    # monthly loading values
    peak_cooling = np.array([0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.])  # Peak cooling in kW
    peak_heating = np.array([160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.])  # Peak heating in kW

    # annual heating and cooling load
    annual_heating_load = 300 * 10 ** 3  # kWh
    annual_cooling_load = 160 * 10 ** 3  # kWh

    # percentage of annual load per month (15.5% for January ...)
    monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
    monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])

    # resulting load per month
    monthly_load_heating = annual_heating_load * monthly_load_heating_percentage  # kWh
    monthly_load_cooling = annual_cooling_load * monthly_load_cooling_percentage  # kWh

    # create the borefield object
    borefield = Borefield(simulation_period=20,
                          peak_heating=peak_heating,
                          peak_cooling=peak_cooling,
                          baseload_heating=monthly_load_heating,
                          baseload_cooling=monthly_load_cooling)

    borefield.set_ground_parameters(data)

    # set temperature boundaries
    borefield.set_max_ground_temperature(16)  # maximum temperature
    borefield.set_min_ground_temperature(0)  # minimum temperature

    # set parameters for sizing
    max_width = 60  # m
    max_length = 60  # m
    min_spacing = 5  # m
    max_spacing = 8  # m
    max_depth = 250  # m

    # size by length and width
    result = borefield.size_by_length_and_width(max_depth, max_width, max_length, min_spacing,
                                                max_spacing)
    # print the possible solutions
    if not result:
        print("There are no possible solutions!")
        exit()

    for solution in result:
        print("A possible borefield is a borefield of size", solution[0], "by", solution[1], end=" ")
        print("with a spacing of", solution[2], "m and a depth of", round(solution[3], 2), "m.")
