# test if model can be imported
import numpy as np
import pytest
import copy
from math import isclose

from GHEtool import *

import pygfunction as gt

data = GroundData(3, 10, 0.2)
fluidData = FluidData(0.2, 0.568, 998, 4180, 1e-3)
pipeData = PipeData(1, 0.015, 0.02, 0.4, 0.05, 2)

borefield_gt = gt.boreholes.rectangle_field(10, 12, 6, 6, 110, 4, 0.075)


def load_case(number):
    """This function returns the values for one of the four cases."""
    if number == 4:
        # case 4
        # limited in the last year by heating
        monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
        monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
        monthly_load_heating = monthly_load_heating_percentage * 300 * 10 ** 3  # kWh
        monthly_load_cooling = monthly_load_cooling_percentage * 150 * 10 ** 3  # kWh
        peak_cooling = np.array([0., 0., 22., 44., 83., 117., 134., 150., 100., 23., 0., 0.])
        peak_heating = np.array([300., 268., 191., 103., 75., 0., 0., 38., 76., 160., 224., 255.])

    return monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating


def test_different_heating_cooling_peaks():
    # Monthly loading values
    peakCooling = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]  # Peak cooling in kW
    peakHeating = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]  # Peak heating in kW

    # annual heating and cooling load
    annualHeatingLoad = 300 * 10 ** 3  # kWh
    annualCoolingLoad = 160 * 10 ** 3  # kWh

    # percentage of annual load per month (15.5% for January ...)
    monthlyLoadHeatingPercentage = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144]
    monthlyLoadCoolingPercentage = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]

    # resulting load per month
    monthlyLoadHeating = list(map(lambda x: x * annualHeatingLoad, monthlyLoadHeatingPercentage))  # kWh
    monthlyLoadCooling = list(map(lambda x: x * annualCoolingLoad, monthlyLoadCoolingPercentage))  # kWh

    borefield = Borefield(simulation_period=20,
                          peak_heating=peakHeating,
                          peak_cooling=peakCooling,
                          baseload_heating=monthlyLoadHeating,
                          baseload_cooling=monthlyLoadCooling)

    borefield.set_ground_parameters(data)
    borefield.set_borefield(copy.copy(borefield_gt))

    # set temperature boundaries
    borefield.set_max_ground_temperature(16)  # maximum temperature
    borefield.set_min_ground_temperature(0)  # minimum temperature
    borefield.set_length_peak_cooling(8)
    assert borefield.length_peak_cooling == 8
    assert borefield.length_peak_heating == 6
    assert np.isclose(borefield.size(), 94.05270927679376)
    assert borefield.length_peak_cooling == 8
    assert borefield.length_peak_heating == 6


def test_stuck_in_loop():
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(4)

    borefield = Borefield(simulation_period=20,
                          peak_heating=peak_heating,
                          peak_cooling=peak_cooling,
                          baseload_heating=monthly_load_heating,
                          baseload_cooling=monthly_load_cooling)

    borefield.set_ground_parameters(data)
    borefield.set_borefield(copy.copy(borefield_gt))

    # set temperature boundaries
    borefield.set_max_ground_temperature(16)  # maximum temperature
    borefield.set_min_ground_temperature(0)  # minimum temperature

    borefield.size()
    borefield.set_length_peak_cooling(8)
    borefield.set_length_peak_heating(8)
    assert borefield.length_peak_cooling == 8
    assert borefield.length_peak_heating == 8
    borefield.size()
    assert np.isclose(borefield.size(), 100.91784885721547)
