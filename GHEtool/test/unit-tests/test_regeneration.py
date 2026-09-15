import numpy as np
import pandas as pd
import pytest

from GHEtool import *

from GHEtool.VariableClasses import HourlyBuildingLoad
from GHEtool.VariableClasses.Regeneration import Regeneration
from GHEtool.Methods.regeneration import calculate_regeneration


def test_regeneration_only_power():
    regeneration = Regeneration(200)
    assert regeneration.power == 200
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 5, 1, 4000), 200)
    regeneration.surface = 10
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 5, 1, 4000), 2000)
    regeneration.surface = 1
    regeneration = Regeneration(np.array([200, 300, 400]))
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 5, 1, 4000), 200)
    assert np.isclose(regeneration.get_regeneration_power_inlet(1, 5, 1, 4000), 300)
    assert np.isclose(regeneration.get_regeneration_power_inlet(2, 5, 1, 4000), 400)
    regeneration = Regeneration(np.array([200, 300, 400]), 1, a1=1, a2=2, min_delta_T=10)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 5, 1, 4000), 277.1363490516876)
    assert np.isclose(regeneration.get_regeneration_power_inlet(1, 5, 1, 4000), 376.8268535360164)
    assert np.isclose(regeneration.get_regeneration_power_inlet(2, 5, 1, 4000), 476.51797723702316)
    regeneration = Regeneration(np.array([200, 300, 400]), np.array([1, 1, 1]), a1=1, a2=2, min_delta_T=10)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 5, 1, 4000), 277.1363490516876)
    assert np.isclose(regeneration.get_regeneration_power_inlet(1, 5, 1, 4000), 376.8268535360164)
    assert np.isclose(regeneration.get_regeneration_power_inlet(2, 5, 1, 4000), 476.51797723702316)


def test_regeneration_temperature():
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0.1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 0, 1, 4000), 0.5999475405360499)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0.1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 2, 1, 4000), -0.39998496959015023)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0.001)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 0, 1, 4000), 0.5009681558476586)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 0, 1, 4000), 0.4999687519530029)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 2, 1, 4000), -0.4999687519530029)

    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=5e6, a2=0.1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 0, 1, 4000), 4000)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=5e6, a2=0.1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 2, 1, 4000), -4000)
    regeneration = Regeneration(power=100, temperature=np.array([1, 1, 1]), a1=5e6, a2=0.1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 2, 1, 4000), -4000)
    regeneration = Regeneration(power=10000, temperature=np.array([1, 1, 1]), a1=5e6, a2=0.1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 1, 1, 4000), 15.974437701515852)
    regeneration = Regeneration(power=10000, temperature=np.array([1, 1, 1]), a1=5e6, a2=0.1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 0, 1, 4000), 8003.194889170117)

    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=5e6)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 0, 1, 4000), 4000)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=5e6)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 2, 1, 4000), -4000)
    regeneration = Regeneration(power=100, temperature=np.array([1, 1, 1]), a1=5e6)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 2, 1, 4000), -4000)
    regeneration = Regeneration(power=10000, temperature=np.array([1, 1, 1]), a1=5e6)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 1, 1, 4000), 15.974437701515852)
    regeneration = Regeneration(power=10000, temperature=np.array([1, 1, 1]), a1=5e6)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 0, 1, 4000), 8003.194889170117)
    regeneration = Regeneration(power=10000, temperature=np.array([1, 1, 1]), a1=100)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 2, 1, 4000), 9777.777777777777)
    regeneration = Regeneration(power=10000, temperature=np.array([1, 1, 1]), a1=100, a2=1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 2, 1, 4000), 9782.657761064684)


def test_regeneration_temperature_min_delta():
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0.1, min_delta_T=1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(1, -1, 1, 4000), 0.5999475405360499)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0.1, min_delta_T=1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(1, 1, 1, 4000), 0)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0.001, min_delta_T=1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(-1, -1, 1, 4000), 0.5009681558476586)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0.1, min_delta_T=1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 3, 1, 4000), -0.39998496959015023)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0, min_delta_T=1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(-1, -1, 1, 4000), 0.4999687519530029)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, min_delta_T=1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(-1, -1, 1, 4000), 0.4999687519530029)


def test_ensure_max_limit():
    ground_data = GroundFluxTemperature(2, 10)
    fluid_data = TemperatureDependentFluidData('MPG', 0, mass_percentage=False)
    flow_data = ConstantDeltaTFlowRate(delta_temp_extraction=3, delta_temp_injection=3)
    pipe_data = DoubleUTube(1, 0.013, 0.016, 0.4, 0.035)
    borefield = Borefield()
    borefield.create_rectangular_borefield(4, 3, 6, 6, 105, 0.7, 0.07)
    borefield.ground_data = ground_data
    borefield.fluid_data = fluid_data
    borefield.flow_data = flow_data
    borefield.pipe_data = pipe_data
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_fluid_temperature(20)
    borefield.set_min_fluid_temperature(5.5)
    hourly_load_building = HourlyBuildingLoad(efficiency_cooling=7, efficiency_heating=6)

    hourly_load_building.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/auditorium.csv"), header=True,
                                             separator=";", col_cooling=0, col_heating=1)
    borefield.load = hourly_load_building
    borefield.load.simulation_period = 5

    # get weather data
    weather_file = open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb')
    weather_file.seek(0)
    TMY: pd.DataFrame = pd.read_csv(weather_file, sep=",", header=None, skiprows=8)

    TMY.drop(columns=TMY.columns[:5], inplace=True)
    solar: np.ndarray = np.tile(np.array(TMY.iloc[:, 8]), 20)
    temperature: np.ndarray = np.tile(np.array(TMY.iloc[:, 1]), 20)

    # initiate regeneration object
    a0 = 0.45
    a1 = 24.76  # W/K/m²

    surface = 200  # m²

    regeneration_object = Regeneration(power=solar * a0 * surface * 2, temperature=temperature, a1=a1 * surface)

    proceeding_my, proceeding = calculate_regeneration(
        borefield=borefield,
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='proceeding',
        simulation_horizon=8760 * 2)

    # with a time horizon of 2 years, the peak next year will not be forgotten
    assert np.isclose(np.sum(proceeding[:8760]), 0)

    roceeding_my, proceeding = calculate_regeneration(
        borefield=borefield,
        regen_obj=regeneration_object,
        rules=(1, 2,),
        algorithm='proceeding',
        simulation_horizon=8760 * 2)

    # without rule three, the simulation horizon is of no importance
    assert np.isclose(np.sum(proceeding[:8760]), 19134.841382664712)

    # one year simulation horizon
    proceeding_my, proceeding = calculate_regeneration(
        borefield=borefield,
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='proceeding', simulation_horizon=8760)
    # there is regeneration right after the peak so it ignores the peak in 8760 hours
    assert np.isclose(np.sum(proceeding[:8760]), 9.069911501402991)

    # 100 hours simulation horizon
    proceeding_my, proceeding = calculate_regeneration(
        borefield=borefield,
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='proceeding', simulation_horizon=100)
    # way more regeneration due to smaller time horizon
    assert np.isclose(np.sum(proceeding[:8760]), 18933.931812094048)

    # 100 hours simulation horizon
    proceeding_my, proceeding = calculate_regeneration(
        borefield=borefield,
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='proceeding', simulation_horizon=100, position_regeneration='outlet')

    # way more regeneration due to smaller time horizon, but smaller than for inlet
    assert np.isclose(np.sum(proceeding[:8760]), 18634.19248501228)


def test_regeneration_error():
    ground_data = GroundFluxTemperature(2, 10)
    fluid_data = TemperatureDependentFluidData('MPG', 0, mass_percentage=False)
    flow_data = ConstantDeltaTFlowRate(delta_temp_extraction=3, delta_temp_injection=3)
    pipe_data = DoubleUTube(1, 0.013, 0.016, 0.4, 0.035)
    borefield = Borefield()
    borefield.create_rectangular_borefield(4, 3, 6, 6, 105, 0.7, 0.07)
    borefield.ground_data = ground_data
    borefield.fluid_data = fluid_data
    borefield.flow_data = flow_data
    borefield.pipe_data = pipe_data
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_fluid_temperature(20)
    borefield.set_min_fluid_temperature(5.5)
    hourly_load_building = HourlyBuildingLoad(efficiency_cooling=7, efficiency_heating=6)

    hourly_load_building.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/auditorium.csv"), header=True,
                                             separator=";", col_cooling=0, col_heating=1)
    borefield.load = hourly_load_building
    borefield.load.simulation_period = 5

    # get weather data
    weather_file = open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb')
    weather_file.seek(0)
    TMY: pd.DataFrame = pd.read_csv(weather_file, sep=",", header=None, skiprows=8)

    TMY.drop(columns=TMY.columns[:5], inplace=True)
    solar: np.ndarray = np.tile(np.array(TMY.iloc[:, 8]), 20)
    temperature: np.ndarray = np.tile(np.array(TMY.iloc[:, 1]), 20)

    # initiate regeneration object
    a0 = 0.45
    a1 = 24.76  # W/K/m²

    surface = 200  # m²

    regeneration_object = Regeneration(power=solar * a0 * surface * 2, temperature=temperature, a1=a1 * surface)
    borefield.borehole.use_constant_Rb = True
    with pytest.raises(ValueError):
        calculate_regeneration(
            borefield=borefield,
            regen_obj=regeneration_object,
            rules=(1, 2, 3),
            algorithm='proceeding',
            simulation_horizon=8760 * 2)
    borefield.borehole.use_constant_Rb = False
    with pytest.raises(ValueError):
        calculate_regeneration(
            borefield=borefield,
            regen_obj=regeneration_object,
            rules=(1, 2, 3),
            algorithm='proceeding',
            simulation_horizon=8760 * 2, position_regeneration='outlett')
    borefield.borehole.flow_data = VariableHourlyFlowRate(mfr=np.ones(8760))
    with pytest.raises(ValueError):
        calculate_regeneration(
            borefield=borefield,
            regen_obj=regeneration_object,
            rules=(1, 2, 3),
            algorithm='proceeding',
            simulation_horizon=8760 * 2)


def test_yearly_multiyearly():
    ground_data = GroundFluxTemperature(2, 10)
    fluid_data = TemperatureDependentFluidData('MPG', 0, mass_percentage=False)
    flow_data = ConstantDeltaTFlowRate(delta_temp_extraction=3, delta_temp_injection=3)
    pipe_data = DoubleUTube(1, 0.013, 0.016, 0.4, 0.035)
    borefield = Borefield()
    borefield.create_rectangular_borefield(4, 3, 6, 6, 105, 0.7, 0.07)
    borefield.ground_data = ground_data
    borefield.fluid_data = fluid_data
    borefield.flow_data = flow_data
    borefield.pipe_data = pipe_data
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_fluid_temperature(25)
    borefield.set_min_fluid_temperature(5.5)
    hourly_load_building = HourlyBuildingLoad(efficiency_cooling=7, efficiency_heating=6)

    hourly_load_building.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/auditorium.csv"), header=True,
                                             separator=";", col_cooling=0, col_heating=1)
    borefield.load = hourly_load_building
    borefield.load.simulation_period = 5

    # get weather data
    weather_file = open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb')
    weather_file.seek(0)
    TMY: pd.DataFrame = pd.read_csv(weather_file, sep=",", header=None, skiprows=8)

    TMY.drop(columns=TMY.columns[:5], inplace=True)
    solar: np.ndarray = np.tile(np.array(TMY.iloc[:, 8]), 20)
    temperature: np.ndarray = np.tile(np.array(TMY.iloc[:, 1]), 20)

    # initiate regeneration object
    a0 = 0.45
    a1 = 24.76  # W/K/m²

    surface = 200  # m²

    regeneration_object = Regeneration(power=solar * a0 * surface * 2, temperature=temperature, a1=a1 * surface)

    _, yearly = calculate_regeneration(
        borefield=borefield,
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='yearly',
        simulation_horizon=8760)

    _, total = calculate_regeneration(
        borefield=borefield,
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='total',
        simulation_horizon=8760)

    # should be identical since there is still remaining imbalance
    assert np.all(yearly >= 0)
    assert np.all(total >= 0)
    assert np.allclose(yearly, total)

    np.allclose(_.hourly_regeneration_load_simulation_period, total)


def test_proceeding_extra():
    ground_data = GroundFluxTemperature(2, 10)
    fluid_data = TemperatureDependentFluidData('MPG', 0, mass_percentage=False)
    flow_data = ConstantDeltaTFlowRate(delta_temp_extraction=3, delta_temp_injection=3)
    pipe_data = DoubleUTube(1, 0.013, 0.016, 0.4, 0.035)
    borefield = Borefield()
    borefield.create_rectangular_borefield(4, 3, 6, 6, 105, 0.7, 0.07)
    borefield.ground_data = ground_data
    borefield.fluid_data = fluid_data
    borefield.flow_data = flow_data
    borefield.pipe_data = pipe_data
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_fluid_temperature(30)
    borefield.set_min_fluid_temperature(5.5)
    hourly_load_building = HourlyBuildingLoad(efficiency_cooling=7, efficiency_heating=6)

    hourly_load_building.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/auditorium.csv"), header=True,
                                             separator=";", col_cooling=0, col_heating=1)
    borefield.load = hourly_load_building
    borefield.load.simulation_period = 5

    # get weather data
    weather_file = open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb')
    weather_file.seek(0)
    TMY: pd.DataFrame = pd.read_csv(weather_file, sep=",", header=None, skiprows=8)

    TMY.drop(columns=TMY.columns[:5], inplace=True)
    solar: np.ndarray = np.tile(np.array(TMY.iloc[:, 8]), 20)
    temperature: np.ndarray = np.tile(np.array(TMY.iloc[:, 1]), 20)

    # initiate regeneration object
    a0 = 0.45
    a1 = 24.76  # W/K/m²

    surface = 200  # m²

    regeneration_object = Regeneration(power=solar * a0 * surface * 2, temperature=temperature, a1=a1 * surface)

    _, proceeding_extra = calculate_regeneration(
        borefield=borefield,
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='proceeding_extra',
        simulation_horizon=8760)

    assert np.any(proceeding_extra < 0)
    _, proceeding = calculate_regeneration(
        borefield=borefield,
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='proceeding',
        simulation_horizon=8760)

    # more regeneration with proceeding extra
    assert np.isclose(np.sum(proceeding_extra[proceeding_extra >= 0]), 129587.40836822524)
    assert np.isclose(np.sum(proceeding), 129243.70464857337)

    assert np.any(proceeding_extra < 0)
    _, proceeding = calculate_regeneration(
        borefield=borefield,
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='proceeding_extra',
        simulation_horizon=8760, position_regeneration='outlet')
    assert np.isclose(np.sum(proceeding_extra[proceeding_extra >= 0]), 129587.40836822524)


def test_equal_with_different_horizons():
    # get weather data
    weather_file = open(FOLDER.joinpath("Examples/BEL_Brussels.064510_IWEC.epw"), 'rb')
    weather_file.seek(0)
    TMY: pd.DataFrame = pd.read_csv(weather_file, sep=",", header=None, skiprows=8)

    TMY.drop(columns=TMY.columns[:5], inplace=True)
    solar: np.ndarray = np.tile(np.array(TMY.iloc[:, 8]), 20)
    temperature: np.ndarray = np.tile(np.array(TMY.iloc[:, 1]), 20)

    a0 = 0.47
    a1 = 22.9  # W/k/m²
    triple_solar = Regeneration(power=solar * a0, temperature=temperature, a1=a1)

    ground_data = GroundFluxTemperature(2, 10)
    fluid_data = TemperatureDependentFluidData('MPG', 0, mass_percentage=False)
    flow_data = ConstantDeltaTFlowRate(delta_temp_extraction=3, delta_temp_injection=3)
    pipe_data = DoubleUTube(1, 0.013, 0.016, 0.4, 0.035)

    borefield = Borefield()
    borefield.create_rectangular_borefield(20, 20, 6, 6, 200, 4, 0.075)
    borefield.ground_data = ground_data
    borefield.fluid_data = fluid_data
    borefield.pipe_data = pipe_data
    borefield.flow_data = flow_data
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_fluid_temperature(17)
    borefield.set_min_fluid_temperature(3)
    hourly_load = HourlyBuildingLoad(efficiency_dhw=3.5)
    hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/swimming_pool.csv"), header=True,
                                    separator=";", col_cooling=0, col_heating=1, col_dhw=2)
    borefield.load = hourly_load
    borefield.load.simulation_period = 5
    triple_solar.surface = 200
    _, regen_8760 = calculate_regeneration(borefield, triple_solar, algorithm='proceeding',
                                           simulation_horizon=8760)
    _, regen_100 = calculate_regeneration(borefield, triple_solar, algorithm='proceeding',
                                          simulation_horizon=100)
    assert np.allclose(regen_8760, regen_100)


def test_office():
    borefield = Borefield()
    borefield.create_rectangular_borefield(8, 9, 6, 6, 100, 4, 0.075)
    fluid_data = TemperatureDependentFluidData('MPG', 0, mass_percentage=False)
    flow_data = ConstantDeltaTFlowRate(delta_temp_extraction=3, delta_temp_injection=3)
    pipe_data = DoubleUTube(1, 0.013, 0.016, 0.4, 0.035)
    ground_data = GroundFluxTemperature(2, 10)
    borefield.ground_data = ground_data
    borefield.fluid_data = fluid_data
    borefield.pipe_data = pipe_data
    borefield.flow_data = flow_data
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_fluid_temperature(25)
    borefield.set_min_fluid_temperature(0)
    hourly_load = HourlyBuildingLoad(efficiency_cooling=5)
    hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/office.csv"), header=True,
                                    separator=";", col_cooling=0, col_heating=1)
    borefield.load = hourly_load
    borefield.load.simulation_period = 5

    # get weather data
    weather_file = open(FOLDER.joinpath("Examples/BEL_Brussels.064510_IWEC.epw"), 'rb')
    weather_file.seek(0)
    TMY: pd.DataFrame = pd.read_csv(weather_file, sep=",", header=None, skiprows=8)

    TMY.drop(columns=TMY.columns[:5], inplace=True)
    solar: np.ndarray = np.tile(np.array(TMY.iloc[:, 8]), 20)
    temperature: np.ndarray = np.tile(np.array(TMY.iloc[:, 1]), 20)

    # initiate regeneration object
    a0 = 0.45
    a1 = 24.76  # W/K/m²

    surface = 200  # m²

    regeneration_object = Regeneration(power=solar * a0 * surface, temperature=temperature, a1=a1 * surface)
    load, regen = calculate_regeneration(borefield=borefield, regen_obj=regeneration_object)
    assert np.isclose(np.sum(regen[:8760]), -47923.77520000006)
    assert np.isclose(np.sum(regen[:8760]), (-1) * borefield.load.imbalance)
    load, regen = calculate_regeneration(borefield=borefield, regen_obj=regeneration_object,
                                         position_regeneration='outlet')
    # idem since there is more than enough regeneration capacity
    assert np.isclose(np.sum(regen[:8760]), -47923.77519999997)
    load, regen = calculate_regeneration(borefield=borefield, regen_obj=regeneration_object, algorithm='total')
    assert np.isclose(np.sum(regen[:8760]), -49775.377701580066)
