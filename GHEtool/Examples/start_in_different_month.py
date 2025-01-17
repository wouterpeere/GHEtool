"""
This example illustrates the importance of when a borefield is 'started' (i.e. when the first month of operation is).
"""

from GHEtool import *
from GHEtool.Validation.cases import load_case

import matplotlib.pyplot as plt


def start_in_different_month():
    # set data
    ground_data = GroundTemperatureGradient(2.5, 10)
    load = MonthlyGeothermalLoadAbsolute(*load_case(1))

    # create borefield object
    borefield = Borefield(load=load)
    borefield.ground_data = ground_data
    borefield.create_rectangular_borefield(10, 8, 6, 6, 100)

    borefield.set_max_avg_fluid_temperature(17)
    borefield.set_min_avg_fluid_temperature(3)
    borefield.calculation_setup(max_nb_of_iterations=100)

    depth_list = []

    # iterate over all the start months
    for month in range(1, 13, 1):
        borefield.load.start_month = month
        depth_list.append(borefield.size_L3())

    plt.figure()
    plt.bar(range(1, 13, 1), depth_list)
    plt.ylabel('Required borehole length [m]')
    plt.xlabel('First month of operation')
    plt.xlim(0)
    plt.ylim(0)
    plt.title('Required borehole length as a function of the first month of operation')
    plt.show()


if __name__ == "__main__":  # pragma: no cover
    start_in_different_month()
