"""
This file contains a couple of sizing examples to show the enhanced speed and accuracy of the new method implemented
in issue 403. When working with variable fluid properties, the Rb* calculation takes quite a lot of time. In order to
save some, interpolation is used (default 50 values). However, this also introduces an interpolation error.

In this new method, only the min and max temperatures are used and directly calculated instead of being interpolated.
This results in a more accurate sizing, since the limits are used directly.
"""
from GHEtool import *
import numpy as np

import time


def test_monthly_quadrant_4():
    ground = GroundFluxTemperature(3.5, 9.6, flux=0.07)
    borefield = Borefield(ground_data=ground)
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
    assert np.isclose(borefield.H, 93.26359850472193)
    assert np.isclose(borefield.results.min_temperature, 0.0001445559281965103)
    assert np.isclose(borefield.results.max_temperature, 15.625961732265106)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 93.26372520583197)
    assert np.isclose(borefield.results.min_temperature, 0.00014378529190839373)
    assert np.isclose(borefield.results.max_temperature, 15.625956914178497)
    print(f'Simulation time without speed up {time.time() - start}s')


def test_monthly_quadrant_1():
    ground = GroundFluxTemperature(3.5, 9.6, flux=0.07)
    borefield = Borefield(ground_data=ground)
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
    assert np.isclose(borefield.H, 83.09881599111853)
    assert np.isclose(borefield.results.min_temperature, 5.296214968773752)
    assert np.isclose(borefield.results.max_temperature, 16.00273196708503)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 83.17430886882794)
    assert np.isclose(borefield.results.min_temperature, 5.300760137618011)
    assert np.isclose(borefield.results.max_temperature, 15.99936830071769)
    print(f'Simulation time without speed up {time.time() - start}s')


def test_monthly_quadrant_1_more_data_points():
    ground = GroundFluxTemperature(3.5, 9.6, flux=0.07)
    borefield = Borefield(ground_data=ground)
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
    assert np.isclose(borefield.H, 83.09881599111853)
    assert np.isclose(borefield.results.min_temperature, 5.296214968773752)
    assert np.isclose(borefield.results.max_temperature, 16.00273196708503)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()
    borefield.borehole._nb_of_data_points = 500

    borefield.size_L3()
    assert np.isclose(borefield.H, 83.09936353547558)
    assert np.isclose(borefield.results.min_temperature, 5.29624824242701)
    assert np.isclose(borefield.results.max_temperature, 15.99936830071769)
    print(f'Simulation time without speed up {time.time() - start}s')


def test_monthly_quadrant_2():
    ground = GroundFluxTemperature(3.5, 9.6, flux=0.07)
    borefield = Borefield(ground_data=ground)
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
    borefield.set_min_avg_fluid_temperature(0)
    borefield.set_max_avg_fluid_temperature(17)

    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 116.00524762354382)
    assert np.isclose(borefield.results.min_temperature, 8.407099988410305)
    assert np.isclose(borefield.results.max_temperature, 17.001626884710568)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L3()
    assert np.isclose(borefield.H, 116.0394997074172)
    assert np.isclose(borefield.results.min_temperature, 8.408106764334239)
    assert np.isclose(borefield.results.max_temperature, 17.000621479904506)
    print(f'Simulation time without speed up {time.time() - start}s')


def test_case_office():
    borefield = Borefield()
    borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
    borefield.ground_data = GroundFluxTemperature(3, 10)
    borefield.fluid_data = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)
    borefield.flow_data = ConstantFlowRate(vfr=0.3)
    borefield.pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_avg_fluid_temperature(17)
    borefield.set_min_avg_fluid_temperature(3)
    hourly_load = HourlyGeothermalLoad()
    hourly_load.simulation_period = 20
    hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\office.csv"), header=True, separator=";",
                                    col_injection=0, col_extraction=1)
    borefield.load = hourly_load

    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 141.96534390958553)
    assert np.isclose(borefield.results.min_temperature, 8.643460326864346)
    assert np.isclose(borefield.results.max_temperature, 17.00064802237182)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 141.968830876313)
    assert np.isclose(borefield.results.min_temperature, 8.643563349090133)
    assert np.isclose(borefield.results.max_temperature, 17.00055762922439)
    print(f'Simulation time without speed up {time.time() - start}s')


def test_case_auditorium():
    borefield = Borefield()
    borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
    borefield.ground_data = GroundFluxTemperature(3, 10)
    borefield.fluid_data = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)
    borefield.flow_data = ConstantFlowRate(vfr=0.3)
    borefield.pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_avg_fluid_temperature(17)
    borefield.set_min_avg_fluid_temperature(3)
    hourly_load = HourlyGeothermalLoad()
    hourly_load.simulation_period = 20
    hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True,
                                    separator=";",
                                    col_injection=0, col_extraction=1)
    borefield.load = hourly_load
    borefield.create_rectangular_borefield(5, 4, 6, 6, 110, 4, 0.075)

    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 146.56168945870414)
    assert np.isclose(borefield.results.min_temperature, 7.627998329436393)
    assert np.isclose(borefield.results.max_temperature, 17.00060373723548)
    print(f'Simulation time with speed up {time.time() - start}s')

    borefield.USE_SPEED_UP_IN_SIZING = False
    start = time.time()

    borefield.size_L4()
    assert np.isclose(borefield.H, 146.56251979924573)
    assert np.isclose(borefield.results.min_temperature, 7.628019277863065)
    assert np.isclose(borefield.results.max_temperature, 17.000585005188466)
    print(f'Simulation time without speed up {time.time() - start}s')


def test_case_swimming_pool():
    borefield = Borefield()
    borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
    borefield.ground_data = GroundFluxTemperature(3, 10)
    borefield.fluid_data = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)
    borefield.flow_data = ConstantFlowRate(vfr=0.3)
    borefield.pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_avg_fluid_temperature(17)
    borefield.set_min_avg_fluid_temperature(3)
    hourly_load = HourlyGeothermalLoad()
    hourly_load.simulation_period = 20

    hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\swimming_pool.csv"), header=True,
                                    separator=";",
                                    col_injection=0, col_extraction=1)
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
