"""
This document contains an example on sizing with an hourly building load and the difference between L3 and L4 sizing.
It can be seen that sizing with an hourly method not only gives a completely different result, but also that the SCOP
differs and is more accurate.
"""

import numpy as np
import pygfunction as gt

from GHEtool import *
from typing import Tuple

# initiate ground data
data = GroundFluxTemperature(2.1, 10, flux=0.07)
borefield_gt = gt.boreholes.rectangle_field(10, 12, 6, 6, 110, 1, 0.075)

cop = COP(np.array(
    [4.42, 5.21, 6.04, 7.52, 9.5, 3.99, 4.58, 5.21, 6.02, 6.83, 3.86, 4.39, 4.97,
     5.62, 6.19, 3.8, 4.3, 4.86, 5.44, 5.9, 3.76, 4.25, 4.79, 5.34, 5.74]),
    np.array([[-5, 1.06], [0, 1.25], [5, 1.45], [10, 1.66], [15, 1.9], [-5, 2.05], [0, 2.42], [5, 2.81], [10, 3.2],
              [15, 3.54], [-5, 3.05], [0, 3.6], [5, 4.17], [10, 4.73], [15, 5.18], [-5, 4.04], [0, 4.77], [5, 5.54],
              [10, 6.27], [15, 6.82], [-5, 5.03], [0, 5.95], [5, 6.9], [10, 7.81], [15, 8.46]]),
    part_load=True, reference_nominal_power=1, nominal_power=550)


def L3_sizing() -> Tuple[float, float]:
    """
    Size the borefield with a monthly sizing method.

    Returns
    -------
    length, SCOP
    """
    # initiate borefield
    borefield = Borefield()

    # set parameters
    borefield.set_min_avg_fluid_temperature(0)
    borefield.set_max_avg_fluid_temperature(25)

    # set ground data in borefield
    borefield.ground_data = data

    # set Rb
    borefield.Rb = 0.12

    # set borefield
    borefield.set_borefield(borefield_gt)

    # load the hourly profile
    load = HourlyBuildingLoad(efficiency_heating=cop)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"), header=True, separator=";")
    borefield.load = load

    # size the borefield and plot the resulting temperature evolution
    length = borefield.size(100, L3_sizing=True)
    print(
        f'When sizing with an L3 method, the required borehole length is {length:.2f}m. '
        f'The SCOP is {borefield.load.SCOP_total:.2f}.')
    borefield.print_temperature_profile()
    return length, borefield.load.SCOP_heating


def L4_sizing() -> Tuple[float, float]:
    """
    Size the borefield with an hourly sizing method.

    Returns
    -------
    length, SCOP
    """
    # initiate borefield
    borefield = Borefield()

    # set parameters
    borefield.set_min_avg_fluid_temperature(3)
    borefield.set_max_avg_fluid_temperature(25)

    # set ground data in borefield
    borefield.ground_data = data

    # set Rb
    borefield.Rb = 0.12

    # set borefield
    borefield.set_borefield(borefield_gt)

    # load the hourly profile
    load = HourlyBuildingLoad(efficiency_heating=cop)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"), header=True, separator=";")
    borefield.load = load

    # size the borefield and plot the resulting temperature evolution
    length = borefield.size(100, L4_sizing=True)
    print(
        f'When sizing with an L4 method, the required borehole length is {length:.2f}m. '
        f'The SCOP is {borefield.load.SCOP_total:.2f}.')
    borefield.print_temperature_profile(plot_hourly=True)
    return length, borefield.load.SCOP_heating


if __name__ == "__main__":
    L3_sizing()
    L4_sizing()
