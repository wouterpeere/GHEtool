# noinspection PyPackageRequirements
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
from GHEtool.Validation.cases import load_case

data = GroundConstantTemperature(3, 10)
ground_data_constant = data
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
    borefield.set_borefield(copy.deepcopy(borefield_gt))
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
    borefield = Borefield(borefield=copy.deepcopy(borefield_gt))
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
    borefield_test.create_rectangular_borefield(10, 10, 6, 6, 100, 1, 0.075)
    try:
        borefield_test.create_custom_dataset([100, 1000], [50, 100])
        assert False  # pragma: no cover
    except AssertionError:
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


def test_set_Rb():
    borefield = Borefield()
    borefield.set_Rb(0.2)
    assert borefield.Rb == 0.2
    borefield.set_Rb(0.3)
    assert borefield.Rb == 0.3
    borefield.Rb = 0.4
    assert borefield.Rb == 0.4
    assert borefield.Rb == borefield.borehole._Rb


def test_ground_data_custom_gfunction():
    borefield = Borefield(borefield=copy.deepcopy(borefield_gt))
    assert borefield.ground_data == GroundConstantTemperature()
    borefield.ground_data = ground_data_constant
    assert borefield.custom_gfunction is None

    # create custom data set
    borefield.create_custom_dataset()
    borefield.gfunction([5000, 10000], 150)
    assert not borefield.custom_gfunction is None

    # test for property setter
    borefield.ground_data = ground_data_constant
    assert borefield.ground_data == ground_data_constant
    assert borefield._ground_data == ground_data_constant
    assert borefield.custom_gfunction is None

    # create custom data set
    borefield.create_custom_dataset()
    borefield.gfunction([5000, 10000], 150)
    assert not borefield.custom_gfunction is None

    # test for set function
    borefield.set_ground_parameters(data_ground_flux)
    assert borefield.ground_data == data_ground_flux
    assert borefield._ground_data == data_ground_flux
    assert borefield.custom_gfunction is None


def test_ground_data_jit_gfunction():
    borefield = Borefield(borefield=copy.deepcopy(borefield_gt))
    assert borefield.ground_data == GroundConstantTemperature()
    borefield.ground_data = ground_data_constant

    # calculate gfunction
    borefield.gfunction([5000, 10000], 150)
    assert np.any(borefield.gfunction_calculation_object.depth_array)

    # test for property setter
    borefield.ground_data = ground_data_constant
    assert borefield.ground_data == ground_data_constant
    assert borefield._ground_data == ground_data_constant
    assert not np.any(borefield.gfunction_calculation_object.depth_array)

    # calculate gfunction
    borefield.gfunction([5000, 10000], 150)
    assert np.any(borefield.gfunction_calculation_object.depth_array)

    # test for set function
    borefield.set_ground_parameters(data_ground_flux)
    assert borefield.ground_data == data_ground_flux
    assert borefield._ground_data == data_ground_flux
    assert not np.any(borefield.gfunction_calculation_object.depth_array)


def test_set_fluid_params():
    borefield = Borefield()
    assert borefield.borehole.fluid_data == FluidData()
    borefield.set_fluid_parameters(fluidData)
    assert borefield.borehole.fluid_data == fluidData


def test_set_pipe_params():
    borefield = Borefield()
    assert borefield.borehole.pipe_data == PipeData()
    borefield.set_pipe_parameters(pipeData)
    assert borefield.borehole.pipe_data == pipeData


def test_set_Rb():
    borefield = Borefield()
    assert borefield.Rb == 0.12
    borefield.set_Rb(0.13)
    assert borefield.Rb == 0.13


def test_set_max_temp():
    borefield = Borefield()
    borefield.set_max_ground_temperature(13)
    assert borefield.Tf_max == 13
    borefield.set_max_ground_temperature(14)
    assert borefield.Tf_max == 14
    try:
        borefield.set_max_ground_temperature(borefield.Tf_min-1)
        assert False  # pragma: no cover
    except ValueError:
        assert True


def test_set_min_temp():
    borefield = Borefield()
    borefield.set_min_ground_temperature(3)
    assert borefield.Tf_min == 3
    borefield.set_min_ground_temperature(4)
    assert borefield.Tf_min == 4
    try:
        borefield.set_min_ground_temperature(borefield.Tf_max+1)
        assert False  # pragma: no cover
    except ValueError:
        assert True


def test_Tg():
    borefield = Borefield()
    borefield.set_ground_parameters(ground_data_constant)
    assert borefield._Tg() == borefield.ground_data.calculate_Tg(borefield.H)
    assert borefield._Tg(20) == borefield.ground_data.calculate_Tg(20)
    borefield.set_ground_parameters(data_ground_flux)
    assert borefield._Tg() == borefield.ground_data.calculate_Tg(borefield.H)
    assert borefield._Tg(20) == borefield.ground_data.calculate_Tg(20)


@pytest.mark.parametrize("ground_data, constant_Rb, result",
                         zip([ground_data_constant, data_ground_flux, ground_data_constant, data_ground_flux],
                             [True, True, False, False],
                             [30.924434615896764, 30.245606119498383, 30.924434615896764, 30.245606119498383]))
def test_Ahmadfard(ground_data, constant_Rb, result):
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(3)
    borefield.set_peak_heating(peak_heating)
    borefield.set_peak_cooling(peak_cooling)
    borefield.set_baseload_cooling(monthly_load_cooling)
    borefield.set_baseload_heating(monthly_load_heating)

    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluidData)
    borefield.set_pipe_parameters(pipeData)
    borefield.sizing_setup(use_constant_Rb=constant_Rb)
    borefield._calculate_last_year_params(True)
    assert np.isclose(result, borefield._Ahmadfard)
    assert np.isclose(result, borefield.H)

@pytest.mark.parametrize("ground_data, constant_Rb, result",
                         zip([ground_data_constant, data_ground_flux, ground_data_constant, data_ground_flux],
                             [True, True, False, False],
                             [38.53491016745154, 37.10078260823372, 38.53491016745154, 37.100782551185]))
def test_Carcel(ground_data, constant_Rb, result):
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(3)
    borefield.set_peak_heating(peak_heating)
    borefield.set_peak_cooling(peak_cooling)
    borefield.set_baseload_cooling(monthly_load_cooling)
    borefield.set_baseload_heating(monthly_load_heating)

    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluidData)
    borefield.set_pipe_parameters(pipeData)
    borefield.sizing_setup(use_constant_Rb=constant_Rb)
    borefield._calculate_first_year_params(True)
    assert np.isclose(result, borefield._Carcel)
    assert np.isclose(result, borefield.H)


def test_set_sizing_setup():
    borefield = Borefield()
    sizing_setup_backup = copy.deepcopy(borefield._sizing_setup)
    H_init_backup = borefield.H_init
    borefield.sizing_setup()
    assert borefield._sizing_setup == sizing_setup_backup
    assert borefield.H_init == H_init_backup
    # set sizing_setup
    test = SizingSetup(True, 4, False, True, False)
    test2 = SizingSetup(False, 3, False, False, True)
    borefield.sizing_setup(120, True, 4, False, True, False)
    assert borefield.H_init == 120
    assert borefield._sizing_setup == test
    assert borefield._sizing_setup == test
    borefield.sizing_setup(sizing_setup=test2)
    assert borefield.H_init == 120
    assert borefield._sizing_setup == test2


def test_size():
    borefield = Borefield()
    try:
        borefield.size()
        assert False  # pragma: no cover
    except ValueError:
        assert True
    borefield.borefield = copy.deepcopy(borefield_gt)
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(3)
    borefield.set_peak_heating(peak_heating)
    borefield.set_peak_cooling(peak_cooling)
    borefield.set_baseload_cooling(monthly_load_cooling)
    borefield.set_baseload_heating(monthly_load_heating)

    borefield.set_ground_parameters(ground_data_constant)
    sizing_setup_backup = copy.deepcopy(borefield._sizing_setup)
    borefield.size(L3_sizing=True)
    assert borefield._sizing_setup == sizing_setup_backup


def test_select_size():
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(3)
    borefield.set_peak_heating(peak_heating)
    borefield.set_peak_cooling(peak_cooling)
    borefield.set_baseload_cooling(monthly_load_cooling)
    borefield.set_baseload_heating(monthly_load_heating)

    # with constant Tg
    borefield.set_ground_parameters(ground_data_constant)
    assert borefield._select_size(100, 20) == 100
    assert borefield._select_size(10, 20) == 20

    # with variable Tg
    borefield.set_ground_parameters(data_ground_flux)
    assert borefield._select_size(100, 20) == 100
    assert borefield._select_size(10, 80) == 80
    borefield.set_max_ground_temperature(14)
    try:
        borefield._select_size(10, 80)
        assert False  # pragma: no cover
    except ValueError:
        assert True


def test_size_L2_value_errors():
    borefield = Borefield()
    try:
        borefield.size_L2(100)
        assert False  # pragma: no cover
    except ValueError:
        assert True
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(2)
    borefield.set_peak_heating(peak_heating)
    borefield.set_peak_cooling(peak_cooling)
    borefield.set_baseload_cooling(monthly_load_cooling)
    borefield.set_baseload_heating(monthly_load_heating)
    borefield.set_ground_parameters(ground_data_constant)
    try:
        borefield.size_L2(100, 5)
        assert False  # pragma: no cover
    except ValueError:
        assert True


@pytest.mark.parametrize("quadrant, result",
                         zip([1, 2, 3, 4], [74.55862437702756, 96.8819595625224, 27.20469151215654, 21.935797517893317]))
def test_size_L2(quadrant, result):
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(2)
    borefield.set_peak_heating(peak_heating)
    borefield.set_peak_cooling(peak_cooling)
    borefield.set_baseload_cooling(monthly_load_cooling)
    borefield.set_baseload_heating(monthly_load_heating)
    borefield.set_ground_parameters(ground_data_constant)

    assert np.isclose(result, borefield.size_L2(100, quadrant_sizing=quadrant))
    assert borefield.limiting_quadrant == quadrant
    assert np.isclose(result, borefield.H)


def test_size_L3_value_errors():
    borefield = Borefield()
    try:
        borefield.size_L3(100)
        assert False  # pragma: no cover
    except ValueError:
        assert True
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(2)
    borefield.set_peak_heating(peak_heating)
    borefield.set_peak_cooling(peak_cooling)
    borefield.set_baseload_cooling(monthly_load_cooling)
    borefield.set_baseload_heating(monthly_load_heating)
    borefield.set_ground_parameters(ground_data_constant)
    try:
        borefield.size_L3(100, 5)
        assert False  # pragma: no cover
    except ValueError:
        assert True

@pytest.mark.parametrize("quadrant, result",
                         zip([1, 2, 3, 4], [98.64768654650995, 98.64768654650995, 26.722846792067735, 26.722846792067735]))
def test_size_L3(quadrant, result):
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(2)
    borefield.set_peak_heating(peak_heating)
    borefield.set_peak_cooling(peak_cooling)
    borefield.set_baseload_cooling(monthly_load_cooling)
    borefield.set_baseload_heating(monthly_load_heating)
    borefield.set_ground_parameters(ground_data_constant)

    assert np.isclose(result, borefield.size_L3(100, quadrant_sizing=quadrant))
    assert np.isclose(result, borefield.H)
