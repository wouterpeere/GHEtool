import numpy as np
import pygfunction as gt
from GHEtool import GroundConstantTemperature, Borefield, HourlyGeothermalLoad, FOLDER
from scipy.signal import convolve
from math import pi
from time import process_time_ns


def test_new_calc_method(simulation_period: int):
    """
    Test the new calculation method which is just considering the first and last year.

    Parameters
    ----------
    simulation_period : int
        simulation period [years]

    Returns
    -------
        None

    Raises
    -------
        AssertionError
    """

    h = 110

    # initiate ground data
    data = GroundConstantTemperature(3, 10)

    # initiate pygfunction borefield model
    borefield_gt = gt.boreholes.rectangle_field(10, 10, 6, 6, 110, 1, 0.075)

    # initiate borefield
    borefield = Borefield(100)

    # set borehole thermal equivalent resistance
    borefield.Rb = 0.12

    # set ground data in borefield
    borefield.set_ground_parameters(data)

    # set pygfunction borefield model
    borefield.set_borefield(borefield_gt)


    # load the hourly profile
    load = HourlyGeothermalLoad(simulation_period=simulation_period)
    load.load_hourly_profile(f'hourly_profile.csv', header=True, separator=";")

    borefield.load = load

    # borefield.g-function is a function that uses the precalculated data to interpolate the correct values of the
    # g-function. This dataset is checked over and over again and is correct
    g_values = borefield.gfunction(borefield.time_L4, borefield.H)

    # get process time at start of new method
    dt1 = process_time_ns()
    # determine load
    loads_short = borefield.hourly_cooling_load - borefield.hourly_heating_load
    # reverse the load
    loads_short_rev = loads_short[::-1]
    # init results vector
    results = np.zeros(loads_short.size * 2)
    # calculation of needed differences of the g-function values. These are the weight factors in the calculation
    # of Tb.
    g_value_differences = np.diff(g_values, prepend=0)

    # convolution to get the results for the first year
    results[:8760] = convolve(loads_short * 1000, g_value_differences[:8760])[:8760]
    # sum up g_values until the pre last year
    g_sum_n1 = g_value_differences[:8760 * (borefield.simulation_period - 1)].reshape(borefield.simulation_period - 1, 8760).sum(axis=0)
    # add up last year
    g_sum = g_sum_n1 + g_value_differences[8760 * (borefield.simulation_period - 1):]
    # add zero at start and reverse the order
    g_sum_n2 = np.concatenate((np.array([0]), g_sum_n1[::-1]))[:-1]
    # determine results for the last year by the influence of the year (first term) and the previous years (last term)
    results[8760:] = convolve(loads_short * 1000, g_sum)[:8760] + convolve(loads_short_rev * 1000, g_sum_n2)[:8760][::-1]
    # calculation the borehole wall temperature for every month i
    t_b = results / (2 * pi * borefield.ground_data.k_s) / (borefield.H * borefield.number_of_boreholes) + borefield._Tg(borefield.H)

    # get process time
    dt2 = process_time_ns()
    # determine hourly load
    hourly_load = np.tile(borefield.hourly_cooling_load - borefield.hourly_heating_load, borefield.simulation_period)
    # calculation of needed differences of the g-function values. These are the weight factors in the calculation
    # of Tb.
    g_value_differences = np.diff(g_values, prepend=0)

    # convolution to get the monthly results
    results = convolve(hourly_load * 1000, g_value_differences)[:hourly_load.size]

    # calculation the borehole wall temperature for every month i
    t_b_new = results / (2 * pi * borefield.ground_data.k_s) / (h * borefield.number_of_boreholes) + borefield._Tg(h)

    # print time for the different methods
    print(f'simulation period: {simulation_period}; old: {(process_time_ns() - dt2)/1000:.0f} µs;'
          f'new: {(dt2 - dt1)/1000:.0f} µs')
    # compare results to ensure they are the same
    assert np.allclose(t_b[:8760], t_b_new[:8760])
    assert np.allclose(t_b[8760:], t_b_new[8760*(borefield.simulation_period - 1):])


if __name__ == "__main__":
    for sim_year in np.arange(5, 101, 10):
        test_new_calc_method(sim_year)
