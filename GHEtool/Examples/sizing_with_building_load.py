"""
This document contains an example on sizing with a building load and different resolutions for the COP data.
It is shown that sizing with a fixed SCOP can lead to oversizing.
Please note that using a variable cop with a monthly dataset is not without risk, since there is no detailed information
about the part load power.
"""

import numpy as np
import pygfunction as gt

from GHEtool import *
from typing import Tuple

# define building loads in kWh/year
building_demand_heating = np.array(
    [26.37, 23.34, 19.55, 13.03, 6.67, 2.88, 0.91, 0.76, 3.94, 10.61, 18.49, 25]) * 1000
building_demand_cooling = np.array([0, 0, 0, 0, 3.56, 5.33, 12.44, 12.44, 1.78, 0, 0, 0]) * 1000
building_peak_heating = np.array([85, 85, 85, 85, 85, 0, 0, 85, 85, 85, 85, 85])
building_peak_cooling = np.zeros(12)
building_demand_DHW = 88_030

ground_data = GroundFluxTemperature(1.5, 11, flux=0.07)
pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.42, 0.0425)
fluid_data = FluidData(k_f=0.475, rho=1033, Cp=3930, mu=0.0079, vfr=0.186)


def size_with_scop() -> Tuple[float, float]:
    """
    Size the borefield using a constant value for the cop and eer.

    Returns
    -------
    Depth : float
        Required borehole depth
    """
    scop = SCOP(4.5)
    seer = SEER(1000)
    scop_dhw = SCOP(3.5)
    load = MonthlyBuildingLoadAbsolute(building_demand_heating,
                                       building_demand_cooling,
                                       building_peak_heating,
                                       building_peak_cooling,
                                       25, scop, seer, building_demand_DHW, scop_dhw)
    load.peak_duration = 18
    load.start_month = 9

    # create borefield object
    borefield = Borefield(load=load)
    borefield.ground_data = ground_data
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)

    borefield.create_rectangular_borefield(3, 14, 7, 7, 94, r_b=0.0655)

    depth = borefield.size_L3(100)
    print(f'When sizing with a constant SCOP, the required borehole depth is {depth:.2f}m. The SCOP (incl. DHW) is '
          f'{borefield.load.SCOP_total:.2f}.')
    borefield.print_temperature_profile()
    return depth, borefield.load.SCOP_total


def size_with_variable_ground_temperature() -> Tuple[float, float]:
    """
    Size the borefield using cop that depends on the average primary temperature.

    Returns
    -------
    Depth : float
        Required borehole depth
    """
    seer = SEER(1000)
    cop = COP(np.array([3.76, 4.25, 4.79, 5.34, 5.74]), np.array([-5, 0, 5, 10, 15]))
    cop_dhw = COP(np.array([2.52, 2.84, 3.2, 3.61, 3.96]), np.array([-5, 0, 5, 10, 15]))
    load = MonthlyBuildingLoadAbsolute(building_demand_heating,
                                       building_demand_cooling,
                                       building_peak_heating,
                                       building_peak_cooling,
                                       25, cop, seer, building_demand_DHW, cop_dhw)
    load.peak_duration = 18
    load.start_month = 9

    # create borefield object
    borefield = Borefield(load=load)
    borefield.ground_data = ground_data
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)

    borefield.create_rectangular_borefield(3, 14, 7, 7, 94, r_b=0.0655)

    depth = borefield.size_L3(100)
    print(f'When sizing with a inlet temperature dependent COP, the required borehole depth is {depth:.2f}m. '
          f'The SCOP (incl. DHW) is {borefield.load.SCOP_total:.2f}.')
    borefield.print_temperature_profile()
    return depth, borefield.load.SCOP_total


def size_with_part_load_data() -> Tuple[float, float]:
    """
    Size the borefield using cop that depends on both the average primary temperature and the part load data.

    Returns
    -------
    Depth : float
        Required borehole depth
    """
    seer = SEER(1000)
    cop = COP(np.array(
        [4.42, 5.21, 6.04, 7.52, 9.5, 3.99, 4.58, 5.21, 6.02, 6.83, 3.86, 4.39, 4.97,
         5.62, 6.19, 3.8, 4.3, 4.86, 5.44, 5.9, 3.76, 4.25, 4.79, 5.34, 5.74]),
        np.array([[-5, 1.06], [0, 1.25], [5, 1.45], [10, 1.66], [15, 1.9], [-5, 2.05], [0, 2.42], [5, 2.81], [10, 3.2],
                  [15, 3.54], [-5, 3.05], [0, 3.6], [5, 4.17], [10, 4.73], [15, 5.18], [-5, 4.04], [0, 4.77], [5, 5.54],
                  [10, 6.27], [15, 6.82], [-5, 5.03], [0, 5.95], [5, 6.9], [10, 7.81], [15, 8.46]]),
        part_load=True, reference_nominal_power=1, nominal_power=9)

    cop_dhw = COP(np.array(
        [2.88, 3.21, 3.63, 4.04, 4.51, 2.64, 2.97, 3.35, 3.76, 4.15, 2.57, 2.9, 3.27, 3.68, 4.04, 2.54, 2.86, 3.23,
         3.64, 3.99, 2.52, 2.84, 3.2, 3.61, 3.96]),
        np.array([[-5, 1.06], [0, 1.25], [5, 1.45], [10, 1.66], [15, 1.9], [-5, 2.05], [0, 2.42], [5, 2.81],
                  [10, 3.2], [15, 3.54], [-5, 3.05], [0, 3.6], [5, 4.17], [10, 4.73], [15, 5.18], [-5, 4.04],
                  [0, 4.77], [5, 5.54], [10, 6.27], [15, 6.82], [-5, 5.03], [0, 5.95], [5, 6.9], [10, 7.81],
                  [15, 8.46]]), part_load=True, reference_nominal_power=1, nominal_power=9)

    load = MonthlyBuildingLoadAbsolute(building_demand_heating,
                                       building_demand_cooling,
                                       building_peak_heating,
                                       building_peak_cooling,
                                       25, cop, seer, building_demand_DHW, cop_dhw)
    load.peak_duration = 18
    load.start_month = 9

    # create borefield object
    borefield = Borefield(load=load)
    borefield.ground_data = ground_data
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)

    borefield.create_rectangular_borefield(3, 14, 7, 7, 94, r_b=0.0655)

    depth = borefield.size_L3(100)
    print(
        f'When sizing with a inlet temperature and part-load dependent COP, the required borehole depth is {depth:.2f}m. '
        f'The SCOP (incl. DHW) is {borefield.load.SCOP_total:.2f}.')
    borefield.print_temperature_profile()
    return depth, borefield.load.SCOP_total


if __name__ == "__main__":
    size_with_scop()
    size_with_variable_ground_temperature()
    size_with_part_load_data()
