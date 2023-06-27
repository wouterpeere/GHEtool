import copy
from math import isclose

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pygfunction as gt
import pytest
from pytest import raises

from GHEtool import GroundConstantTemperature, GroundFluxTemperature, FluidData, PipeData, Borefield, SizingSetup, FOLDER
from GHEtool.logger import ghe_logger

data = GroundConstantTemperature(3, 10)
data_ground_flux = GroundFluxTemperature(3, 10)
fluidData = FluidData(0.2, 0.568, 998, 4180, 1e-3)
pipeData = PipeData(1, 0.015, 0.02, 0.4, 0.05, 2)

borefield_gt = gt.boreholes.rectangle_field(10, 12, 6, 6, 110, 4, 0.075)

# Monthly loading values
peakCooling = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]              # Peak cooling in kW
peakHeating = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]             # Peak heating in kW

# annual heating and cooling load
annualHeatingLoad = 300*10**3  # kWh
annualCoolingLoad = 160*10**3  # kWh

# percentage of annual load per month (15.5% for January ...)
monthlyLoadHeatingPercentage = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144]
monthlyLoadCoolingPercentage = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]

# resulting load per month
monthlyLoadHeating = list(map(lambda x: x * annualHeatingLoad, monthlyLoadHeatingPercentage))   # kWh
monthlyLoadCooling = list(map(lambda x: x * annualCoolingLoad, monthlyLoadCoolingPercentage))   # kWh


def borefields_equal(borefield_one, borefield_two) -> bool:
    for i in range(len(borefield_one)):
        if borefield_one[i].__dict__ != borefield_two[i].__dict__:
            return False
    return True


@pytest.fixture
def borefield():
    borefield = Borefield(simulation_period=20,
                          peak_heating=peakHeating,
                          peak_cooling=peakCooling,
                          baseload_heating=monthlyLoadHeating,
                          baseload_cooling=monthlyLoadCooling)

    borefield.set_ground_parameters(data)
    borefield.set_borefield(borefield_gt)
    borefield.set_Rb(0.2)

    # set temperature boundaries
    borefield.set_max_ground_temperature(16)  # maximum temperature
    borefield.set_min_ground_temperature(0)  # minimum temperature
    return borefield


def test_logging():
    borefield = Borefield()
    assert ghe_logger.level == 20
    borefield.activate_logger()
    assert ghe_logger.level == 15
    borefield.deactivate_logger()
    assert ghe_logger.level == 20


def test_nb_of_boreholes():
    borefield = Borefield()
    assert borefield.number_of_boreholes == 0
    borefield = Borefield(borefield=borefield_gt)
    borefield.set_ground_parameters(data_ground_flux)
    assert borefield.number_of_boreholes == 120
    borefield.set_borefield(gt.boreholes.rectangle_field(5, 5, 6, 6, 110, 0.1, 0.07))
    assert borefield.H == 110
    assert borefield.r_b == 0.07
    assert borefield.D == 0.1
    assert borefield.number_of_boreholes == 25
    borefield.gfunction(5000, 110)
    assert np.any(borefield.gfunction_calculation_object.depth_array)
    borefield.borefield = gt.boreholes.rectangle_field(6, 5, 6, 6, 100, 1, 0.075)
    assert not np.any(borefield.gfunction_calculation_object.depth_array)
    assert borefield.H == 100
    assert borefield.r_b == 0.075
    assert borefield.D == 1
    temp = copy.deepcopy(borefield.gfunction_calculation_object)
    borefield.gfunction(5000, 110)
    assert np.any(borefield.gfunction_calculation_object.depth_array)
    assert borefield.number_of_boreholes == 30
    borefield.borefield = None
    assert not np.any(borefield.gfunction_calculation_object.depth_array)
    assert borefield.gfunction_calculation_object
    assert borefield.number_of_boreholes == 0
    borefield.borefield = gt.boreholes.rectangle_field(6, 5, 6, 6, 100, 1, 0.075)
    borefield.gfunction(5000, 110)
    assert np.any(borefield.gfunction_calculation_object.depth_array)
    borefield.set_borefield(None)
    assert not np.any(borefield.gfunction_calculation_object.depth_array)
    assert borefield.number_of_boreholes == 0


def test_create_rectangular_field(borefield):
    borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
    assert borefield.number_of_boreholes == 100
    borefields_equal(borefield.borefield, gt.boreholes.rectangle_field(10, 10, 6, 6, 110, 4, 0.075))


def test_create_circular_field(borefield):
    borefield.create_circular_borefield(10, 10, 100, 1)
    assert borefield.number_of_boreholes == 10
    borefields_equal(borefield.borefield, gt.boreholes.circle_field(10, 10, 100, 1, 0.075))


def test_update_depth(borefield):
    init_H = borefield.borefield[0].H

    borefield.H = init_H + 1
    borefield._update_borefield_depth()
    for bor in borefield.borefield:
        assert bor.H == init_H + 1

    borefield._update_borefield_depth(init_H + 2)
    for bor in borefield.borefield:
        assert bor.H == init_H + 2

    borefield._update_borefield_depth(init_H + 2)
    for bor in borefield.borefield:
        assert bor.H == init_H + 2

def test_create_custom_dataset(borefield):
    borefield_test = Borefield()
    try:
        borefield_test.create_custom_dataset([100, 1000], [50, 100])
        assert False  # pragma: no cover
    except ValueError:
        assert True
    borefield.create_rectangular_borefield(10, 10, 6, 6, 100, 1, 0.075)
    try:
        borefield_test.create_custom_dataset([100, 1000], [50, 100])
        assert False  # pragma: no cover
    except ValueError:
        assert True


@pytest.mark.slow
def test_load_custom_gfunction(borefield):
    borefield.create_custom_dataset()
    borefield.custom_gfunction.dump_custom_dataset("./", "test")
    dataset = copy.copy(borefield.custom_gfunction)
    borefield.borefield = None
    assert borefield.custom_gfunction is None
    borefield.custom_gfunction = dataset
    borefield.set_borefield(None)
    assert borefield.custom_gfunction is None
    borefield.load_custom_gfunction("./test.gvalues")
    assert borefield.custom_gfunction == dataset


def test_set_investment_cost(borefield):
    borefield.set_investment_cost()
    assert borefield.cost_investment == Borefield.DEFAULT_INVESTMENT
    borefield.set_investment_cost([0, 39])
    assert borefield.cost_investment == [0, 39]


def test_set_length_peak():
    borefield = Borefield()
    borefield.set_length_peak_heating(8)
    borefield.set_length_peak_cooling(10)
    assert borefield.length_peak_cooling == 10
    assert borefield.length_peak_heating == 8
    borefield.set_length_peak(12)
    assert borefield.length_peak_cooling == 12
    assert borefield.length_peak_heating == 12
    borefield.set_length_peak_cooling()
    borefield.set_length_peak_heating()
    assert borefield.length_peak_heating == 6
    assert borefield.length_peak_cooling == 6
    borefield.set_length_peak_heating(8)
    borefield.set_length_peak_cooling(10)
    borefield.set_length_peak()
    assert borefield.length_peak_heating == 6
    assert borefield.length_peak_cooling == 6


def test_simulation_period():
    borefield = Borefield(simulation_period=20)
    assert borefield.simulation_period == 20
    assert len(borefield.time_L3_last_year) == 12 * 20
    borefield = Borefield(simulation_period=25)
    assert borefield.simulation_period == 25
    assert len(borefield.time_L3_last_year) == 12 * 25
    borefield.set_simulation_period(40)
    assert borefield.simulation_period == 40
    assert len(borefield.time_L3_last_year) == 12 * 40



