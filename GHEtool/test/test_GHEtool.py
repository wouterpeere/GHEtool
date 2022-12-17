# test if model can be imported
import numpy as np
import pytest
import copy

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


def test_hourly_to_monthly(borefield):
    borefield.load_hourly_profile("GHEtool/Examples/hourly_profile.csv", header=True, separator=";", first_column_heating=True)
    borefield.convert_hourly_to_monthly()

    assert np.isclose(np.sum(borefield.baseload_cooling), np.sum(borefield.hourly_cooling_load))
    assert np.isclose(np.sum(borefield.baseload_heating), np.sum(borefield.hourly_heating_load))


def test_size(borefield):
    assert borefield.size(100) == 92.06688246062056


def test_imbalance(borefield):
    assert borefield.imbalance == -140000.0


def test_temperatureProfile(borefield):
    borefield.calculate_temperatures(depth=90)
    print(np.around(borefield.results_peak_cooling, 8))
    np.testing.assert_array_equal(np.around(borefield.results_peak_cooling, 8),
                                  np.around(np.array([9.07271073,9.16542396,9.77304156,10.72369543,12.54298531,14.38213495,15.34748675,16.13307023,13.59477656,10.32167863,9.35252056,8.86424021,8.65045333,8.75960532,9.37961003,10.33955964,12.16621319,14.01454763,14.98702831,15.77816218,13.24705144,9.97999009,9.01851721,8.53665217,8.32749027,8.4445767,9.06811793,10.03194031,11.868557,13.72166506,14.69944645,15.49462065,12.96374438,9.69983322,8.74313316,8.26440487,8.06284722,8.18518691,8.81217158,9.78199637,11.61901397,13.47316268,14.45501655,15.25444535,12.7275943,9.46877621,8.51198827,8.0356435,7.83781816,7.96375854,8.5955959,9.56715097,11.40431863,13.26150984,14.24663584,15.04888566,12.52884485,9.27189592,8.31781475,7.8454471,7.65095011,7.77840303,8.40799548,9.37510293,11.21210047,13.07108291,14.05978985,14.87156639,12.35776998,9.10552218,8.15503013,7.68442615,7.48867495,7.61215762,8.23701046,9.20280921,11.04132773,12.90369892,13.89999332,14.71852765,12.2088115,8.95974773,8.01111059,7.54009952,7.34149645,7.46105478,8.08389056,9.05062752,10.89159809,12.75898428,13.76216048,14.58429827,12.07744959,8.83028507,7.88183731,7.40878608,7.20686972,7.32393695,7.94729372,8.91580221,10.75990475,12.63415896,13.64054455,14.46528149,11.9603373,8.71378911,7.76391451,7.2880367,7.08332282,7.2006032,7.82521644,8.79612894,10.64749675,12.52607033,13.53600411,14.36341736,11.85965098,8.61183386,7.65868177,7.17913717,6.97385232,7.09246128,7.71986353,8.69497344,10.54729499,12.42586858,13.43580236,14.26321561,11.75944923,8.51163211,7.55848001,7.07893542,6.87365057,6.99225952,7.62133522,8.60107195,10.45729025,12.33893498,13.35078285,14.17810712,11.67187846,8.42039677,7.46493068,6.9861141,6.78295583,6.90514466,7.53716594,8.51690266,10.37312097,12.25476569,13.26661357,14.09393784,11.58770917,8.33622749,7.3807614,6.90194482,6.69878655,6.82439527,7.45972558,8.44216157,10.30038979,12.1828079,13.19343266,14.01803889,11.50894914,8.25736642,7.30305549,6.82654567,6.62678405,6.75274326,7.38807357,8.37050955,10.22873777,12.11115589,13.12178064,13.94638688,11.43729712,8.18571441,7.23140348,6.7562819,6.55936431,6.68770461,7.32489254,8.30840876,10.16639473,12.04714451,13.05547785,13.87891306,11.37037344,8.12022501,7.16824987,6.69465482,6.49773723,6.62607754,7.26326546,8.24678168,10.10476765,11.98551743,12.99385077,13.81728598,11.30874636,8.05862838,7.10911826,6.63763323,6.4424241,6.57201486,7.20960451,8.19217961,10.04830628,11.92722132,12.93569675,13.75996053,11.25300418,8.00513577,7.05562565,6.58414062,6.38893149,6.51852225,7.1561119,8.138687,9.99481367,11.87372871,12.88220414,13.70646792,11.20123385,7.95614778,7.00895276,6.53925451,6.34500463,6.47416847,7.1099692,8.09026323,9.9454988,11.82505598,12.83506333,13.66174923,11.15772092,7.91263486,6.96543984,6.49574158]), 8))


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
