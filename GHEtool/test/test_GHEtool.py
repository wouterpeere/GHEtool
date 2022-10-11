# test if model can be imported
from GHEtool import *
import pytest
import numpy as np
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
montlyLoadHeatingPercentage = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144]
montlyLoadCoolingPercentage = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]

# resulting load per month
monthlyLoadHeating = list(map(lambda x: x * annualHeatingLoad, montlyLoadHeatingPercentage))   # kWh
monthlyLoadCooling = list(map(lambda x: x * annualCoolingLoad, montlyLoadCoolingPercentage))   # kWh

custom_field = gt.boreholes.L_shaped_field(N_1=4, N_2=5, B_1=5., B_2=5., H=100., D=4, r_b=0.05)


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
    assert borefield.Tf_C == 0
    assert borefield.Tf_H == 16
    np.testing.assert_array_equal(borefield.peak_heating, np.array([160., 142, 102., 55., 26.301369863013697, 0., 0., 0., 40.4, 85., 119., 136.]))


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


def test_empty_values(empty_borefield):
    np.testing.assert_array_equal(empty_borefield.baseload_cooling, np.zeros(12))


def test_size(borefield):
    assert borefield.size(100) == 92.04554491439661


def test_imbalance(borefield):
    assert borefield.imbalance == -140000.0


def test_temperatureProfile(borefield):
    borefield.calculate_temperatures(depth=90)
    np.testing.assert_array_equal(np.around(borefield.results_peak_cooling, 8),
                                  np.around(np.array([9.0712399,9.16314934,9.77067314,10.72163508,12.54230241,14.38307633,15.34894413,16.13569336,13.59485555,10.3174525,9.34677416,8.85727484,8.64218566,8.75010319,9.36950038,10.32935087,12.15705656,14.00662496,14.979314,15.77138848,13.23744895,9.96583809,9.00253888,8.51920484,8.30855584,8.4241055,9.04691889,10.01050055,11.84782409,13.7020139,14.67982194,15.47579387,12.94207877,9.67351399,8.71485193,8.23457153,8.03129553,8.15194086,8.77808849,9.74750236,11.58523442,13.44045245,14.42223328,15.22234853,12.69254756,9.42895971,8.47022823,7.99228836,7.79266596,7.91682919,8.54772471,9.51884575,11.35673851,13.21495007,14.19994493,15.00282412,12.47973861,9.21801715,8.26197182,7.78796326,7.59162368,7.71726631,8.34593026,9.31265005,11.15037448,13.01035858,13.99889704,14.81123327,12.29436672,9.03733019,8.08486161,7.61261063,7.41502116,7.53670724,8.1606479,9.12606352,10.96530368,12.82866485,13.82478342,14.64389292,12.13112504,8.8772869,7.9266816,7.4540217,7.2535675,7.37131152,7.99322603,8.9595841,10.80128736,12.66969392,13.67275772,14.49551439,11.98564875,8.73373289,7.78331927,7.30859446,7.10478679,7.22000951,7.84245133,8.8106024,10.65547589,12.53086239,13.53719902,14.36260621,11.8546827,8.60339536,7.65152669,7.17391944,6.96725895,7.08269903,7.70642215,8.67702475,10.52934627,12.40918161,13.41917278,14.24733649,11.7406261,8.48803179,7.53278739,7.05140345,6.84415487,6.96096336,7.58755909,8.56248491,10.41578875,12.29562409,13.30561526,14.13377897,11.62706858,8.37447427,7.41922987,6.93784593,6.73059736,6.84740584,7.47574536,8.45549247,10.31285685,12.19589242,13.20787814,14.03594913,11.52667296,8.27026005,7.31260439,6.83197907,6.62694646,6.74748528,7.3788942,8.3586413,10.21600569,12.09904126,13.11102697,13.93909797,11.42982179,8.17340888,7.21575323,6.73512791,6.5300953,6.65424746,7.28915256,8.27175161,10.1312396,12.0150923,13.02578571,13.85098493,11.33868584,8.08216618,7.12573103,6.64754294,6.4460991,6.57062157,7.20552668,8.18812572,10.04761371,11.93146641,12.94215983,13.76735905,11.25505995,7.9985403,7.04210514,6.56540271,6.36700247,6.49407312,7.1309662,8.11472127,9.97395001,11.85601731,12.86425852,13.68820454,11.17649419,7.92150947,6.967574,6.49250522,6.29410498,6.42117563,7.05806871,8.04182378,9.90105253,11.78311982,12.79136103,13.61530706,11.1035967,7.84864498,6.89738079,6.4245986,6.22804978,6.35647552,6.99380393,7.97653914,9.833753,11.71383203,12.72222722,13.54707115,11.03707654,7.78456263,6.83329845,6.36051625,6.16396743,6.29239317,6.92972158,7.91245679,9.76967065,11.64974968,12.65814487,13.4829888,10.9748922,7.72544453,6.77673167,6.30591856,6.11042687,6.23838213,6.87373909,7.85396048,9.71019232,11.59097901,12.60106242,13.42857561,10.92180781,7.67236014,6.72364728,6.25283417]), 8))


def test_quadrantSizing(borefield):
    assert round(borefield.size(100, quadrant_sizing=3), 2) == 41.41


def test_dynamicRb(borefield):
    borefield.set_fluid_parameters(fluidData)
    borefield.set_pipe_parameters(pipeData)
    assert round(borefield.size(100, use_constant_Rb=False), 2) == 52.58


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


def test_precalculated_out_of_bound_1(borefield_custom_data):
    borefield_custom_data.gfunction(10**10, H=100)


def test_precalculated_out_of_bound_2(borefield_custom_data):
    borefield_custom_data.gfunction(1, H=100)


def test_precalculated_out_of_bound_3(borefield_custom_data):
    borefield_custom_data.gfunction(10 ** 10, H=100)


def test_precalculated_data_1(borefield_custom_data):
    borefield_custom_data.gfunction([3600*100, 3600*100], 100)


def test_precalculated_data_2(borefield_custom_data):
    borefield_custom_data.gfunction([3600*100, 3600*100, 3600*101], 100)

