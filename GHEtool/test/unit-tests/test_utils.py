import pytest
import numpy as np

from GHEtool import FOLDER
from GHEtool.utils import calculate_load
from GHEtool.VariableClasses import HourlyBuildingLoad, HourlyBuildingLoadMultiYear, MonthlyBuildingLoadAbsolute
from typing import Union


def load_equals(data, load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear],
                new_load: Union[HourlyBuildingLoad, HourlyBuildingLoadMultiYear]):
    sum_heating = data['borefield heating'] + data['excess heating'] + data['top heating'] + data['bottom heating']
    sum_cooling = data['borefield cooling'] + data['excess cooling'] + data['top cooling'] + data['bottom cooling']
    if isinstance(load, HourlyBuildingLoad):
        assert np.allclose(load.hourly_heating_load, sum_heating)
        assert np.allclose(load.hourly_cooling_load, sum_cooling)
        assert np.allclose(data['borefield heating'], new_load.hourly_heating_load)
        assert np.allclose(data['borefield cooling'], new_load.hourly_cooling_load)
        return
    assert np.allclose(load.hourly_heating_load_simulation_period, sum_heating)
    assert np.allclose(load.hourly_cooling_load_simulation_period, sum_cooling)
    assert np.allclose(data['borefield heating'], new_load.hourly_heating_load_simulation_period)
    assert np.allclose(data['borefield cooling'], new_load.hourly_cooling_load_simulation_period)


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
    load_equals(_, hourly_load, data)
    data, _ = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), multiyear_load)
    assert multiyear_load == data
    load_equals(_, multiyear_load, data)


def test_calculate_load_yearly():
    hourly_load = HourlyBuildingLoad(np.arange(0, 8760, 1), np.arange(0, 8760, 1) * 2, efficiency_heating=8, dhw=100)
    hourly_load.start_month = 5
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load)
    load_equals(data, hourly_load, new_load)

    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50,
                                    max_peak_heating_top=50, threshold_heating_top=15)
    assert new_load.start_month == 5
    load_equals(data, hourly_load, new_load)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50,
                                    max_peak_cooling_top=50, threshold_cooling_top=15)
    load_equals(data, hourly_load, new_load)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50,
                                    max_peak_heating_bottom=50, threshold_heating_bottom=15)
    load_equals(data, hourly_load, new_load)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50,
                                    max_peak_cooling_bottom=50, threshold_cooling_bottom=15)
    load_equals(data, hourly_load, new_load)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load)
    load_equals(data, hourly_load, new_load)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=None, max_peak_heating_borefield=None,
                                    max_peak_heating_top=0, max_peak_cooling_top=0, max_peak_heating_bottom=0,
                                    max_peak_cooling_bottom=0, threshold_heating_top=15, threshold_heating_bottom=-2,
                                    threshold_cooling_top=22, threshold_cooling_bottom=12)
    assert new_load == hourly_load
    load_equals(data, hourly_load, new_load)


def test_calculate_load_multiyear():
    hourly_load = HourlyBuildingLoadMultiYear(np.arange(0, 8760 * 2 - 1, 1), np.arange(0, 8760 * 2 - 1, 1) * 2,
                                              efficiency_heating=8)

    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load)
    load_equals(data, hourly_load, new_load)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50,
                                    max_peak_heating_top=50, threshold_heating_top=15)
    load_equals(data, hourly_load, new_load)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50,
                                    max_peak_cooling_top=50, threshold_cooling_top=15)
    load_equals(data, hourly_load, new_load)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50,
                                    max_peak_heating_bottom=50, threshold_heating_bottom=15)
    load_equals(data, hourly_load, new_load)
    new_load, data = calculate_load(open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb'), hourly_load,
                                    max_peak_cooling_borefield=50, max_peak_heating_borefield=50,
                                    max_peak_cooling_bottom=50, threshold_cooling_bottom=15)
    load_equals(data, hourly_load, new_load)
