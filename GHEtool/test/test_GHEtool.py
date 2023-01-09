# test if model can be imported
import matplotlib.pyplot as plt
import numpy as np
import pygfunction as gt
import pytest
import copy
from math import isclose

from GHEtool import *

data = GroundData(3, 10, 0.2)
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


def load_case(number):
    """This function returns the values for one of the four cases."""

    if number == 1:
        # case 1
        # limited in the first year by cooling
        monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
        monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
        monthly_load_heating = monthly_load_heating_percentage * 300 * 10 ** 3  # kWh
        monthly_load_cooling = monthly_load_cooling_percentage * 150 * 10 ** 3  # kWh
        peak_cooling = np.array([0., 0., 22., 44., 83., 117., 134., 150., 100., 23., 0., 0.])
        peak_heating = np.zeros(12)

    elif number == 2:
        # case 2
        # limited in the last year by cooling
        monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, .117, 0.144])
        monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
        monthly_load_heating = monthly_load_heating_percentage * 160 * 10 ** 3  # kWh
        monthly_load_cooling = monthly_load_cooling_percentage * 240 * 10 ** 3  # kWh
        peak_cooling = np.array([0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.])  # Peak cooling in kW
        peak_heating = np.array([160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.])

    elif number == 3:
        # case 3
        # limited in the first year by heating
        monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, .117, 0.144])
        monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
        monthly_load_heating = monthly_load_heating_percentage * 160 * 10 ** 3  # kWh
        monthly_load_cooling = monthly_load_cooling_percentage * 240 * 10 ** 3  # kWh
        peak_cooling = np.zeros(12)
        peak_heating = np.array([300.0, 266.25, 191.25, 103.125, 0.0, 0.0, 0.0, 0.0, 75.75, 159.375, 223.125, 255.0])

    else:
        # case 4
        # limited in the last year by heating
        monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
        monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
        monthly_load_heating = monthly_load_heating_percentage * 300 * 10 ** 3  # kWh
        monthly_load_cooling = monthly_load_cooling_percentage * 150 * 10 ** 3  # kWh
        peak_cooling = np.array([0., 0., 22., 44., 83., 117., 134., 150., 100., 23., 0., 0.])
        peak_heating = np.array([300., 268., 191., 103., 75., 0., 0., 38., 76., 160., 224., 255.])

    return monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating


def test_borefield():
    borefield = Borefield(simulation_period=20,
                          peak_heating=peakHeating,
                          peak_cooling=peakCooling,
                          baseload_heating=monthlyLoadHeating,
                          baseload_cooling=monthlyLoadCooling)

    borefield.set_ground_parameters(data)
    borefield.set_borefield(borefield_gt)

    # set temperature boundaries
    borefield.set_max_ground_temperature(16)  # maximum temperature
    borefield.set_min_ground_temperature(0)  # minimum temperature

    assert borefield.simulation_period == 20
    assert borefield.Tf_min == 0
    assert borefield.Tf_max == 16
    np.testing.assert_array_equal(borefield.peak_heating, np.array([160., 142, 102., 55., 26.301369863013697, 0., 0., 0., 40.4, 85., 119., 136.]))


@pytest.fixture
def borefield_quadrants():
    data = GroundData(3.5,  # conductivity of the soil (W/mK)
                      10,  # Ground temperature at infinity (degrees C)
                      0.2)  # equivalent borehole resistance (K/W)

    borefield_gt = gt.boreholes.rectangle_field(10, 12, 6.5, 6.5, 110, 4, 0.075)

    borefield = Borefield()
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
    borefield.create_custom_dataset()

    # set temperature boundaries
    borefield.set_max_ground_temperature(16)  # maximum temperature
    borefield.set_min_ground_temperature(0)  # minimum temperature
    return borefield


@pytest.fixture
def empty_borefield():
    borefield = Borefield()
    return borefield


@pytest.fixture
def hourly_borefield():
    from GHEtool import FOLDER
    borefield = Borefield()
    borefield.set_ground_parameters(data)
    borefield.set_borefield(borefield_gt)
    borefield.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    return borefield


@pytest.fixture
def hourly_borefield_reversed():
    borefield = Borefield()
    borefield.set_ground_parameters(data)
    borefield.set_borefield(borefield_gt)
    borefield.load_hourly_profile("GHEtool/Examples/hourly_profile.csv", first_column_heating=False)
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
    borefield.set_borefield(borefield_gt)

    return borefield


def test_create_rectangular_field(borefield):
    for i in range(len(borefield.borefield)):
        assert borefield.borefield[i].__dict__ == gt.boreholes.rectangle_field(10, 12, 6, 6, 110, 4, 0.075)[i].__dict__


def test_create_circular_field(borefield):
    borefield.create_circular_borefield(10, 10, 100, 1)
    for i in range(len(borefield.borefield)):
        assert borefield.borefield[i].__dict__ == gt.boreholes.circle_field(10, 10, 100, 1, 0.075)[i].__dict__


def test_empty_values(empty_borefield):
    np.testing.assert_array_equal(empty_borefield.baseload_cooling, np.zeros(12))


def test_hourly_to_monthly(borefield):
    borefield.load_hourly_profile("GHEtool/Examples/hourly_profile.csv", header=True, separator=";", first_column_heating=True)
    borefield.convert_hourly_to_monthly()

    assert np.isclose(np.sum(borefield.baseload_cooling), np.sum(borefield.hourly_cooling_load))
    assert np.isclose(np.sum(borefield.baseload_heating), np.sum(borefield.hourly_heating_load))


def test_size(borefield):
    assert isclose(borefield.size(100), 92.06688246062056)


def test_imbalance(borefield):
    assert borefield.imbalance == -140000.0


def test_temperatureProfile(borefield):
    borefield.calculate_temperatures(depth=90)
    print(np.around(borefield.results_peak_cooling, 8))
    np.testing.assert_array_equal(np.around(borefield.results_peak_cooling, 8),
                                  np.around(np.array([9.07267348,9.165368,9.77296687,10.72360291,12.54288359,14.38203799,15.3474007,16.13299311,13.594681,10.32156769,9.35238892,8.86407987,8.65026263,8.7593864,9.37936169,10.33928507,12.16592283,14.01425456,14.98674021,15.7778788,13.24674443,9.97966311,9.0181641,8.53626611,8.32707069,8.44412401,9.06763415,10.03142806,11.86802419,13.7211279,14.69891185,15.49408876,12.96318871,9.6992561,8.74252847,8.26376645,8.06217274,8.18447773,8.81143016,9.78122514,11.61822277,13.47236748,14.45422346,15.25365421,12.72677845,9.46793857,8.51112362,8.03474536,7.83688396,7.96278941,8.59459444,9.56612014,11.40326828,13.26045599,14.24558444,15.0478363,12.52777258,9.27080327,8.31669644,7.84429667,7.64976448,7.77718235,8.4067412,9.37381755,11.21079551,13.06977514,14.05848593,14.87026882,12.35645275,9.10418709,8.1536713,7.68303613,7.48724905,7.61069456,8.23551126,9.20127822,11.03977797,12.90214816,13.89845095,14.71699625,12.20726347,8.95818419,8.00952468,7.53848213,7.33984107,7.45935933,8.08215747,9.04886334,10.88981695,12.75720605,13.76039653,14.58254864,12.075686,8.82850773,7.88003778,7.40695317,7.20499575,7.32202059,7.9453402,8.91381925,10.75790775,12.63217191,13.63857533,14.46332946,11.95837341,8.71181215,7.76191378,7.28599947,7.08124143,7.19847966,7.82305714,8.79394284,10.64530562,12.52389502,13.53385146,14.36128553,11.85750889,8.60967698,7.65649666,7.17691058,6.9715808,7.09014941,7.71751969,8.69260851,10.54492632,12.42351573,13.43347216,14.26090624,11.7571296,8.50929769,7.55611737,7.07653129,6.8712015,6.98977012,7.6188164,8.59853909,10.45475959,12.33642483,13.34829827,14.17564323,11.66940055,8.41789849,7.46240064,6.98354369,6.78034373,6.90249767,7.53449402,8.51421671,10.37043722,12.25210245,13.2639759,14.09132086,11.58507818,8.33357612,7.37807827,6.89922132,6.69602136,6.82160123,7.45691246,8.43933918,10.29757315,12.18001314,13.19066131,14.01528343,11.50617461,8.25457133,7.30023069,6.82368457,6.62388726,6.74981824,7.38512947,8.36755618,10.22579016,12.10823014,13.11887831,13.94350044,11.43439161,8.18278834,7.2284477,6.75329254,6.55634484,6.68466159,7.32183408,8.30534315,10.1633344,12.04410277,13.05245503,13.87590383,11.36734622,8.11718006,7.16517978,6.69155416,6.49460646,6.62292321,7.2600957,8.24360477,10.10159602,11.98236439,12.99071665,13.81416545,11.30560784,8.05547219,7.10594217,6.63443104,6.43919543,6.5687653,7.20634037,8.18890632,10.04503431,11.92396406,12.9324587,13.75673784,11.24976686,8.00188555,7.05235553,6.5808444,6.38560879,6.51517866,7.15275373,8.13531968,9.99144768,11.87037742,12.87887207,13.7031512,11.19790648,7.95281395,7.00560439,6.53588416,6.34161002,6.47075198,7.10653399,8.0868136,9.94204844,11.82162181,12.83165191,13.65835876,11.15432259,7.90923007,6.9620205,6.49230028]), 8))


def test_quadrantSizing(borefield):
    assert round(borefield.size(100, quadrant_sizing=3), 2) == 41.3


def test_dynamicRb(borefield):
    borefield.set_fluid_parameters(fluidData)
    borefield.set_pipe_parameters(pipeData)
    assert round(borefield.size(100, use_constant_Rb=False), 2) == 52.7


def test_load_custom_configuration(borefield):

    borefield.set_borefield(custom_field)
    assert borefield.borefield == custom_field


def test_simulation_period(borefield):
    borefield.set_simulation_period(25)
    assert borefield.simulation_period == 25


def test_without_pipe(borefield):
    borefield.set_pipe_parameters(pipeData)
    borefield.set_fluid_parameters(fluidData)


def test_Tg(borefield):
    borefield._sizing_setup.use_constant_Tg = False
    borefield._Tg()


def test_calculate_Rb(borefield):
    try:
        borefield.calculate_Rb()
    except ValueError:
        assert True


def test_too_much_sizing_methods(borefield):
    try:
        borefield.sizing_setup(L2_sizing=True, L3_sizing=True)
    except ValueError:
        assert True


def test_size_L3(borefield):
    borefield.size(L3_sizing=True)


def test_draw_internals(monkeypatch, borefield):
    monkeypatch.setattr(plt, 'show', lambda: None)
    borefield.set_fluid_parameters(fluidData)
    borefield.set_pipe_parameters(pipeData)
    borefield.draw_borehole_internal()


def test_size_L4(hourly_borefield):
    assert hourly_borefield._check_hourly_load()
    hourly_borefield.sizing_setup(L4_sizing=True)
    hourly_borefield.size()


def test_size_L4_quadrant(hourly_borefield):
    hourly_borefield.sizing_setup(L4_sizing=True, quadrant_sizing=1)
    hourly_borefield.size()


def test_size_L4_quadrant_4(hourly_borefield):
    hourly_borefield.hourly_heating_load[0] = 100000
    hourly_borefield.sizing_setup(L4_sizing=True)
    hourly_borefield.size()


def test_size_L4_heating_dom(hourly_borefield_reversed):
    hourly_borefield_reversed.sizing_setup(L4_sizing=True)
    hourly_borefield_reversed.size()


def test_size_L4_quadrant_3(hourly_borefield_reversed):
    hourly_borefield_reversed.hourly_heating_load[0] = 100000
    hourly_borefield_reversed.sizing_setup(L4_sizing=True)
    hourly_borefield_reversed.size()


def test_sizing_setup(borefield):
    borefield.sizing_setup(sizing_setup=SizingSetup())


def test_cooling_dom(borefield_cooling_dom):
    borefield_cooling_dom.size()


def test_sizing_different_quadrants(borefield):
    borefield.size(quadrant_sizing=1)
    borefield.size(quadrant_sizing=2)
    borefield.size(quadrant_sizing=3)
    borefield.size(quadrant_sizing=4)
    borefield.size(quadrant_sizing=1, L3_sizing=True)


def test_quadrant_4(borefield):
    borefield.set_peak_heating(np.array(peakHeating)*8)
    borefield.size()


def test_sizing_L3(borefield):
    borefield.set_peak_heating(np.array(peakHeating)*8)
    borefield.size(L3_sizing=True)


def test_sizing_L32(borefield_cooling_dom):
    borefield_cooling_dom.size(L3_sizing=True)
    borefield_cooling_dom.set_peak_heating(np.array(peakHeating) * 5)
    borefield_cooling_dom.size(L3_sizing=True)


def test_size_L4_without_data(borefield):
    try:
        borefield.size(L4_sizing=True)
    except ValueError:
        assert True


def test_load_duration(monkeypatch, hourly_borefield):
    monkeypatch.setattr(plt, 'show', lambda: None)
    hourly_borefield.plot_load_duration(legend=True)


def test_load_duration_no_hourly_data(borefield):
    try:
        borefield.plot_load_duration()
    except ValueError:
        assert True


def test_optimise_load_profile_without_data(borefield):
    try:
        borefield.optimise_load_profile()
    except ValueError:
        assert True


def test_precalculated_data_1(borefield_custom_data):
    borefield_custom_data.gfunction([3600*100, 3600*100], 100)


def test_precalculated_data_2(borefield_custom_data):
    borefield_custom_data.gfunction([3600*100, 3600*100, 3600*101], 100)


def test_error_variable_Tg(borefield):
    borefield.ground_data.Tg = 14
    borefield.sizing_setup(use_constant_Tg=False)


def test_choose_quadrant_1(borefield_quadrants):
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(1)

    borefield_quadrants.set_peak_heating(peak_heating)
    borefield_quadrants.set_peak_cooling(peak_cooling)
    borefield_quadrants.set_baseload_cooling(monthly_load_cooling)
    borefield_quadrants.set_baseload_heating(monthly_load_heating)

    borefield_quadrants.size(100, L3_sizing=True)
    assert 1 == borefield_quadrants.calculate_quadrant()


def test_choose_quadrant_2(borefield_quadrants):
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(2)

    borefield_quadrants.set_peak_heating(peak_heating)
    borefield_quadrants.set_peak_cooling(peak_cooling)
    borefield_quadrants.set_baseload_cooling(monthly_load_cooling)
    borefield_quadrants.set_baseload_heating(monthly_load_heating)

    borefield_quadrants.size(100, L3_sizing=True)
    assert 2 == borefield_quadrants.calculate_quadrant()


def test_choose_quadrant_3(borefield_quadrants):
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(3)

    borefield_quadrants.set_peak_heating(peak_heating)
    borefield_quadrants.set_peak_cooling(peak_cooling)
    borefield_quadrants.set_baseload_cooling(monthly_load_cooling)
    borefield_quadrants.set_baseload_heating(monthly_load_heating)

    borefield_quadrants.size(100, L3_sizing=True)
    assert 3 == borefield_quadrants.calculate_quadrant()


def test_choose_quadrant_4(borefield_quadrants):
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(4)

    borefield_quadrants.set_peak_heating(peak_heating)
    borefield_quadrants.set_peak_cooling(peak_cooling)
    borefield_quadrants.set_baseload_cooling(monthly_load_cooling)
    borefield_quadrants.set_baseload_heating(monthly_load_heating)

    borefield_quadrants.size(100, L3_sizing=True)
    assert 4 == borefield_quadrants.calculate_quadrant()


def test_choose_quadrant_None(borefield_quadrants):
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(4)

    borefield_quadrants.set_peak_heating(peak_heating)
    borefield_quadrants.set_peak_cooling(peak_cooling)
    borefield_quadrants.set_baseload_cooling(monthly_load_cooling)
    borefield_quadrants.set_baseload_heating(monthly_load_heating)

    borefield_quadrants.calculate_temperatures(200)
    assert None is borefield_quadrants.calculate_quadrant()


def test_set_none_borefield(borefield):
    borefield.set_borefield(None)


def test_set_investment_cost(borefield):
    borefield.set_investment_cost()
    assert borefield.cost_investment == Borefield.DEFAULT_INVESTMENT
    borefield.set_investment_cost([0, 38])
    assert borefield.cost_investment == [0, 38]


def test_investment_cost(borefield):
    borefield.H = 100
    cost = 10 * 12 * 100
    assert borefield.investment_cost == cost * borefield.cost_investment[0]
    borefield.set_investment_cost([38, 0])
    assert borefield.investment_cost == cost * 38


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
    try:
        borefield.size_L4(H_init=100)
    except ValueError:
        assert True


def test_size_hourly_quadrant(hourly_borefield):
    hourly_borefield.H = 0.5
    hourly_borefield.size_L4(H_init=100, quadrant_sizing=1)


def test_create_custom_dataset_without_data(borefield):
    borefield.ground_data = None
    try:
        borefield.create_custom_dataset()
    except ValueError:
        assert True
    borefield.borefield = None
    try:
        borefield.create_custom_dataset()
    except ValueError:
        assert True


def test_check_hourly_load(borefield):
    try:
        borefield._check_hourly_load()
    except ValueError:
        assert True

    borefield.load_hourly_profile("GHEtool/Examples/hourly_profile.csv")
    borefield.hourly_cooling_load[0] = -1
    try:
        borefield._check_hourly_load()
    except ValueError:
        assert True


def test_load_hourly_data(borefield):
    borefield.load_hourly_profile("GHEtool/Examples/hourly_profile.csv")
    test_cooling = copy.copy(borefield.hourly_cooling_load)
    borefield.load_hourly_profile("GHEtool/Examples/hourly_profile.csv", first_column_heating=False)
    assert np.array_equal(test_cooling, borefield.hourly_heating_load)

    borefield.load_hourly_profile("GHEtool/test/hourly_profile_without_header.csv", header=False)
    assert np.array_equal(test_cooling, borefield.hourly_cooling_load)


def test_convert_hourly_to_monthly_without_data(borefield):
    try:
        borefield.convert_hourly_to_monthly()
    except IndexError:
        assert True
    borefield.set_fluid_parameters(fluidData)
    borefield.set_pipe_parameters(pipeData)
    borefield._sizing_setup.use_constant_Rb = False
    try:
        borefield.optimise_load_profile()
    except ValueError:
        assert True


def test_calculate_hourly_temperature_profile(hourly_borefield):
    hourly_borefield._calculate_temperature_profile(100, hourly=True)
    hourly_borefield.hourly_heating_load_on_the_borefield = hourly_borefield.hourly_heating_load
    hourly_borefield.hourly_cooling_load_on_the_borefield = hourly_borefield.hourly_cooling_load


def test_incorrect_values_peak_baseload(borefield):
    try:
        borefield.set_peak_heating(8)
    except ValueError:
        assert True

    try:
        borefield.set_peak_cooling(8)
    except ValueError:
        assert True

    try:
        borefield.set_baseload_heating(8)
    except ValueError:
        assert True

    try:
        borefield.set_baseload_cooling(8)
    except ValueError:
        assert True

    try:
        borefield.set_peak_cooling([8, 8])
    except ValueError:
        assert True

    try:
        borefield.set_peak_heating([8, 8])
    except ValueError:
        assert True

    try:
        borefield.set_baseload_cooling([8, 8])
    except ValueError:
        assert True

    try:
        borefield.set_baseload_heating([8, 8])
    except ValueError:
        assert True


def test_temperature_profile_available(hourly_borefield):
    hourly_borefield.calculate_temperatures(100, True)
    assert not hourly_borefield.recalculation_needed
    assert hourly_borefield._check_temperature_profile_available(hourly=True)
    hourly_borefield.recalculation_needed = True
    assert not hourly_borefield._check_temperature_profile_available(True)

    hourly_borefield.gui = True
    hourly_borefield._plot_temperature_profile(plot_hourly=True)


def test_set_options_gfunction_calculation(borefield):
    borefield.set_options_gfunction_calculation({"method": "equivalentt"})
    assert borefield.options_pygfunction["method"] == "equivalentt"
    borefield.set_options_gfunction_calculation({"method": "equivalent"})


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
    try:
        borefield.size()
    except ValueError:
        assert True
