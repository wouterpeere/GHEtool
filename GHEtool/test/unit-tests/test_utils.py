import pytest
import numpy as np

from GHEtool import FOLDER
from GHEtool.utils import calculate_load
from GHEtool.VariableClasses import HourlyBuildingLoad, HourlyBuildingLoadMultiYear, MonthlyBuildingLoadAbsolute
from typing import Union


def test_load(data_, load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear],
              new_load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear]):
    sum_heating = data_['borefield heating'] + data_['excess heating'] + data_['top heating'] + data_['bottom heating']
    sum_cooling = data_['borefield cooling'] + data_['excess cooling'] + data_['top cooling'] + data_['bottom cooling']
    if isinstance(load, HourlyBuildingLoad):
        assert np.allclose(load.hourly_heating_load, sum_heating)
        assert np.allclose(load.hourly_cooling_load, sum_cooling)
        assert np.allclose(data_['borefield heating'], new_load.hourly_heating_load)
        assert np.allclose(data_['borefield cooling'], new_load.hourly_cooling_load)
        return
    assert np.allclose(load.hourly_heating_load_simulation_period, sum_heating)
    assert np.allclose(load.hourly_cooling_load_simulation_period, sum_cooling)
    assert np.allclose(data_['borefield heating'], new_load.hourly_heating_load_simulation_period)
    assert np.allclose(data_['borefield cooling'], new_load.hourly_cooling_load_simulation_period)


def test_value_error():
    hourly_load = HourlyBuildingLoad(np.full(8760, 100), np.full(8760, 100), efficiency_heating=8, dhw=100)
    multiyear_load = HourlyBuildingLoadMultiYear(np.full(8760 * 2, 100), np.full(8760 * 2, 100), efficiency_heating=8)
    monthly_load = MonthlyBuildingLoadAbsolute(np.linspace(0, 11, 12), np.linspace(0, 11, 12), np.linspace(0, 11, 12),
                                               np.linspace(0, 11, 12))
    with pytest.raises(ValueError):
        calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw_wrong.epw"), 'rb'), hourly_load)
    with pytest.raises(ValueError):
        calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                       max_peak_heating_top=10)
    with pytest.raises(ValueError):
        calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), monthly_load)
    with pytest.raises(ValueError):
        calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                       threshold_cooling_bottom=10)
    with pytest.raises(ValueError):
        calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                       threshold_cooling_bottom=10, max_peak_cooling_bottom=0, max_peak_cooling_top=0,
                       threshold_cooling_top=5)
    with pytest.raises(ValueError):
        calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                       threshold_heating_bottom=10, max_peak_heating_bottom=0, max_peak_heating_top=0,
                       threshold_heating_top=5)
    # without error
    data, _ = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load)
    assert hourly_load == data
    test_load(_, hourly_load, data)
    data, _ = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), multiyear_load)
    assert multiyear_load == data
    test_load(_, multiyear_load, data)


def test_calculate_load_yearly():
    hourly_load = HourlyBuildingLoad(np.full(8760, 100), np.full(8760, 100), efficiency_heating=8, dhw=100)

    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50)
    test_load(data, hourly_load, new_load)
    assert np.allclose(data['borefield heating'], hourly_load.hourly_heating_load / 2)
    assert np.allclose(data['borefield cooling'], hourly_load.hourly_cooling_load / 2)
    assert np.allclose(data['excess heating'], hourly_load.hourly_heating_load / 2)
    assert np.allclose(data['excess cooling'], hourly_load.hourly_cooling_load / 2)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50,
                                    max_peak_heating_top=50, threshold_heating_top=15)
    test_load(data, hourly_load, new_load)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50,
                                    max_peak_cooling_top=50, threshold_cooling_top=15)
    test_load(data, hourly_load, new_load)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50,
                                    max_peak_heating_bottom=50, threshold_heating_bottom=15)
    test_load(data, hourly_load, new_load)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50,
                                    max_peak_cooling_bottom=50, threshold_cooling_bottom=15)
    test_load(data, hourly_load, new_load)


def test_calculate_load_multiyearl():
    hourly_load = HourlyBuildingLoadMultiYear(np.full(8760 * 2, 100), np.full(8760 * 2, 100), efficiency_heating=8)

    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50)
    test_load(data, hourly_load, new_load)
    assert np.allclose(data['borefield heating'], hourly_load.hourly_heating_load_simulation_period / 2)
    assert np.allclose(data['borefield cooling'], hourly_load.hourly_cooling_load_simulation_period / 2)
    assert np.allclose(data['excess heating'], hourly_load.hourly_heating_load_simulation_period / 2)
    assert np.allclose(data['excess cooling'], hourly_load.hourly_cooling_load_simulation_period / 2)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50,
                                    max_peak_heating_top=50, threshold_heating_top=15)
    test_load(data, hourly_load, new_load)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50,
                                    max_peak_cooling_top=50, threshold_cooling_top=15)
    test_load(data, hourly_load, new_load)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50,
                                    max_peak_heating_bottom=50, threshold_heating_bottom=15)
    test_load(data, hourly_load, new_load)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50,
                                    max_peak_cooling_bottom=50, threshold_cooling_bottom=15)
    test_load(data, hourly_load, new_load)
