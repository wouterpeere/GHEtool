import pytest

import matplotlib.pyplot as plt
import numpy as np

from GHEtool import FOLDER
from GHEtool.VariableClasses import HourlyGeothermalLoad, HourlyGeothermalLoadMultiYear, MonthlyGeothermalLoadAbsolute
from GHEtool.Validation.cases import load_case


def test_load_hourly_data():
    load = HourlyGeothermalLoad()
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    load1 = HourlyGeothermalLoad()
    load1.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"), col_extraction=1, col_injection=0)
    assert np.array_equal(load.hourly_injection_load, load1.hourly_extraction_load)
    assert np.array_equal(load.hourly_extraction_load, load1.hourly_injection_load)
    load2 = HourlyGeothermalLoad()
    load2.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile_without_header.csv"),
                              header=False)
    assert np.array_equal(load.hourly_injection_load, load2.hourly_injection_load)
    assert np.array_equal(load.hourly_extraction_load, load2.hourly_extraction_load)


def test_checks():
    load = HourlyGeothermalLoad()
    assert not load._check_input(2)
    assert not load._check_input(np.ones(8759))
    assert not load._check_input(-1 * np.ones(8760))
    assert load._check_input([1] * 8760)
    assert load._check_input(np.ones(8760))


def test_imbalance():
    load = HourlyGeothermalLoad(np.ones(8760) * 10, np.ones(8760))
    assert load.imbalance == -78840
    load = HourlyGeothermalLoad(np.ones(8760), np.ones(8760) * 10)
    assert load.imbalance == 78840


def test_load_duration(monkeypatch):
    monkeypatch.setattr(plt, "show", lambda: None)
    load = HourlyGeothermalLoad(np.ones(8760) * 10, np.ones(8760))
    load.plot_load_duration(legend=True)


def test_resample_to_monthly():
    load = HourlyGeothermalLoad()
    peak, baseload = load.resample_to_monthly(np.tile(np.linspace(0, 729, 730), 12))
    assert np.array_equal(peak, np.ones(12) * 729)
    assert np.array_equal(baseload, np.ones(12) * 266085)
    load.all_months_equal = False
    peak, baseload = load.resample_to_monthly(np.tile(np.linspace(0, 729, 730), 12))
    assert np.array_equal(peak, np.array([729., 685., 729., 729., 729., 729., 729., 729., 729., 729., 729., 729.]))
    assert np.array_equal(baseload, np.array([266176., 234864., 275780., 259140., 275836., 259100.,
                                              275892., 276088., 258920., 276144., 258880., 276200.]))


def test_yearly_loads():
    load = HourlyGeothermalLoad(extraction_load=np.linspace(0, 8759, 8760),
                                injection_load=np.linspace(0, 8759, 8760) * 2,
                                simulation_period=10)
    assert np.array_equal(load.yearly_injection_load_simulation_period, [76728840] * 10)
    assert np.array_equal(load.yearly_extraction_load_simulation_period, [38364420] * 10)
    assert np.array_equal(load.yearly_injection_peak_simulation_period, [17518] * 10)
    assert np.array_equal(load.yearly_extraction_peak_simulation_period, [8759] * 10)


def test_baseload_heating():
    load = HourlyGeothermalLoad()
    assert np.array_equal(load.monthly_baseload_extraction, np.zeros(12))
    load.hourly_extraction_load = np.repeat(np.linspace(0, 11, 12), 730)
    assert np.array_equal(load.monthly_baseload_extraction, np.linspace(0, 11, 12) * 730)
    assert np.array_equal(load.monthly_baseload_extraction / 730, load.monthly_baseload_extraction_power)
    assert np.array_equal(load.monthly_baseload_extraction_power, load.monthly_peak_extraction)


def test_baseload_cooling():
    load = HourlyGeothermalLoad()
    assert np.array_equal(load.monthly_baseload_injection, np.zeros(12))
    load.hourly_injection_load = np.repeat(np.linspace(0, 11, 12), 730)
    assert np.array_equal(load.monthly_baseload_injection, np.linspace(0, 11, 12) * 730)
    assert np.array_equal(load.monthly_baseload_injection / 730, load.monthly_baseload_injection_power)
    assert np.array_equal(load.monthly_baseload_injection_power, load.monthly_peak_injection)


def test_peak_heating():
    load = HourlyGeothermalLoad()
    assert np.array_equal(load.monthly_peak_extraction, np.zeros(12))
    load.hourly_extraction_load = np.repeat(np.linspace(0, 11, 12), 730)
    assert np.array_equal(load.monthly_peak_extraction, np.linspace(0, 11, 12))
    load.hourly_extraction_load = np.repeat(np.linspace(1, 12, 12), 730)
    assert np.array_equal(load.monthly_peak_extraction, np.linspace(1, 12, 12))


def test_peak_cooling():
    load = HourlyGeothermalLoad()
    assert np.array_equal(load.monthly_peak_injection, np.zeros(12))
    load.hourly_injection_load = np.repeat(np.linspace(0, 11, 12), 730)
    assert np.array_equal(load.monthly_peak_injection, np.linspace(0, 11, 12))
    load.hourly_injection_load = np.repeat(np.linspace(1, 12, 12), 730)
    assert np.array_equal(load.monthly_peak_injection, np.linspace(1, 12, 12))


def test_load_simulation_period():
    load = HourlyGeothermalLoad()
    load.hourly_extraction_load = np.linspace(0, 8759, 8760)
    assert np.array_equal(load.hourly_extraction_load_simulation_period,
                          np.tile(np.linspace(0, 8759, 8760), load.simulation_period))
    load.hourly_injection_load = np.linspace(50, 8759, 8760)
    assert np.array_equal(load.hourly_injection_load_simulation_period,
                          np.tile(np.linspace(50, 8759, 8760), load.simulation_period))
    assert np.array_equal(load.hourly_net_resulting_power,
                          np.tile(-np.linspace(0, 8759, 8760) + np.linspace(50, 8759, 8760), load.simulation_period))


def test_set_hourly_values():
    load = HourlyGeothermalLoad()
    with pytest.raises(ValueError):
        load.set_hourly_extraction_load(np.ones(10))
    with pytest.raises(ValueError):
        load.set_hourly_injection_load(np.ones(10))


def test_start_month_general():
    load = HourlyGeothermalLoad()
    assert load.start_month == 1
    with pytest.raises(ValueError):
        load.start_month = 1.5
    with pytest.raises(ValueError):
        load.start_month = 0
    with pytest.raises(ValueError):
        load.start_month = 13
    load.start_month = 12
    assert load.start_month == 12
    assert load._start_hour == 11 * 730
    load.start_month = 1
    assert load.start_month == 1
    assert load._start_hour == 0
    load.start_month = 3
    assert load.start_month == 3
    assert load._start_hour == 730 * 2

    load.all_months_equal = False
    assert load._start_hour == 1416


def test_different_start_month():
    load = HourlyGeothermalLoad(np.arange(1, 8761, 1), np.arange(1, 8761, 1))
    load.start_month = 3
    assert load.start_month == 3
    assert load.hourly_injection_load[0] == 731 * 2 - 1
    assert load.hourly_extraction_load[0] == 731 * 2 - 1
    assert load.hourly_injection_load_simulation_period[0] == 731 * 2 - 1
    assert load.hourly_extraction_load_simulation_period[0] == 731 * 2 - 1
    load.all_months_equal = False
    assert load.hourly_injection_load[0] == 1417
    assert load.hourly_extraction_load[0] == 1417
    assert load.hourly_injection_load_simulation_period[0] == 1417
    assert load.hourly_extraction_load_simulation_period[0] == 1417


def test_eq():
    profile_1 = HourlyGeothermalLoad()
    profile_2 = MonthlyGeothermalLoadAbsolute()
    assert not profile_1 == profile_2
    assert profile_1 == profile_1

    profile_2 = HourlyGeothermalLoad()
    assert profile_1 == profile_2

    profile_1.simulation_period = 55
    assert profile_1 != profile_2

    profile_1.hourly_injection_load = np.linspace(0, 10000, 8760)
    profile_2.simulation_period = 55
    assert profile_1 != profile_2

    profile_2.hourly_injection_load = np.linspace(0, 10000, 8760)
    assert profile_1 == profile_2

    profile_1.hourly_extraction_load = np.linspace(0, 8759, 8760)
    assert profile_1 != profile_2

    profile_2.hourly_extraction_load = np.linspace(0, 8759, 8760)
    assert profile_1 == profile_2


def test_add():
    load_1 = HourlyGeothermalLoad(extraction_load=np.arange(0, 8760, 1),
                                  injection_load=np.full(8760, 2),
                                  simulation_period=20)
    load_2 = HourlyGeothermalLoad(injection_load=np.arange(0, 8760, 1) + 1,
                                  extraction_load=np.full(8760, 3),
                                  simulation_period=30)

    with pytest.raises(TypeError):
        load_1 + 55

    with pytest.warns():
        result = load_1 + load_2

    assert result.simulation_period == 30
    assert np.allclose(result.hourly_injection_load, load_1.hourly_injection_load + load_2.hourly_injection_load)
    assert np.allclose(result.hourly_extraction_load, load_1.hourly_extraction_load + load_2.hourly_extraction_load)

    load_2.simulation_period = 20
    try:
        with pytest.warns():
            result = load_1 + load_2
        assert False  # pragma: no cover
    except:
        assert True
    assert result.simulation_period == 20
    assert np.allclose(result.hourly_injection_load, load_1.hourly_injection_load + load_2.hourly_injection_load)
    assert np.allclose(result.hourly_extraction_load, load_1.hourly_extraction_load + load_2.hourly_extraction_load)

    # add with monthly load
    load_1 = MonthlyGeothermalLoadAbsolute(*load_case(2))
    load_hourly = HourlyGeothermalLoad(np.full(8760, 10), np.full(8760, 20), 30)

    with pytest.warns():
        result = load_1 + load_hourly  # simulation period not equal

    assert result.simulation_period == 30
    assert np.allclose(result._baseload_extraction,
                       load_1._baseload_extraction +
                       load_hourly.resample_to_monthly(load_hourly._hourly_extraction_load)[
                           1])
    assert np.allclose(result._baseload_injection,
                       load_1._baseload_injection +
                       load_hourly.resample_to_monthly(load_hourly._hourly_injection_load)[
                           1])
    assert np.allclose(result._peak_extraction,
                       load_1._peak_extraction + load_hourly.resample_to_monthly(load_hourly._hourly_extraction_load)[
                           0])
    assert np.allclose(result._peak_injection,
                       load_1._peak_injection + load_hourly.resample_to_monthly(load_hourly._hourly_injection_load)[0])

    # test multiyear
    load_1 = HourlyGeothermalLoadMultiYear(extraction_load=np.arange(0, 8760 * 2, 1),
                                           injection_load=np.full(8760 * 2, 2))
    load_2 = HourlyGeothermalLoad(np.arange(0, 8760, 1),
                                  np.arange(0, 8760, 1) + 1)

    with pytest.warns():
        result = load_1 + load_2

    assert np.allclose(result._hourly_extraction_load,
                       load_1._hourly_extraction_load + np.tile(load_2.hourly_extraction_load,
                                                                load_1.simulation_period))
    assert np.allclose(result._hourly_injection_load,
                       load_1._hourly_injection_load + np.tile(load_2.hourly_injection_load, load_1.simulation_period))
    assert np.allclose(result.hourly_extraction_load, load_1.hourly_extraction_load + load_2.hourly_extraction_load)
    assert np.allclose(result.hourly_injection_load, load_1.hourly_injection_load + load_2.hourly_injection_load)

    assert np.allclose(result._hourly_extraction_load,
                       load_1._hourly_extraction_load + np.tile(load_2._hourly_extraction_load,
                                                                load_1.simulation_period))
    assert np.allclose(result._hourly_injection_load,
                       load_1._hourly_injection_load + np.tile(load_2._hourly_injection_load, load_1.simulation_period))


def test_depreciation_warning():
    with pytest.raises(DeprecationWarning):
        HourlyGeothermalLoad(hourly_heating=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
