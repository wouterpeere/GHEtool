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
    assert np.isclose(borefield.H, 93.05654758180941)
    assert np.isclose(borefield.results.min_temperature, -1.771529250405024e-06)
    assert np.isclose(borefield.results.max_temperature, 15.57317638444852)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 93.05737320261332)
    assert np.isclose(borefield.results.min_temperature, -6.434965902357703e-07)
    assert np.isclose(borefield.results.max_temperature, 15.57314567825897)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 93.05654758180941)
    assert np.isclose(borefield.results.min_temperature, -1.771529250405024e-06)
    assert np.isclose(borefield.results.max_temperature, 15.57317638444852)
    print(f'Simulation time with speed up and approximate_req_depth {time.time() - start}s')

    borefield.calculation_setup(use_explicit_multipole=True)
    borefield.calculation_setup(approximate_req_depth=False)
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 93.0298736599179)
    assert np.isclose(borefield.results.min_temperature, -6.978619486730508e-07)
    assert np.isclose(borefield.results.max_temperature, 15.56888506644774)
    print(f'Simulation time with speed up and explicit models {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 93.0299429145191)
    assert np.isclose(borefield.results.min_temperature, -6.935132264018762e-07)
    assert np.isclose(borefield.results.max_temperature, 15.568882503224488)
    print(f'Simulation time without speed up and explicit models {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 93.0298736599179)
    assert np.isclose(borefield.results.min_temperature, -6.978619486730508e-07)
    assert np.isclose(borefield.results.max_temperature, 15.56888506644774)
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
    assert np.isclose(borefield.H, 82.39860433268365)
    assert np.isclose(borefield.results.min_temperature, 5.262135922063676)
    assert np.isclose(borefield.results.max_temperature, 16.003006724834492)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L3()
    print(borefield.H, borefield.results.min_temperature, borefield.results.max_temperature)
    assert np.isclose(borefield.H, 82.46326214379562)
    assert np.isclose(borefield.results.min_temperature, 5.264946847691636)
    assert np.isclose(borefield.results.max_temperature, 15.999999998666684)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    borefield.calculation_setup(approximate_req_depth=True)
    print(borefield.H, borefield.results.min_temperature, borefield.results.max_temperature)
    assert np.isclose(borefield.H, 82.39860433268365)
    assert np.isclose(borefield.results.min_temperature, 5.262135922063676)
    assert np.isclose(borefield.results.max_temperature, 16.003006724834492)
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
    assert np.isclose(borefield.H, 82.39860433268365)
    assert np.isclose(borefield.results.min_temperature, 5.262135922063676)
    assert np.isclose(borefield.results.max_temperature, 16.003006724834492)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()
    borefield.borehole._nb_of_data_points = 500

    borefield.size_L3()
    assert np.isclose(borefield.H, 82.42429689439584)
    assert np.isclose(borefield.results.min_temperature, 5.2637093371255945)
    assert np.isclose(borefield.results.max_temperature, 15.999999924377677)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 82.39860433268365)
    assert np.isclose(borefield.results.min_temperature, 5.262136137196954)
    assert np.isclose(borefield.results.max_temperature, 16.001207717423252)
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
    assert np.isclose(borefield.H, 115.26554111270471)
    assert np.isclose(borefield.results.min_temperature, 8.390821841206733)
    assert np.isclose(borefield.results.max_temperature, 16.999250592024296)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 115.24651636406257)
    assert np.isclose(borefield.results.min_temperature, 8.390257200148307)
    assert np.isclose(borefield.results.max_temperature, 16.999999855492447)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 115.26554111270471)
    assert np.isclose(borefield.results.min_temperature, 8.390821841206733)
    assert np.isclose(borefield.results.max_temperature, 16.999250592024296)
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
    assert np.isclose(borefield.H, 130.71695149056347)
    assert np.isclose(borefield.results.min_temperature, 8.319815787199419)
    assert np.isclose(borefield.results.max_temperature, 17.03756286071479)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 132.47709003123953)
    assert np.isclose(borefield.results.min_temperature, 8.374294640785031)
    assert np.isclose(borefield.results.max_temperature, 17.00054207088482)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L4()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 130.71695149056347)
    assert np.isclose(borefield.results.min_temperature, 8.319815787199419)
    assert np.isclose(borefield.results.max_temperature, 17.03756286071479)
    print(f'Simulation time with speed up and approximate_req_depth {time.time() - start}s')

    borefield.calculation_setup(use_explicit_multipole=True)
    borefield.calculation_setup(approximate_req_depth=False)
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 130.71438790857485)
    assert np.isclose(borefield.results.min_temperature, 8.319888848576895)
    assert np.isclose(borefield.results.max_temperature, 17.0025716858377)
    print(f'Simulation time with speed up and explicit models {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 130.90713618148186)
    assert np.isclose(borefield.results.min_temperature, 8.325906567651355)
    assert np.isclose(borefield.results.max_temperature, 16.99892742981564)
    print(f'Simulation time without speed up and explicit models {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L4()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 130.71438790857485)
    assert np.isclose(borefield.results.min_temperature, 8.319888848576895)
    assert np.isclose(borefield.results.max_temperature, 17.0025716858377)
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
    assert np.isclose(borefield.H, 131.82733169722147)
    assert np.isclose(borefield.results.min_temperature, 7.111225215106762)
    assert np.isclose(borefield.results.max_temperature, 17.021118745623)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 133.09029368923098)
    assert np.isclose(borefield.results.min_temperature, 7.16238543081485)
    assert np.isclose(borefield.results.max_temperature, 17.00000000016381)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L4()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 131.82733169722147)
    assert np.isclose(borefield.results.min_temperature, 7.111225215106762)
    assert np.isclose(borefield.results.max_temperature, 17.021118745623)
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
    assert np.isclose(borefield.H, 301.68298615990733)
    assert np.isclose(borefield.results.min_temperature, 2.9998608708664563)
    assert np.isclose(borefield.results.max_temperature, 12.919593360833481)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    print(borefield.H, borefield.results.min_temperature, borefield.results.max_temperature)

    assert np.isclose(borefield.H, 301.68298748462246)
    assert np.isclose(borefield.results.min_temperature, 2.999860921598256)
    assert np.isclose(borefield.results.max_temperature, 12.919593374507821)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L4()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 301.68298615990733)
    assert np.isclose(borefield.results.min_temperature, 2.9998608708664563)
    assert np.isclose(borefield.results.max_temperature, 12.919593360833481)
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
    assert np.isclose(borefield.H, 51.50057378245197)
    assert np.isclose(borefield.results.min_temperature, 2.9999999939722155)
    assert np.isclose(borefield.results.max_temperature, 23.72051656414498)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 51.50057378245197)
    assert np.isclose(borefield.results.min_temperature, 2.9999999939722155)
    assert np.isclose(borefield.results.max_temperature, 23.72051656414498)
    print(f'Simulation time without speed up {time.time() - start}s')
