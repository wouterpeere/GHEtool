"""
This file contains a couple of sizing examples to show the enhanced speed and accuracy of the new method implemented
in issue 403. When working with variable fluid properties, the Rb* calculation takes quite a lot of time. In order to
save some, interpolation is used (default 50 values). However, this also introduces an interpolation error.

In this new method, only the min and max temperatures are used and directly calculated instead of being interpolated.
This results in a more accurate sizing, since the limits are used directly.

A second speed improvement can be set as the attribute approximate_req_depth in calculation_setup. This in most cases
half's the simulation time, but can lead to slightly different depth convergences.

------------------------------------
Note, since the implementation of the explicit borehole models is it faster not to use this approach.
This effect is shown for test_monthly_quadrant_4 and test_case_office.
The other examples use the borehole resistance calculation from pygfunction.
"""
from GHEtool import *
import numpy as np

import time


def test_monthly_quadrant_4():
    ground = GroundFluxTemperature(3.5, 9.6, flux=0.07)
    borefield = Borefield(ground_data=ground)
    borefield.calculation_setup(use_explicit_multipole=False)
    borefield.create_rectangular_borefield(10, 7, 6.5, 6.5, 100, 4, 0.075)
    borefield.fluid_data = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)
    borefield.flow_data = ConstantFlowRate(mfr=0.3)
    borefield.pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

    peak_heating_rel = np.array([1, .991, .802, .566, .264, 0, 0, 0, .066, .368, .698, .934])
    peak_cooling_rel = np.array([0, 0, 0, 0, .415, .756, 1, .976, .549, 0, 0, 0])
    bl_heating = np.array([.176, .174, .141, .1, .045, 0, 0, 0, .012, .065, .123, .164])
    bl_cooling = np.array([0, 0, 0, 0, .112, .205, .27, .264, .149, 0, 0, 0])

    load = MonthlyBuildingLoadAbsolute(300000 * bl_heating, 150000 * bl_cooling, 300 * peak_heating_rel,
                                       150 * peak_cooling_rel, efficiency_cooling=20, efficiency_heating=5)
    load.peak_duration = 8
    borefield.load = load
    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 93.07211168325443)
    assert np.isclose(borefield.results.min_temperature, 0.0002468738488783373)
    assert np.isclose(borefield.results.max_temperature, 15.572595961723243)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 93.07211168325443)
    assert np.isclose(borefield.results.min_temperature, 0.0002462780022183253)
    assert np.isclose(borefield.results.max_temperature, 15.572588425674457)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 93.07190954347438)
    assert np.isclose(borefield.results.min_temperature, 0.0002468738488783373)
    assert np.isclose(borefield.results.max_temperature, 15.572595961723243)
    print(f'Simulation time with speed up and approximate_req_depth {time.time() - start}s')

    borefield.calculation_setup(use_explicit_multipole=True)
    borefield.calculation_setup(approximate_req_depth=False)
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 93.04522394124531)
    assert np.isclose(borefield.results.min_temperature, 0.00024763561670226863)
    assert np.isclose(borefield.results.max_temperature, 15.568308313315452)
    print(f'Simulation time with speed up and explicit models {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 93.04529252397683)
    assert np.isclose(borefield.results.min_temperature, 0.0002470427444825063)
    assert np.isclose(borefield.results.max_temperature, 15.568305763045862)
    print(f'Simulation time without speed up and explicit models {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 93.04522394124531)
    assert np.isclose(borefield.results.min_temperature, 0.00024763561670226863)
    assert np.isclose(borefield.results.max_temperature, 15.568308313315452)
    print(f'Simulation time with speed up, approximate_req_depth and explicit models {time.time() - start}s')


def test_monthly_quadrant_1():
    ground = GroundFluxTemperature(3.5, 9.6, flux=0.07)
    borefield = Borefield(ground_data=ground)
    borefield.calculation_setup(use_explicit_multipole=False)
    borefield.create_rectangular_borefield(10, 7, 6.5, 6.5, 100, 4, 0.075)
    borefield.fluid_data = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)
    borefield.flow_data = ConstantFlowRate(mfr=0.3)
    borefield.pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

    peak_heating_rel = np.array([1, .991, .802, .566, .264, 0, 0, 0, .066, .368, .698, .934])
    peak_cooling_rel = np.array([0, 0, 0, 0, .415, .756, 1, .976, .549, 0, 0, 0])
    bl_heating = np.array([.176, .174, .141, .1, .045, 0, 0, 0, .012, .065, .123, .164])
    bl_cooling = np.array([0, 0, 0, 0, .112, .205, .27, .264, .149, 0, 0, 0])

    load = MonthlyBuildingLoadAbsolute(300000 * bl_heating, 150000 * bl_cooling, 0 * peak_heating_rel,
                                       150 * peak_cooling_rel, efficiency_cooling=20, efficiency_heating=5)
    load.peak_duration = 8
    borefield.load = load
    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 82.41177541437784)
    assert np.isclose(borefield.results.min_temperature, 5.250350844132524)
    assert np.isclose(borefield.results.max_temperature, 16.00214239323884)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 82.4799174661786)
    assert np.isclose(borefield.results.min_temperature, 5.254132865075517)
    assert np.isclose(borefield.results.max_temperature, 15.998991197446832)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 82.41177541437784)
    assert np.isclose(borefield.results.min_temperature, 5.250350844132524)
    assert np.isclose(borefield.results.max_temperature, 16.00214239323884)
    print(f'Simulation time with speed up and approximate_req_depth {time.time() - start}s')


def test_monthly_quadrant_1_more_data_points():
    ground = GroundFluxTemperature(3.5, 9.6, flux=0.07)
    borefield = Borefield(ground_data=ground)
    borefield.calculation_setup(use_explicit_multipole=False)
    borefield.create_rectangular_borefield(10, 7, 6.5, 6.5, 100, 4, 0.075)
    borefield.fluid_data = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)
    borefield.flow_data = ConstantFlowRate(mfr=0.3)
    borefield.pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

    peak_heating_rel = np.array([1, .991, .802, .566, .264, 0, 0, 0, .066, .368, .698, .934])
    peak_cooling_rel = np.array([0, 0, 0, 0, .415, .756, 1, .976, .549, 0, 0, 0])
    bl_heating = np.array([.176, .174, .141, .1, .045, 0, 0, 0, .012, .065, .123, .164])
    bl_cooling = np.array([0, 0, 0, 0, .112, .205, .27, .264, .149, 0, 0, 0])

    load = MonthlyBuildingLoadAbsolute(300000 * bl_heating, 150000 * bl_cooling, 0 * peak_heating_rel,
                                       150 * peak_cooling_rel, efficiency_cooling=20, efficiency_heating=5)
    load.peak_duration = 8
    borefield.load = load
    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 82.41177541437784)
    assert np.isclose(borefield.results.min_temperature, 5.250350844132524)
    assert np.isclose(borefield.results.max_temperature, 16.00214239323884)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()
    borefield.borehole._nb_of_data_points = 500

    borefield.size_L3()
    assert np.isclose(borefield.H, 82.43767072911498)
    assert np.isclose(borefield.results.min_temperature, 5.251929773005157)
    assert np.isclose(borefield.results.max_temperature, 15.999110322935508)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 82.41177541437784)
    assert np.isclose(borefield.results.min_temperature, 5.2503510707281285)
    assert np.isclose(borefield.results.max_temperature, 16.000327510411708)
    print(f'Simulation time with speed up and approximate_req_depth {time.time() - start}s')


def test_monthly_quadrant_2():
    ground = GroundFluxTemperature(3.5, 9.6, flux=0.07)
    borefield = Borefield(ground_data=ground)
    borefield.calculation_setup(use_explicit_multipole=False)
    borefield.create_rectangular_borefield(10, 11, 6.5, 6.5, 100, 4, 0.075)
    borefield.fluid_data = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)
    borefield.flow_data = ConstantFlowRate(mfr=0.3)
    borefield.pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

    peak_heating_rel = np.array([1, .991, .802, .566, .264, 0, 0, 0, .066, .368, .698, .934])
    peak_cooling_rel = np.array([0, 0, 0, 0, .415, .756, 1, .976, .549, 0, 0, 0])
    bl_heating = np.array([.176, .174, .141, .1, .045, 0, 0, 0, .012, .065, .123, .164])
    bl_cooling = np.array([0, 0, 0, 0, .112, .205, .27, .264, .149, 0, 0, 0])

    load = MonthlyBuildingLoadAbsolute(160000 * bl_heating, 240000 * bl_cooling, 160 * peak_heating_rel,
                                       240 * peak_cooling_rel, efficiency_cooling=20, efficiency_heating=5)
    load.peak_duration = 8
    borefield.load = load
    borefield.USE_SPEED_UP_IN_SIZING = True
    borefield.set_min_fluid_temperature(0)
    borefield.set_max_fluid_temperature(17)

    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 115.2118575013218)
    assert np.isclose(borefield.results.min_temperature, 8.389238430692593)
    assert np.isclose(borefield.results.max_temperature, 16.999907039310955)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 115.18928587456186)
    assert np.isclose(borefield.results.min_temperature, 8.388569217689858)
    assert np.isclose(borefield.results.max_temperature, 17.000634432631973)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 115.2118575013218)
    assert np.isclose(borefield.results.min_temperature, 8.389238430692593)
    assert np.isclose(borefield.results.max_temperature, 16.999907039310955)
    print(f'Simulation time with speed up and approximate_req_depth {time.time() - start}s')


def test_case_office():
    borefield = Borefield()
    borefield.calculation_setup(use_explicit_multipole=False)
    borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
    borefield.ground_data = GroundFluxTemperature(3, 10)
    borefield.fluid_data = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)
    borefield.flow_data = ConstantFlowRate(vfr=0.3)
    borefield.pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_fluid_temperature(17)
    borefield.set_min_fluid_temperature(3)
    hourly_load = HourlyGeothermalLoad()
    hourly_load.simulation_period = 20
    hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\office.csv"), header=True, separator=";",
                                    col_injection=0, col_extraction=1)
    borefield.load = hourly_load

    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 130.66446763370453)
    assert np.isclose(borefield.results.min_temperature, 8.318173729158907)
    assert np.isclose(borefield.results.max_temperature, 17.038669695204497)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 132.4673002791876)
    assert np.isclose(borefield.results.min_temperature, 8.374020595608556)
    assert np.isclose(borefield.results.max_temperature, 17.000729593255436)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L4()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 130.66446763370453)
    assert np.isclose(borefield.results.min_temperature, 8.318173729158907)
    assert np.isclose(borefield.results.max_temperature, 17.038669695204497)
    print(f'Simulation time with speed up and approximate_req_depth {time.time() - start}s')

    borefield.calculation_setup(use_explicit_multipole=True)
    borefield.calculation_setup(approximate_req_depth=False)
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 130.66193708714195)
    assert np.isclose(borefield.results.min_temperature, 8.318247857757454)
    assert np.isclose(borefield.results.max_temperature, 17.003566759231216)
    print(f'Simulation time with speed up and explicit models {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 130.78132818358134)
    assert np.isclose(borefield.results.min_temperature, 8.32197886166622)
    assert np.isclose(borefield.results.max_temperature, 17.001305013407563)
    print(f'Simulation time without speed up and explicit models {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L4()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 130.66193708714195)
    assert np.isclose(borefield.results.min_temperature, 8.318247857757454)
    assert np.isclose(borefield.results.max_temperature, 17.003566759231216)
    print(f'Simulation time with speed up, approximate_req_depth and explicit models {time.time() - start}s')


def test_case_auditorium():
    borefield = Borefield()
    borefield.calculation_setup(use_explicit_multipole=False)
    borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
    borefield.ground_data = GroundFluxTemperature(3, 10)
    borefield.fluid_data = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)
    borefield.flow_data = ConstantFlowRate(vfr=0.3)
    borefield.pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_fluid_temperature(17)
    borefield.set_min_fluid_temperature(3)
    hourly_load = HourlyGeothermalLoad()
    hourly_load.simulation_period = 20
    hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True,
                                    separator=";", col_injection=0, col_extraction=1)
    borefield.load = hourly_load
    borefield.create_rectangular_borefield(5, 4, 6, 6, 110, 4, 0.075)

    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 131.76269387938362)
    assert np.isclose(borefield.results.min_temperature, 7.110055740728681)
    assert np.isclose(borefield.results.max_temperature, 17.022233519266145)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 133.02284452056082)
    assert np.isclose(borefield.results.min_temperature, 7.159205196665665)
    assert np.isclose(borefield.results.max_temperature, 17.001111980643916)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L4()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 131.76269387938362)
    assert np.isclose(borefield.results.min_temperature, 7.110055740728681)
    assert np.isclose(borefield.results.max_temperature, 17.022233519266145)
    print(f'Simulation time with speed up and approximate_req_depth {time.time() - start}s')


def test_case_swimming_pool():
    borefield = Borefield()
    borefield.calculation_setup(use_explicit_multipole=False)
    borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
    borefield.ground_data = GroundFluxTemperature(3, 10)
    borefield.fluid_data = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)
    borefield.flow_data = ConstantFlowRate(vfr=0.3)
    borefield.pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_fluid_temperature(17)
    borefield.set_min_fluid_temperature(3)
    hourly_load = HourlyGeothermalLoad()
    hourly_load.simulation_period = 20

    hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\swimming_pool.csv"), header=True,
                                    separator=";", col_injection=0, col_extraction=1)
    borefield.load = hourly_load
    borefield.create_rectangular_borefield(15, 20, 6, 6, 110, 4, 0.075)
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 301.64200169879945)
    assert np.isclose(borefield.results.min_temperature, 3.0001878903488888)
    assert np.isclose(borefield.results.max_temperature, 12.91917014081557)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    print(borefield.H, borefield.results.min_temperature, borefield.results.max_temperature)

    assert np.isclose(borefield.H, 301.6420030473213)
    assert np.isclose(borefield.results.min_temperature, 3.000187935887761)
    assert np.isclose(borefield.results.max_temperature, 12.919170154744883)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L4()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 301.64200169879945)
    assert np.isclose(borefield.results.min_temperature, 3.0001878903488888)
    assert np.isclose(borefield.results.max_temperature, 12.91917014081557)
    print(f'Simulation time with speed up and approximate_req_depth {time.time() - start}s')


def test_case_auditorium_active_passive():
    borefield = Borefield()
    borefield.calculation_setup(use_explicit_multipole=False)
    borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
    borefield.ground_data = GroundFluxTemperature(3, 10)
    borefield.fluid_data = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)
    borefield.flow_data = ConstantFlowRate(vfr=0.3)
    borefield.pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_fluid_temperature(25)
    borefield.set_min_fluid_temperature(3)
    hourly_load = HourlyBuildingLoad()
    hourly_load.simulation_period = 20
    hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True,
                                    separator=";", col_cooling=0, col_heating=1)
    hourly_load.eer = EERCombined(20, 5, 17)
    borefield.load = hourly_load
    borefield.create_rectangular_borefield(5, 4, 6, 6, 110, 4, 0.075)
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 51.55180221798138)
    assert np.isclose(borefield.results.min_temperature, 3.000432898708333)
    assert np.isclose(borefield.results.max_temperature, 23.709306900929022)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 51.55180221798138)
    assert np.isclose(borefield.results.min_temperature, 3.000432898708333)
    assert np.isclose(borefield.results.max_temperature, 23.709306900929022)
    print(f'Simulation time without speed up {time.time() - start}s')
