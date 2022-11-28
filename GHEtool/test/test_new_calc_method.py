import numpy as np
import pygfunction as gt
from GHEtool import GroundData, Borefield
from GHEtool.main_class import FOLDER
from scipy.signal import convolve
from math import pi
from time import process_time_ns


def test_new_calc_method():

    h = 110

    # initiate ground data
    data = GroundData(3, 10, 0.12)

    # initiate pygfunction borefield model
    borefield_gt = gt.boreholes.rectangle_field(10, 10, 6, 6, 110, 1, 0.075)

    # initiate borefield
    borefield = Borefield(100)

    # set ground data in borefield
    borefield.set_ground_parameters(data)

    # set pygfunction borefield model
    borefield.set_borefield(borefield_gt)

    borefield.set_simulation_period(100)

    # load the hourly profile
    borefield.load_hourly_profile(f"{FOLDER}/Examples/hourly_profile.csv", header=True, separator=";", first_column_heating=True)

    # borefield.g-function is a function that uses the precalculated data to interpolate the correct values of the
    # g-function. This dataset is checked over and over again and is correct
    g_values = borefield.gfunction(borefield.time_L4, borefield.H)

    dt1 = process_time_ns()

    loads_short = borefield.hourly_cooling_load - borefield.hourly_heating_load
    loads_short_rev = loads_short[::-1]

    results = np.zeros(loads_short.size * 2)
    # calculation of needed differences of the g-function values. These are the weight factors in the calculation
    # of Tb. Last element removed in order to make arrays the same length
    g_value_previous_step = np.concatenate((np.array([0]), g_values))[:-1]
    g_value_differences = g_values - g_value_previous_step

    # convolution to get the monthly results
    results[:8760] = convolve(loads_short * 1000, g_value_differences[:8760])[:8760]

    g_sum_n1 = g_value_differences[:8760 * (borefield.simulation_period - 1)].reshape(borefield.simulation_period - 1, 8760).sum(axis=0)
    g_sum = g_sum_n1 + g_value_differences[8760 * (borefield.simulation_period - 1):]
    g_sum_n2 = np.concatenate((np.array([0]), g_sum_n1[::-1]))[:-1]

    results[8760:] = convolve(loads_short * 1000, g_sum)[:8760] + convolve(loads_short_rev * 1000, g_sum_n2)[:8760][::-1]

    # calculation the borehole wall temperature for every month i
    t_b = results / (2 * pi * borefield.k_s) / (borefield.H * borefield.number_of_boreholes) + borefield._Tg(borefield.H)
    print('')
    print(f'new: {(process_time_ns() - dt1):_.0f} ns')
    dt1 = process_time_ns()

    hourly_load = np.tile(borefield.hourly_cooling_load - borefield.hourly_heating_load, borefield.simulation_period)

    # calculation of needed differences of the g-function values. These are the weight factors in the calculation
    # of Tb. Last element removed in order to make arrays the same length
    g_value_previous_step = np.concatenate((np.array([0]), g_values))[:-1]
    g_value_differences = g_values - g_value_previous_step

    # convolution to get the monthly results
    results = convolve(hourly_load * 1000, g_value_differences)[:hourly_load.size]

    # calculation the borehole wall temperature for every month i
    t_b_new = results / (2 * pi * borefield.k_s) / (h * borefield.number_of_boreholes) + borefield._Tg(h)
    print(f'old: {(process_time_ns() - dt1):_.0f} ns')

    assert np.allclose(t_b[:8760], t_b_new[:8760])
    assert np.allclose(t_b[8760:], t_b_new[8760*99:])

