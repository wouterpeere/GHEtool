# test if model can be imported
import numpy as np
import pytest

from GHEtool import *

import pygfunction as gt
import matplotlib.pyplot as plt


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
    borefield = Borefield()
    borefield.set_ground_parameters(data)
    borefield.set_borefield(borefield_gt)
    borefield.load_hourly_profile("GHEtool/Examples/hourly_profile.csv")
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
        assert borefield.borefield[i].__dict__ == borefield.create_rectangular_borefield(10, 12, 6, 6, 110, 4, 0.075)[i].__dict__

def test_create_circular_field(borefield):
    borefield.create_circular_borefield(10, 10, 100, 1)
    for i in range(len(borefield.borefield)):
        assert borefield.borefield[i].__dict__ == gt.boreholes.circle_field(10, 10, 100, 1, 0.075)[i].__dict__

def test_empty_values(empty_borefield):
    np.testing.assert_array_equal(empty_borefield.baseload_cooling, np.zeros(12))


def test_size(borefield):
    assert borefield.size(100) == 92.06688246062056


def test_imbalance(borefield):
    assert borefield.imbalance == -140000.0


def test_temperatureProfile(borefield):
    borefield.calculate_temperatures(depth=90)
    print(np.around(borefield.results_peak_cooling, 8))
    np.testing.assert_array_equal(np.around(borefield.results_peak_cooling, 8),
                                  np.around(np.array([9.07267348,9.165368,9.77368204,10.72540446,12.54650156,14.38716199,15.35265141,16.13908188,13.59896695,10.32220591,9.35238892,8.86407987,8.65026263,8.7593864,9.38007687,10.34108662,12.1695408,14.01937857,14.99199093,15.78396757,13.25103038,9.98030132,9.0181641,8.53626611,8.32707069,8.44412401,9.06834933,10.03322961,11.87164216,13.72625191,14.70416257,15.50017753,12.96747466,9.69989432,8.74252847,8.26376645,8.06217274,8.18447773,8.81214533,9.78302668,11.62184074,13.47749149,14.45947417,15.25974298,12.7310644,9.46857679,8.51112362,8.03474536,7.83688396,7.96278941,8.59530962,9.56792168,11.40688625,13.26557999,14.25083516,15.05392507,12.53205853,9.27144149,8.31669644,7.84429667,7.64976448,7.77718235,8.40745637,9.37561909,11.21441348,13.07489914,14.06373664,14.87635758,12.3607387,9.1048253,8.1536713,7.68303613,7.48724905,7.61069456,8.23622643,9.20307976,11.04339594,12.90727216,13.90370166,14.72308501,12.21154942,8.9588224,8.00952468,7.53848213,7.33984107,7.45935933,8.08287264,9.05066488,10.89343492,12.76233005,13.76564725,14.58863741,12.07997195,8.82914595,7.88003778,7.40695317,7.20499575,7.32202059,7.94605538,8.91562079,10.76152572,12.63729591,13.64382604,14.46941823,11.96265935,8.71245037,7.76191378,7.28599947,7.08124143,7.19847966,7.82377231,8.79574439,10.64892359,12.52901903,13.53910217,14.3673743,11.86179484,8.6103152,7.65649666,7.17691058,6.9715808,7.09014941,7.71823487,8.69441006,10.54854429,12.42863973,13.43872287,14.26699501,11.76141555,8.5099359,7.55611737,7.07653129,6.8712015,6.98977012,7.61953157,8.60034063,10.45837756,12.34154883,13.35354898,14.181732,11.6736865,8.4185367,7.46240064,6.98354369,6.78034373,6.90249767,7.5352092,8.51601826,10.37405519,12.25722646,13.26922661,14.09740963,11.58936413,8.33421433,7.37807827,6.89922132,6.69602136,6.82160123,7.45762764,8.44114072,10.30119112,12.18513714,13.19591202,14.0213722,11.51046056,8.25520955,7.30023069,6.82368457,6.62388726,6.74981824,7.38584464,8.36935773,10.22940813,12.11335415,13.12412902,13.94958921,11.43867756,8.18342655,7.2284477,6.75329254,6.55634484,6.68466159,7.32254926,8.3071447,10.16695237,12.04922678,13.05770574,13.8819926,11.37163217,8.11781827,7.16517978,6.69155416,6.49460646,6.62292321,7.26081088,8.24540631,10.10521399,11.9874884,12.99596736,13.82025422,11.30989379,8.0561104,7.10594217,6.63443104,6.43919543,6.5687653,7.20705554,8.19070786,10.04865229,11.92908806,12.93770942,13.7628266,11.25405281,8.00252376,7.05235553,6.5808444,6.38560879,6.51517866,7.1534689,8.13712123,9.99506565,11.87550142,12.88412278,13.70923997,11.20219243,7.95345216,7.00560439,6.53588416,6.34161002,6.47075198,7.10724916,8.08861514,9.94566641,11.82674581,12.83690262,13.66444753,11.15860854,7.90986828,6.9620205,6.49230028]), 8))


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
    borefield.use_constant_Tg = False
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
    hourly_borefield.plot_load_duration()


def test_optimise_load_profile_without_data(borefield):
    try:
        borefield.optimise_load_profile()
    except ValueError:
        assert True


def test_precalculated_out_of_bound_2(borefield_custom_data):
    borefield_custom_data.gfunction(2, H=100)


def test_precalculated_out_of_bound_1(borefield_custom_data):
    borefield_custom_data.gfunction(10**10, H=100)


def test_precalculated_out_of_bound_3(borefield_custom_data):
    borefield_custom_data.gfunction([3600*100, 3600*101], H=500)


def test_precalculated_data_1(borefield_custom_data):
    borefield_custom_data.gfunction([3600*100, 3600*100], 100)


def test_precalculated_data_2(borefield_custom_data):
    borefield_custom_data.gfunction([3600*100, 3600*100, 3600*101], 100)


def test_error_variable_Tg(borefield):
    try:
        borefield.ground_data.Tg = 14
        borefield.sizing_setup(use_constant_Tg=False)
    except ValueError:
        assert True


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
