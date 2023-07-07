# test if model can be imported
import copy
from math import isclose

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pygfunction as gt
import pytest
from pytest import raises

from GHEtool import GroundConstantTemperature, GroundFluxTemperature, FluidData, PipeData, Borefield, SizingSetup, FOLDER
from GHEtool.Validation.cases import load_case

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

custom_field = gt.boreholes.L_shaped_field(N_1=4, N_2=5, B_1=5., B_2=5., H=100., D=4, r_b=0.05)


def test_borefield():
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

    assert borefield.simulation_period == 20
    assert borefield.Tf_min == 0
    assert borefield.Tf_max == 16
    np.testing.assert_array_equal(borefield.peak_heating, np.array([160., 142, 102., 55., 26.301369863013697, 0., 0., 0., 40.4, 85., 119., 136.]))


@pytest.fixture
def borefield_quadrants():
    data = GroundConstantTemperature(3.5,  # conductivity of the soil (W/mK)
                                     10)  # Ground temperature at infinity (degrees C)

    borefield_gt = gt.boreholes.rectangle_field(10, 12, 6.5, 6.5, 110, 4, 0.075)

    borefield = Borefield()
    borefield.set_Rb(0.2)
    borefield.set_ground_parameters(data)
    borefield.set_borefield(borefield_gt)

    return borefield


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


@pytest.fixture
def borefield_custom_data():
    borefield = Borefield(simulation_period=20,
                          peak_heating=peakHeating,
                          peak_cooling=peakCooling,
                          baseload_heating=monthlyLoadHeating,
                          baseload_cooling=monthlyLoadCooling)

    borefield.set_ground_parameters(data)
    borefield.set_borefield(borefield_gt)
    borefield.set_Rb(0.2)
    borefield.create_custom_dataset()

    # set temperature boundaries
    borefield.set_max_ground_temperature(16)  # maximum temperature
    borefield.set_min_ground_temperature(0)  # minimum temperature
    return borefield


@pytest.fixture
def hourly_borefield():
    borefield = Borefield()
    borefield.set_ground_parameters(data)
    borefield.set_Rb(0.2)
    borefield.set_borefield(borefield_gt)
    borefield.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    return borefield


@pytest.fixture
def borefield_cooling_dom():
    borefield = Borefield(simulation_period=20,
                          peak_heating=peakHeating,
                          peak_cooling=peakCooling,
                          baseload_heating=monthlyLoadHeating,
                          baseload_cooling=monthlyLoadCooling)

    borefield.set_baseload_cooling(np.array(monthlyLoadCooling)*2)

    borefield.set_ground_parameters(data)
    borefield.set_Rb(0.2)
    borefield.set_borefield(borefield_gt)

    return borefield


def test_hourly_to_monthly(borefield):
    borefield.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"), header=True, separator=";", first_column_heating=True)
    borefield.convert_hourly_to_monthly()
    borefield.size()

    assert np.isclose(np.sum(borefield.baseload_cooling), np.sum(borefield.hourly_cooling_load))
    assert np.isclose(np.sum(borefield.baseload_heating), np.sum(borefield.hourly_heating_load))
    # check if hourly imbalance equals the monthly imbalance
    assert np.isclose(borefield.imbalance, np.sum(borefield.baseload_cooling) - np.sum(borefield.baseload_heating))


def test_imbalance(borefield):
    assert borefield.imbalance == -140000.0


def test_sizing_L3_threshold_depth_error(borefield):
    max_temp = borefield.Tf_max
    borefield.set_max_ground_temperature(14)
    borefield.set_ground_parameters(data_ground_flux)
    borefield._sizing_setup.use_constant_Tg = False
    with raises(ValueError):
        borefield.gfunction(3600, borefield.THRESHOLD_DEPTH_ERROR + 1)
    borefield._sizing_setup.use_constant_Tg = True
    borefield.set_max_ground_temperature(max_temp)
    borefield.ground_data.flux = 0


def test_sizing_L32(borefield_cooling_dom):
    borefield_cooling_dom.size(L3_sizing=True)
    borefield_cooling_dom.set_peak_heating(np.array(peakHeating) * 5)
    borefield_cooling_dom.size(L3_sizing=True)


def test_plot_hourly(monkeypatch, hourly_borefield):
    monkeypatch.setattr(plt, 'show', lambda: None)
    hourly_borefield.print_temperature_profile(plot_hourly=True)


def test_load_duration_no_hourly_data(borefield):
    with raises(ValueError):
        borefield.plot_load_duration()


def test_precalculated_data_1(borefield_custom_data):
    borefield_custom_data.gfunction([3600*100, 3600*100], 100)


def test_precalculated_data_2(borefield_custom_data):
    borefield_custom_data.gfunction([3600*100, 3600*100, 3600*101], 100)


def test_choose_quadrant_None(borefield_quadrants):
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(4)

    borefield_quadrants.set_peak_heating(peak_heating)
    borefield_quadrants.set_peak_cooling(peak_cooling)
    borefield_quadrants.set_baseload_cooling(monthly_load_cooling)
    borefield_quadrants.set_baseload_heating(monthly_load_heating)

    borefield_quadrants.calculate_temperatures(200)
    assert None is borefield_quadrants.calculate_quadrant()


@pytest.mark.slow
def test_load_custom_gfunction(borefield):
    borefield.create_custom_dataset()
    borefield.custom_gfunction.dump_custom_dataset("./", "test")
    dataset = copy.copy(borefield.custom_gfunction)

    borefield.load_custom_gfunction("./test.gvalues")
    assert borefield.custom_gfunction == dataset


def test_H_smaller_50(borefield):
    borefield.H = 0.5
    borefield.size_L2(H_init=0.5, quadrant_sizing=1)


def test_size_hourly_without_hourly_load(borefield):
    with raises(ValueError):
        borefield.size_L4(H_init=100)
    borefield.hourly_heating_load = None
    borefield.hourly_cooling_load = None
    with raises(ValueError):
        borefield.size_L4(H_init=100)


def test_size_hourly_quadrant(hourly_borefield):
    hourly_borefield.H = 0.5
    hourly_borefield.size_L4(H_init=100, quadrant_sizing=1)


def test_create_custom_dataset_without_data(borefield):
    borefield.ground_data = None
    with raises(ValueError):
        borefield.create_custom_dataset()
    borefield.borefield = None
    with raises(ValueError):
        borefield.create_custom_dataset()


def test_check_hourly_load(borefield):
    with raises(ValueError):
        borefield._check_hourly_load()

    borefield.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    borefield.hourly_cooling_load[0] = -1
    with raises(ValueError):
        borefield._check_hourly_load()
    borefield.hourly_cooling_load[0] = 0
    borefield.hourly_cooling_load = borefield.hourly_cooling_load[:20]
    with raises(ValueError):
        borefield._check_hourly_load()


def test_load_hourly_data(borefield):
    borefield.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    test_cooling = copy.copy(borefield.hourly_cooling_load)
    borefield.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"), first_column_heating=False)
    assert np.array_equal(test_cooling, borefield.hourly_heating_load)

    borefield.load_hourly_profile(FOLDER.joinpath("test/methods/hourly data/hourly_profile_without_header.csv"), header=False)
    assert np.array_equal(test_cooling, borefield.hourly_cooling_load)


def test_convert_hourly_to_monthly_without_data(borefield):
    with raises(IndexError):
        borefield.convert_hourly_to_monthly()
    borefield.set_fluid_parameters(fluidData)
    borefield.set_pipe_parameters(pipeData)
    borefield._sizing_setup.use_constant_Rb = False
    with raises(ValueError):
        borefield.optimise_load_profile()


def test_calculate_hourly_temperature_profile(hourly_borefield):
    hourly_borefield._calculate_temperature_profile(100, hourly=True)
    hourly_borefield.hourly_heating_load_on_the_borefield = hourly_borefield.hourly_heating_load
    hourly_borefield.hourly_cooling_load_on_the_borefield = hourly_borefield.hourly_cooling_load


def test_incorrect_values_peak_baseload(borefield):
    with raises(ValueError):
        borefield.set_peak_heating(8)

    with raises(ValueError):
        borefield.set_peak_cooling(8)

    with raises(ValueError):
        borefield.set_baseload_heating(8)

    with raises(ValueError):
        borefield.set_baseload_cooling(8)

    with raises(ValueError):
        borefield.set_peak_cooling([8, 8])

    with raises(ValueError):
        borefield.set_peak_heating([8, 8])

    with raises(ValueError):
        borefield.set_baseload_cooling([8, 8])

    with raises(ValueError):
        borefield.set_baseload_heating([8, 8])


def test_gfunction_jit(borefield):
    borefield.use_precalculated_data = False
    borefield.gfunction(10000, 100)


def test_no_ground_data():
    borefield = Borefield(simulation_period=20,
                          peak_heating=peakHeating,
                          peak_cooling=peakCooling,
                          baseload_heating=monthlyLoadHeating,
                          baseload_cooling=monthlyLoadCooling)

    borefield.set_borefield(borefield_gt)

    # set temperature boundaries
    borefield.set_max_ground_temperature(16)  # maximum temperature
    borefield.set_min_ground_temperature(0)  # minimum temperature
    with raises(ValueError):
        borefield.size()


def test_hourly_temperature_profile(hourly_borefield):
    folder = FOLDER.joinpath("Examples/hourly_profile.csv")
    d_f = pd.read_csv(folder, sep=';', decimal='.')
    hourly_borefield.hourly_heating_load_on_the_borefield = d_f[d_f.columns[0]].to_numpy()
    hourly_borefield.hourly_cooling_load_on_the_borefield = d_f[d_f.columns[1]].to_numpy()
    hourly_borefield.calculate_temperatures(100, hourly=True)
    hourly_borefield.hourly_heating_load_on_the_borefield = np.array([])
    hourly_borefield.hourly_cooling_load_on_the_borefield = np.array([])
    hourly_borefield.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))


def test_value_error_cooling_dom_temp_gradient():
    data = GroundFluxTemperature(3, 12)
    borefield_pyg = gt.boreholes.rectangle_field(5, 5, 6, 6, 110, 4, 0.075)
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(1)

    borefield = Borefield(simulation_period=20,
                          peak_heating=peak_heating,
                          peak_cooling=peak_cooling,
                          baseload_heating=monthly_load_heating,
                          baseload_cooling=monthly_load_cooling)

    borefield.set_ground_parameters(data)
    borefield.set_borefield(borefield_pyg)
    borefield.set_Rb(0.2)

    try:
        borefield.size()
    except ValueError:
        assert True


def test_borefield_with_constant_peaks(borefield):
    # test first year
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(1)
    borefield.set_peak_cooling(peak_cooling)
    borefield.set_peak_heating(peak_heating)
    borefield.set_baseload_heating(monthly_load_heating)
    borefield.set_baseload_cooling(monthly_load_cooling)

    # do not save previous g-functions
    borefield.gfunction_calculation_object.store_previous_values = False

    length_L2_1 = borefield.size_L2(100)
    # set constant peak
    borefield.set_peak_cooling([150]*12)
    length_L2_2 = borefield.size_L2(100)

    assert np.isclose(length_L2_1, length_L2_2)

    # test last year
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(2)
    borefield.set_peak_cooling(peak_cooling)
    borefield.set_peak_heating(peak_heating)
    borefield.set_baseload_heating(monthly_load_heating)
    borefield.set_baseload_cooling(monthly_load_cooling)

    # do not save previous g-functions
    borefield.gfunction_calculation_object.store_previous_values = False

    length_L2_1 = borefield.size_L2(100)
    # set constant peak
    borefield.set_peak_cooling([240] * 12)
    length_L2_2 = borefield.size_L2(100)

    assert np.isclose(length_L2_1, length_L2_2, rtol=3*10**-5)


def test_sizing_with_use_constant_Rb():
    borefield = Borefield()
    borefield.set_ground_parameters(data)
    borefield.set_fluid_parameters(fluidData)
    borefield.set_pipe_parameters(pipeData)
    borefield.borefield = copy.deepcopy(borefield_gt)
    borefield.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    assert not borefield.borehole.use_constant_Rb
    borefield.sizing_setup(L4_sizing=True)
    assert np.isclose(205.49615778557904, borefield.size())
    assert np.isclose(182.17320067531486, borefield.size(use_constant_Rb=True))


def test_size_with_different_peak_lengths(borefield):
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(4)

    borefield.set_peak_heating(peak_heating)
    borefield.set_peak_cooling(peak_cooling)
    borefield.set_baseload_cooling(monthly_load_cooling)
    borefield.set_baseload_heating(monthly_load_heating)

    borefield.set_length_peak_cooling(8)
    borefield.set_length_peak_heating(6)
    assert np.isclose(99.33058400216777, borefield.size(L3_sizing=True))