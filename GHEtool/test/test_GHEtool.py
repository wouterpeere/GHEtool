# test if model can be imported
import numpy as np
import pytest

from GHEtool import GroundData, FluidData, PipeData, Borefield
from GHEtool.main_class import FOLDER

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
def borefield_same():
    borefield_same = Borefield(simulation_period=100)
    borefield_same.set_ground_parameters(data)
    borefield_same.set_borefield(borefield_gt)
    borefield_same.load_hourly_profile(f"{FOLDER}/Examples/hourly_profile_same.csv", separator=';')
    return borefield_same


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
    from GHEtool.main_class import FOLDER
    borefield = Borefield()
    borefield.set_ground_parameters(data)
    borefield.set_borefield(borefield_gt)
    borefield.load_hourly_profile(f"{FOLDER}/Examples/hourly_profile.csv")
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


def test_hourly_to_monthly(borefield):
    from GHEtool.main_class import FOLDER
    borefield.load_hourly_profile(f"{FOLDER}/Examples/hourly_profile.csv", header=True, separator=";", first_column_heating=True)
    borefield.convert_hourly_to_monthly()

    assert np.isclose(np.sum(borefield.baseload_cooling), np.sum(borefield.hourly_cooling_load))
    assert np.isclose(np.sum(borefield.baseload_heating), np.sum(borefield.hourly_heating_load))


def test_size(borefield):
    assert round(borefield.size(100), 2) == round(92.04554491439661, 2)


def test_imbalance(borefield):
    assert borefield.imbalance == -140000.0


def test_temperatureProfile(borefield):
    borefield.calculate_temperatures(depth=90)
    np.testing.assert_array_equal(np.around(borefield.results_peak_cooling, 8),
                                  np.around(np.array([7.8916356373510546, 8.03681752397025, 8.819379375946376, 9.968210419747908, 12.055240009795533, 14.383076328998147, 15.348944134037856, 16.135693362370773, 13.13062419913821, 9.65535204686884, 8.456363205310826, 7.761384430331367, 7.4625813954412905, 7.623771380374239, 8.418206620909825, 9.575926215793626, 11.669994152370794, 14.006624956580698, 14.979314001195045, 15.771388476973573, 12.773217599992527, 9.303737629280489, 8.112127923020058, 7.423314429923755, 7.128951579773187, 7.297773692574574, 8.09562513000343, 9.257075894251724, 11.360761686210946, 13.70201389537235, 14.67982193664029, 15.475793865915195, 12.47784741618386, 9.01141353225097, 7.824440971533444, 7.138681117790082, 6.851691270535352, 7.02560905141101, 7.8267947310539725, 8.994077704331364, 11.098172013856068, 13.440452452956496, 14.422233281223907, 15.22234852717401, 12.228316201943482, 8.766859254071512, 7.579817273012639, 6.89639795321091, 6.613061698143174, 6.790497382371835, 7.596430952605734, 8.765421091165937, 10.869676108695783, 13.214950068334886, 14.199944929132322, 15.002824123582855, 12.015507252056778, 8.55591669268334, 7.371560861238195, 6.692072846800857, 6.412019415174974, 6.590934498358104, 7.39463649622591, 8.559225396474705, 10.663312070407322, 13.010358583558144, 13.99889704410562, 14.811233269673545, 11.83013536635529, 8.375229731069766, 7.194450652327244, 6.5167202199080165, 6.235416898261638, 6.410375425226146, 7.209354142571313, 8.372638863380935, 10.478241273619627, 12.828664851466044, 13.824783416047005, 14.643892923689792, 11.666893689082727, 8.215186446747536, 7.036270644695023, 6.358131292104149, 6.0739632342272225, 6.244979711336311, 7.041932272431518, 8.206159440160341, 10.314224956550133, 12.66969391582709, 13.672757722690122, 14.495514391989701, 11.521417394177355, 8.071632434389336, 6.892908307902113, 6.212704050180095, 5.925182531244809, 6.093677696598491, 6.891157566476213, 8.057177744847971, 10.168413489857896, 12.530862391990272, 13.53719902226344, 14.362606210004222, 11.390451347115125, 7.941294898934531, 6.761115729084116, 6.078029024536782, 5.787654685295132, 5.9563672187279, 6.755128395447835, 7.923600097312375, 10.042283867167708, 12.40918160880901, 13.41917277865443, 14.247336492737618, 11.276394743948831, 7.825931330433807, 6.642376426270814, 5.955513038124733, 5.66455061298452, 5.834631547529438, 6.636265331877048, 7.809060253252385, 9.928726348858833, 12.295624090500134, 13.305615260345553, 14.13377897442874, 11.162837225639954, 7.71237381212493, 6.528818907961935, 5.841955519815857, 5.550993094675646, 5.721074029220561, 6.524451600576472, 7.7020678090053885, 9.825794447725487, 12.19589242063174, 13.207878136264059, 14.035949131716723, 11.062441600796951, 7.608159592061506, 6.422193431369493, 5.7360886620889495, 5.447342199140863, 5.621153472931909, 6.427600436356948, 7.605216644785867, 9.728943283505961, 12.099041256412217, 13.111026972044534, 13.939097967497199, 10.965590436577429, 7.511308427841981, 6.325342267149969, 5.639237497869427, 5.3504910349213395, 5.527915644033143, 6.33785880458815, 7.518326950097688, 9.64417719085728, 12.015092297110577, 13.025785713992885, 13.85098493444552, 10.87445448247309, 7.42006572683797, 6.235320070520969, 5.551652531339137, 5.266494842478254, 5.44428975941901, 6.254232919974017, 7.434701065483554, 9.560551306243145, 11.931466412496444, 12.942159829378753, 13.767359049831384, 10.790828597858953, 7.336439842223834, 6.151694185906835, 5.46951229876659, 5.187398209947979, 5.367741310132198, 6.179672436354245, 7.361296613879891, 9.486887609539188, 11.856017308979322, 12.864258520831314, 13.688204544842494, 10.712262832026399, 7.259409013974894, 6.077163042668309, 5.396614811160076, 5.1145007223414645, 5.294843822525686, 6.106774948747729, 7.288399126273377, 9.413990121932676, 11.783119821372807, 12.7913610332248, 13.615307057235981, 10.639365344419886, 7.186544518447395, 6.0069698359939006, 5.3287081841339905, 5.048445515910528, 5.230143706440807, 6.042510172849006, 7.223114485427532, 9.346690592287368, 11.713832029476514, 12.722227221614673, 13.547071147697876, 10.572845186872792, 7.122462169338524, 5.942887486885029, 5.26462583502512, 4.984363166801655, 5.166061357331935, 5.978427823740134, 7.159032136318658, 9.282608243178496, 11.649749680367645, 12.658144872505805, 13.482988798589005, 10.510660846389632, 7.0633440745691445, 5.886320713873422, 5.210028148439211, 4.930822607798152, 5.112050318174693, 5.922445330690728, 7.100535824332518, 9.223129916864137, 11.590979011301915, 12.601062422253408, 13.428575612969151, 10.457576455128978, 7.0102596833084885, 5.833236322612765, 5.156943757178553]), 8))


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


def test_same_results_for_L3_L4_with_constant_values(borefield_same):
    # according to L3
    borefield_same.convert_hourly_to_monthly()
    borefield_same.calculate_temperatures(100, False)
    tb = borefield_same.Tb
    temp_res = np.minimum(np.maximum(borefield_same.results_peak_cooling, borefield_same.results_peak_heating), borefield_same.results_peak_heating)

    # according to L4
    borefield_same.calculate_temperatures(100, True)
    tb2 = np.array([borefield_same.Tb[borefield_same.HOURLY_LOAD_ARRAY[t] + 729] for t in range(12)])
    tb3 = np.array([borefield_same.Tb[borefield_same.HOURLY_LOAD_ARRAY[t] + 729 + 8760 * (borefield_same.simulation_period - 1)] for t in range(12)])
    temp_res2 = np.array([borefield_same.results_peak_heating[borefield_same.HOURLY_LOAD_ARRAY[t] + 729] for t in range(12)])
    temp_res3 = np.array(
        [borefield_same.results_peak_heating[borefield_same.HOURLY_LOAD_ARRAY[t] + 729 + 8760 * (borefield_same.simulation_period - 1)] for t in range(12)])
    assert np.allclose(tb[:12], tb2)
    assert np.allclose(tb[12 * (borefield_same.simulation_period - 1):], tb3)
    assert np.allclose(temp_res[:12], temp_res2)
    assert np.allclose(temp_res[12 * (borefield_same.simulation_period - 1):], temp_res3)


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
        borefield.Tg = 14
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
    assert 1 == borefield_quadrants._calculate_quadrant()


def test_choose_quadrant_2(borefield_quadrants):
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(2)

    borefield_quadrants.set_peak_heating(peak_heating)
    borefield_quadrants.set_peak_cooling(peak_cooling)
    borefield_quadrants.set_baseload_cooling(monthly_load_cooling)
    borefield_quadrants.set_baseload_heating(monthly_load_heating)

    borefield_quadrants.size(100, L3_sizing=True)
    assert 2 == borefield_quadrants._calculate_quadrant()


def test_choose_quadrant_3(borefield_quadrants):
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(3)

    borefield_quadrants.set_peak_heating(peak_heating)
    borefield_quadrants.set_peak_cooling(peak_cooling)
    borefield_quadrants.set_baseload_cooling(monthly_load_cooling)
    borefield_quadrants.set_baseload_heating(monthly_load_heating)

    borefield_quadrants.size(100, L3_sizing=True)
    assert 3 == borefield_quadrants._calculate_quadrant()


def test_choose_quadrant_4(borefield_quadrants):
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(4)

    borefield_quadrants.set_peak_heating(peak_heating)
    borefield_quadrants.set_peak_cooling(peak_cooling)
    borefield_quadrants.set_baseload_cooling(monthly_load_cooling)
    borefield_quadrants.set_baseload_heating(monthly_load_heating)

    borefield_quadrants.size(100, L3_sizing=True)
    assert 4 == borefield_quadrants._calculate_quadrant()


def test_choose_quadrant_None(borefield_quadrants):
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(4)

    borefield_quadrants.set_peak_heating(peak_heating)
    borefield_quadrants.set_peak_cooling(peak_cooling)
    borefield_quadrants.set_baseload_cooling(monthly_load_cooling)
    borefield_quadrants.set_baseload_heating(monthly_load_heating)

    borefield_quadrants.calculate_temperatures(200)
    assert None is borefield_quadrants._calculate_quadrant()
