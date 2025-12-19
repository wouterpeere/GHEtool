# test if model can be imported
import copy
from math import isclose

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pygfunction as gt
import pytest
import pickle

from pytest import raises

from GHEtool.VariableClasses.BaseClass import UnsolvableDueToTemperatureGradient, MaximumNumberOfIterations
from GHEtool.Validation.cases import load_case

from GHEtool.Methods import *
from GHEtool import *

data = GroundConstantTemperature(3, 10)
data_ground_flux = GroundFluxTemperature(3, 10)
fluidData = ConstantFluidData(0.568, 998, 4180, 1e-3)
flowData = ConstantFlowRate(mfr=0.2)
pipeData = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)

borefield_gt = gt.borefield.Borefield.rectangle_field(10, 12, 6, 6, 110, 4, 0.075)

# Monthly loading values
peak_injection = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]  # Peak cooling in kW
peak_extraction = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]  # Peak heating in kW

# annual heating and cooling load
annualHeatingLoad = 300 * 10 ** 3  # kWh
annualCoolingLoad = 160 * 10 ** 3  # kWh

# percentage of annual load per month (15.5% for January ...)
baseload_extractionPercentage = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144]
baseload_injectionPercentage = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]

# resulting load per month
baseload_extraction = list(map(lambda x: x * annualHeatingLoad, baseload_extractionPercentage))  # kWh
baseload_injection = list(map(lambda x: x * annualCoolingLoad, baseload_injectionPercentage))  # kWh

custom_field = gt.borefield.Borefield.L_shaped_field(N_1=4, N_2=5, B_1=5., B_2=5., H=100., D=4, r_b=0.05)


def test_borefield():
    load = MonthlyGeothermalLoadAbsolute(baseload_extraction, baseload_injection, peak_extraction, peak_injection)
    borefield = Borefield(load=load)

    borefield.ground_data = data
    borefield.set_borefield(borefield_gt)
    borefield.set_Rb(0.2)

    # set temperature boundaries
    borefield.set_max_avg_fluid_temperature(16)  # maximum temperature
    borefield.set_min_avg_fluid_temperature(0)  # minimum temperature

    assert borefield.simulation_period == 20
    assert borefield.Tf_min == 0
    assert borefield.Tf_max == 16
    assert np.allclose(borefield.load.monthly_peak_extraction, np.array(
        [160., 142, 102., 55., 26.301369863013697, 0., 0., 0., 40.4, 85., 119., 136.]))


@pytest.fixture
def borefield_quadrants():
    data = GroundConstantTemperature(3.5,  # conductivity of the soil (W/mK)
                                     10)  # Ground temperature at infinity (degrees C)

    borefield_gt = gt.borefield.Borefield.rectangle_field(10, 12, 6.5, 6.5, 110, 4, 0.075)

    borefield = Borefield()
    borefield.set_Rb(0.2)
    borefield.ground_data = data
    borefield.set_borefield(borefield_gt)

    return borefield


@pytest.fixture
def borefield():
    load = MonthlyGeothermalLoadAbsolute(baseload_extraction, baseload_injection, peak_extraction, peak_injection)
    borefield = Borefield(load=load)

    borefield.ground_data = data
    borefield.set_borefield(borefield_gt)
    borefield.set_Rb(0.2)

    # set temperature boundaries
    borefield.set_max_avg_fluid_temperature(16)  # maximum temperature
    borefield.set_min_avg_fluid_temperature(0)  # minimum temperature
    return borefield


@pytest.fixture
def borefield_custom_data():
    load = MonthlyGeothermalLoadAbsolute(baseload_extraction, baseload_injection, peak_extraction, peak_injection)
    borefield = Borefield(load=load)

    borefield.ground_data = data
    borefield.set_borefield(borefield_gt)
    borefield.set_Rb(0.2)
    borefield.create_custom_dataset()

    # set temperature boundaries
    borefield.set_max_avg_fluid_temperature(16)  # maximum temperature
    borefield.set_min_avg_fluid_temperature(0)  # minimum temperature
    return borefield


@pytest.fixture
def hourly_borefield():
    borefield = Borefield()
    borefield.ground_data = data
    borefield.set_Rb(0.2)
    borefield.set_borefield(borefield_gt)
    load = HourlyGeothermalLoad()
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"), header=True, separator=";")
    borefield.load = load
    return borefield


@pytest.fixture
def borefield_cooling_dom():
    load = MonthlyGeothermalLoadAbsolute(baseload_extraction, baseload_injection, peak_extraction, peak_injection)
    borefield = Borefield(load=load)

    borefield.load.baseload_injection = np.array(baseload_injection) * 2

    borefield.ground_data = data
    borefield.set_Rb(0.2)
    borefield.set_borefield(borefield_gt)

    return borefield


def test_imbalance(borefield):
    assert borefield.load.imbalance == -140000.0


def test_sizing_L3_threshold_depth_error(borefield):
    max_temp = borefield.Tf_max
    borefield.set_max_avg_fluid_temperature(14)
    borefield.ground_data = data_ground_flux
    borefield._calculation_setup.use_constant_Tg = False
    with raises(UnsolvableDueToTemperatureGradient):
        borefield.gfunction(3600, borefield.THRESHOLD_DEPTH_ERROR + 1)
    borefield._calculation_setup.use_constant_Tg = True
    borefield.set_max_avg_fluid_temperature(max_temp)
    borefield.ground_data.flux = 0


def test_sizing_L32(borefield_cooling_dom):
    borefield_cooling_dom.size(L3_sizing=True)
    borefield_cooling_dom.load.peak_extraction = np.array(peak_extraction) * 5
    borefield_cooling_dom.size(L3_sizing=True)


def test_plot_hourly(monkeypatch, hourly_borefield):
    monkeypatch.setattr(plt, 'show', lambda: None)
    hourly_borefield.print_temperature_profile(plot_hourly=True)


def test_precalculated_data_1(borefield_custom_data):
    borefield_custom_data.gfunction([3600 * 100, 3600 * 100], 100)


def test_precalculated_data_2(borefield_custom_data):
    borefield_custom_data.gfunction([3600 * 100, 3600 * 100, 3600 * 101], 100)


def test_choose_quadrant_None(borefield_quadrants):
    borefield_quadrants.load = MonthlyGeothermalLoadAbsolute(*load_case(4))

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


def test_gfunction_jit(borefield):
    borefield.use_precalculated_data = False
    borefield.gfunction(10000, 100)


def test_no_ground_data():
    borefield = Borefield(
        load=MonthlyGeothermalLoadAbsolute(baseload_extraction, baseload_injection, peak_extraction, peak_injection))

    borefield.set_borefield(borefield_gt)

    # set temperature boundaries
    borefield.set_max_avg_fluid_temperature(16)  # maximum temperature
    borefield.set_min_avg_fluid_temperature(0)  # minimum temperature
    with raises(ValueError):
        borefield.size()


def test_value_error_cooling_dom_temp_gradient():
    data = GroundFluxTemperature(3, 12)
    borefield_pyg = gt.borefield.Borefield.rectangle_field(5, 5, 6, 6, 110, 4, 0.075)

    borefield = Borefield(load=MonthlyGeothermalLoadAbsolute(*load_case(1)))

    borefield.ground_data = data
    borefield.set_borefield(borefield_pyg)
    borefield.set_Rb(0.2)

    with raises(UnsolvableDueToTemperatureGradient):
        borefield.size()

    borefield.calculation_setup(max_nb_of_iterations=500)
    with raises(UnsolvableDueToTemperatureGradient):
        borefield.size()


def test_borefield_with_constant_peaks(borefield):
    # test first year
    borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(1))
    # do not save previous g-functions
    borefield.gfunction_calculation_object.store_previous_values = False

    length_L2_1 = borefield.size_L2(100)
    # set constant peak
    borefield.load.peak_injection = [150] * 12
    length_L2_2 = borefield.size_L2(100)

    assert np.isclose(length_L2_1, length_L2_2)

    # test last year
    borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(2))

    # do not save previous g-functions
    borefield.gfunction_calculation_object.store_previous_values = False

    length_L2_1 = borefield.size_L2(100)
    # set constant peak
    borefield.load.peak_injection = [240] * 12
    length_L2_2 = borefield.size_L2(100)

    assert np.isclose(length_L2_1, length_L2_2, rtol=3 * 10 ** -5)


def test_sizing_with_use_constant_Rb():
    borefield = Borefield()
    borefield.ground_data = data
    borefield.fluid_data = fluidData
    borefield.flow_data = flowData
    borefield.pipe_data = pipeData
    borefield.borefield = copy.deepcopy(borefield_gt)
    load = HourlyGeothermalLoad()
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    borefield.load = load
    assert not borefield.borehole.use_constant_Rb
    borefield.calculation_setup(L4_sizing=True)
    assert np.isclose(205.4926086157351, borefield.size())
    assert np.isclose(182.17320067531486, borefield.size(use_constant_Rb=True))


def test_size_with_different_peak_lengths(borefield):
    borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(4))

    borefield.load.peak_injection_duration = 8
    borefield.load.peak_extraction_duration = 6
    assert np.isclose(99.36581644570013, borefield.size(L3_sizing=True))


def test_convergence_eer_combined():
    ground_data = GroundFluxTemperature(3, 10)
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.2)
    pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)

    load = HourlyBuildingLoad(efficiency_heating=5)  # use SCOP of 5 for heating
    load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True,
                             separator=";", col_cooling=0, col_heating=1)

    eer_active = EER(np.array([15.943, 6.153]),
                     np.array([5, 30]))  # based on the data of the WRE092 chiller of Galletti
    borefield1 = Borefield()
    borefield1.create_rectangular_borefield(3, 3, 6, 6, 110, 0.7, 0.075)
    borefield1.ground_data = ground_data
    borefield1.fluid_data = fluid_data
    borefield1.flow_data = flow_data
    borefield1.pipe_data = pipe_data
    borefield1.set_max_avg_fluid_temperature(25)
    borefield1.set_min_avg_fluid_temperature(3)

    # create combined active and passive EER
    eer = EERCombined(20, eer_active, threshold_temperature=17)

    # set variables
    load.eer = eer
    borefield1.load = load
    borefield1.set_max_avg_fluid_temperature(16)
    borefield1.calculate_temperatures(hourly=True)
    results_16 = copy.deepcopy(borefield1.results)
    borefield1.set_max_avg_fluid_temperature(25)
    borefield1.calculate_temperatures(hourly=True)
    results_25 = copy.deepcopy(borefield1.results)
    assert np.allclose(results_16.peak_injection, results_25.peak_injection)


def test_optimise_load_eer_combined():
    ground_data = GroundFluxTemperature(3, 10)
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.2)
    pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)

    load = HourlyBuildingLoad(efficiency_heating=5)  # use SCOP of 5 for heating
    load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True,
                             separator=";", col_cooling=0, col_heating=1)

    eer_active = EER(np.array([15.943, 6.153]),
                     np.array([5, 30]))  # based on the data of the WRE092 chiller of Galletti
    borefield1 = Borefield()
    borefield1.create_rectangular_borefield(4, 3, 6, 6, 110, 0.7, 0.075)
    borefield1.ground_data = ground_data
    borefield1.fluid_data = fluid_data
    borefield1.flow_data = flow_data
    borefield1.pipe_data = pipe_data
    borefield1.set_max_avg_fluid_temperature(25)
    borefield1.set_min_avg_fluid_temperature(3)

    # create combined active and passive EER
    eer = EERCombined(20, eer_active, threshold_temperature=17)
    load.eer = eer
    borefield1.load = load

    borefield1.set_max_avg_fluid_temperature(16)
    borefield1.calculate_temperatures(hourly=True)
    results_16 = copy.deepcopy(borefield1.results)
    borefield1.set_max_avg_fluid_temperature(25)
    _, sec_load = optimise_load_profile_power(borefield1, borefield1.load)
    borefield1.calculate_temperatures(hourly=True)
    results_25 = copy.deepcopy(borefield1.results)
    assert np.allclose(results_16.peak_injection, results_25.peak_injection)
    _, sec_load = optimise_load_profile_energy(borefield1, borefield1.load)
    borefield1.calculate_temperatures(hourly=True)
    results_25 = copy.deepcopy(borefield1.results)
    assert np.allclose(results_16.peak_injection, results_25.peak_injection)


def test_optimise_methods_different_start_year():
    ground_data = GroundFluxTemperature(3, 10)
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.2)
    pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)

    load = HourlyBuildingLoad(efficiency_heating=5)  # use SCOP of 5 for heating
    load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True,
                             separator=";", col_cooling=0, col_heating=1)
    load.start_month = 5

    borefield = Borefield()
    borefield.create_rectangular_borefield(20, 5, 6, 6, 110, 0.7, 0.075)
    borefield.ground_data = ground_data
    borefield.fluid_data = fluid_data
    borefield.flow_data = flow_data
    borefield.pipe_data = pipe_data

    borefield_load, ext_load = optimise_load_profile_power(borefield, load)
    assert borefield_load.start_month == 5
    assert load.start_month == 5
    assert ext_load.start_month == 5
    assert ext_load.max_peak_heating == 0
    assert ext_load.max_peak_cooling == 0
    assert isinstance(ext_load, HourlyBuildingLoad)

    borefield_load, ext_load = optimise_load_profile_balance(borefield, load)
    assert borefield_load.start_month == 5
    assert load.start_month == 5
    assert ext_load.start_month == 5
    assert np.allclose(borefield_load.hourly_heating_load + ext_load.hourly_heating_load, load.hourly_heating_load)
    assert np.allclose(borefield_load.hourly_cooling_load + ext_load.hourly_cooling_load, load.hourly_cooling_load)

    load = HourlyBuildingLoadMultiYear(load.hourly_heating_load_simulation_period,
                                       load.hourly_cooling_load_simulation_period)

    borefield_load, ext_load = optimise_load_profile_power(borefield, load)
    assert isinstance(ext_load, HourlyBuildingLoadMultiYear)
    assert ext_load.max_peak_heating == 0
    assert ext_load.max_peak_cooling == 0

    borefield_load, ext_load = optimise_load_profile_balance(borefield, load)
    assert isinstance(ext_load, HourlyBuildingLoadMultiYear)
    assert np.allclose(borefield_load.hourly_heating_load + ext_load.hourly_heating_load, load.hourly_heating_load)
    assert np.allclose(borefield_load.hourly_cooling_load + ext_load.hourly_cooling_load, load.hourly_cooling_load)

    borefield.create_rectangular_borefield(10, 2, 6, 6, 110, 0.7, 0.075)
    borefield.ground_data = ground_data
    borefield.fluid_data = fluid_data
    borefield.pipe_data = pipe_data

    borefield_load, ext_load = optimise_load_profile_power(borefield, load)
    assert np.allclose(borefield_load.hourly_heating_load + ext_load.hourly_heating_load, load.hourly_heating_load)
    assert np.allclose(borefield_load.hourly_cooling_load + ext_load.hourly_cooling_load, load.hourly_cooling_load)


def test_optimise_methods_different_start_year_dhw():
    ground_data = GroundFluxTemperature(3, 10)
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.2)
    pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)

    load = HourlyBuildingLoad(efficiency_heating=5)  # use SCOP of 5 for heating
    load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True,
                             separator=";", col_cooling=0, col_heating=1, col_dhw=1)
    load.hourly_heating_load = np.zeros(8760)
    load.start_month = 5

    borefield = Borefield()
    borefield.create_rectangular_borefield(20, 5, 6, 6, 110, 0.7, 0.075)
    borefield.ground_data = ground_data
    borefield.fluid_data = fluid_data
    borefield.flow_data = flow_data
    borefield.pipe_data = pipe_data

    borefield_load, ext_load = optimise_load_profile_power(borefield, load)
    assert borefield_load.start_month == 5
    assert load.start_month == 5
    assert ext_load.start_month == 5
    assert ext_load.max_peak_heating == 0
    assert ext_load.max_peak_cooling == 0
    assert ext_load.max_peak_dhw == 0
    assert isinstance(ext_load, HourlyBuildingLoad)

    borefield_load, ext_load = optimise_load_profile_balance(borefield, load, dhw_preferential=False)
    assert borefield_load.start_month == 5
    assert load.start_month == 5
    assert ext_load.start_month == 5
    assert np.allclose(borefield_load.hourly_heating_load + ext_load.hourly_heating_load, load.hourly_heating_load)
    assert np.allclose(borefield_load.hourly_cooling_load + ext_load.hourly_cooling_load, load.hourly_cooling_load)
    assert np.allclose(borefield_load.hourly_dhw_load + ext_load.hourly_dhw_load, load.hourly_dhw_load)

    load = HourlyBuildingLoadMultiYear(load.hourly_heating_load_simulation_period,
                                       load.hourly_cooling_load_simulation_period)


def test_case_issue_390():
    ground_data = GroundFluxTemperature(1.57, 9.6, flux=0.07)
    fluid = TemperatureDependentFluidData('MPG', 25, False)
    flow = ConstantFlowRate(mfr=0.3)
    pipe = SingleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

    borehole = Borehole(fluid, pipe, flow)

    peak_cooling = [0, 0, 0, 0, 6.225, 11.339999999999998, 15, 14.639999999999999, 8.235, 0, 0, 0]
    peak_heating = [31.3, 31.0183, 25.102600000000002, 17.7158, 8.2632, 0, 0, 0, 2.0658, 11.5184, 21.8474, 29.2342]
    baseload_cooling = [0, 0, 0, 0, 1232, 2255, 2970, 2904, 1639, 0, 0, 0]
    baseload_heating = [11017.6, 10892.4, 8826.6, 6260, 2817, 0, 0, 0, 751.1999999999999, 4069, 7699.8, 10266.4]

    load = MonthlyBuildingLoadAbsolute(baseload_heating, baseload_cooling, peak_heating, peak_cooling, dhw=5000,
                                       efficiency_dhw=3, efficiency_cooling=20, simulation_period=25)

    borefield = Borefield(ground_data=ground_data, load=load)

    borefield.create_rectangular_borefield(4, 4, 6, 6, 100, 1, 0.07)

    borefield.set_min_avg_fluid_temperature(0)
    borefield.set_max_avg_fluid_temperature(17)

    borefield.borehole = borehole
    borefield.size_L3()
    assert np.isclose(borefield.H, 86.21380769613168)
