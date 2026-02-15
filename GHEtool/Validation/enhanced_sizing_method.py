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
    assert np.isclose(borefield.H, 93.24146806456535)
    assert np.isclose(borefield.results.min_temperature, 0.0001600069660581127)
    assert np.isclose(borefield.results.max_temperature, 15.739507592388385)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 93.243081505459)
    assert np.isclose(borefield.results.min_temperature, 0.00015381852217721814)
    assert np.isclose(borefield.results.max_temperature, 15.739453158826853)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 93.24146806456535)
    assert np.isclose(borefield.results.min_temperature, 0.0001600069660581127)
    assert np.isclose(borefield.results.max_temperature, 15.739507592388385)
    print(f'Simulation time with speed up and approximate_req_depth {time.time() - start}s')

    borefield.calculation_setup(use_explicit_multipole=True)
    borefield.calculation_setup(approximate_req_depth=False)
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 93.21459868840302)
    assert np.isclose(borefield.results.min_temperature, 0.00016020852361098292)
    assert np.isclose(borefield.results.max_temperature, 15.728080432710481)
    print(f'Simulation time with speed up and explicit models {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 93.21528026470325)
    assert np.isclose(borefield.results.min_temperature, 0.00015743055001760098)
    assert np.isclose(borefield.results.max_temperature, 15.728056277153398)
    print(f'Simulation time without speed up and explicit models {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 93.21459868840302)
    assert np.isclose(borefield.results.min_temperature, 0.00016020852361098292)
    assert np.isclose(borefield.results.max_temperature, 15.728080432710481)
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
    assert np.isclose(borefield.H, 85.79127756099108)
    assert np.isclose(borefield.results.min_temperature, 5.451954106073291)
    assert np.isclose(borefield.results.max_temperature, 16.009933134246406)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 86.04140068480496)
    assert np.isclose(borefield.results.min_temperature, 5.459660593826807)
    assert np.isclose(borefield.results.max_temperature, 15.999214960639087)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 85.79127756099108)
    assert np.isclose(borefield.results.min_temperature, 5.451954106073291)
    assert np.isclose(borefield.results.max_temperature, 16.009933134246406)
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
    assert np.isclose(borefield.H, 85.79127756099108)
    assert np.isclose(borefield.results.min_temperature, 5.451954106073291)
    assert np.isclose(borefield.results.max_temperature, 16.009933134246406)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()
    borefield.borehole._nb_of_data_points = 500

    borefield.size_L3()
    assert np.isclose(borefield.H, 85.9223631352438)
    assert np.isclose(borefield.results.min_temperature, 5.459485430207949)
    assert np.isclose(borefield.results.max_temperature, 15.999114386583042)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 85.79127756099108)
    assert np.isclose(borefield.results.min_temperature, 5.451954394523563)
    assert np.isclose(borefield.results.max_temperature, 16.004510365189816)
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
    assert np.isclose(borefield.H, 117.42360117447696)
    assert np.isclose(borefield.results.min_temperature, 8.448478389721295)
    assert np.isclose(borefield.results.max_temperature, 17.000155792690094)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 117.40961843257512)
    assert np.isclose(borefield.results.min_temperature, 8.448073848783803)
    assert np.isclose(borefield.results.max_temperature, 17.000585066710645)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L3()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 117.42360117447696)
    assert np.isclose(borefield.results.min_temperature, 8.448478389721295)
    assert np.isclose(borefield.results.max_temperature, 17.000155792690094)
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
    assert np.isclose(borefield.H, 141.9659861806117)
    assert np.isclose(borefield.results.min_temperature, 8.643499473771335)
    assert np.isclose(borefield.results.max_temperature, 17.000616753506712)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 141.965075411997)
    assert np.isclose(borefield.results.min_temperature, 8.643452832019406)
    assert np.isclose(borefield.results.max_temperature, 17.000654666548748)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L4()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 141.9659861806117)
    assert np.isclose(borefield.results.min_temperature, 8.643499473771335)
    assert np.isclose(borefield.results.max_temperature, 17.000616753506712)
    print(f'Simulation time with speed up and approximate_req_depth {time.time() - start}s')

    borefield.calculation_setup(use_explicit_multipole=True)
    borefield.calculation_setup(approximate_req_depth=False)
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 141.95646363193922)
    assert np.isclose(borefield.results.min_temperature, 8.643374849202972)
    assert np.isclose(borefield.results.max_temperature, 17.000615221248903)
    print(f'Simulation time with speed up and explicit models {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 141.9566103028618)
    assert np.isclose(borefield.results.min_temperature, 8.643378819194513)
    assert np.isclose(borefield.results.max_temperature, 17.000611682426978)
    print(f'Simulation time without speed up and explicit models {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L4()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 141.95646363193922)
    assert np.isclose(borefield.results.min_temperature, 8.643374849202972)
    assert np.isclose(borefield.results.max_temperature, 17.000615221248903)
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
    assert np.isclose(borefield.H, 146.5617348169237)
    assert np.isclose(borefield.results.min_temperature, 7.627999444626022)
    assert np.isclose(borefield.results.max_temperature, 17.000602713187273)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 146.56434784374707)
    assert np.isclose(borefield.results.min_temperature, 7.62890725121998)
    assert np.isclose(borefield.results.max_temperature, 17.00056637799696)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L4()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 146.5617348169237)
    assert np.isclose(borefield.results.min_temperature, 7.627999444626022)
    assert np.isclose(borefield.results.max_temperature, 17.000602713187273)
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
    assert np.isclose(borefield.H, 301.7227470622562)
    assert np.isclose(borefield.results.min_temperature, 3.0001872515499888)
    assert np.isclose(borefield.results.max_temperature, 12.919492493925734)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 301.7227592617909)
    assert np.isclose(borefield.results.min_temperature, 3.0001877071926537)
    assert np.isclose(borefield.results.max_temperature, 12.919492619924261)
    print(f'Simulation time without speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = True

    start = time.time()

    borefield.size_L4()
    borefield.calculation_setup(approximate_req_depth=True)
    assert np.isclose(borefield.H, 301.7227470622555)
    assert np.isclose(borefield.results.min_temperature, 3.0001872515499928)
    assert np.isclose(borefield.results.max_temperature, 12.919492493925727)
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
    assert np.isclose(borefield.H, 51.676740693499106)
    assert np.isclose(borefield.results.min_temperature, 3.0002733156958086)
    assert np.isclose(borefield.results.max_temperature, 23.824518064283197)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 51.676740693499106)
    assert np.isclose(borefield.results.min_temperature, 3.0002733156958086)
    assert np.isclose(borefield.results.max_temperature, 23.824518064283197)
    print(f'Simulation time without speed up {time.time() - start}s')
