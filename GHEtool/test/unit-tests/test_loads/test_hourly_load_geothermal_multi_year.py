import pytest

import numpy as np

from GHEtool.VariableClasses import HourlyGeothermalLoad, HourlyGeothermalLoadMultiYear, MonthlyGeothermalLoadAbsolute
from GHEtool.Validation.cases import load_case


def test_checks_multiyear():
    load = HourlyGeothermalLoadMultiYear()
    assert not load._check_input(2)
    assert not load._check_input(np.ones(8759))
    assert not load._check_input(-1 * np.ones(8760))
    assert load._check_input([1] * 8760)
    assert load._check_input(np.ones(8760))
    assert load._check_input(np.ones(8760 * 3))
    assert not load._check_input(np.ones(9000))


def test_set_hourly_load_multi_year():
    load = HourlyGeothermalLoadMultiYear()
    load.hourly_extraction_load = np.linspace(0, 8759 * 2 + 1, 8760 * 2)
    load.hourly_injection_load = np.linspace(0, 8759 * 2 + 1, 8760 * 2)
    assert len(load._hourly_extraction_load) == 8760 * 2
    assert len(load.hourly_extraction_load) == 8760
    assert load.max_peak_extraction, 8759 * 2 + 1
    assert load.max_peak_injection, 8759 * 2 + 1
    assert load.simulation_period == 2
    assert np.array_equal(load.hourly_extraction_load, np.linspace(0 + 8760 / 2, 8759 + 8760 / 2, 8760))
    assert np.array_equal(load.hourly_extraction_load_simulation_period, load._hourly_extraction_load)
    assert len(load._hourly_injection_load) == 8760 * 2
    assert len(load.hourly_injection_load) == 8760
    assert load.simulation_period == 2
    assert np.array_equal(load.hourly_injection_load, np.linspace(0 + 8760 / 2, 8759 + 8760 / 2, 8760))
    assert np.array_equal(load.hourly_injection_load_simulation_period, load._hourly_injection_load)
    load._hourly_injection_load = load._hourly_injection_load - 20
    assert np.array_equal(load.hourly_net_resulting_injection_power,
                          load._hourly_injection_load - load._hourly_extraction_load)


def test_imbalance_multi_year():
    load = HourlyGeothermalLoad(np.ones(8760) * 10, np.ones(8760))
    assert load.imbalance == -78840
    load = HourlyGeothermalLoad(np.ones(8760), np.ones(8760) * 10)
    assert load.imbalance == 78840


def test_set_hourly_values_multi_year():
    load = HourlyGeothermalLoadMultiYear()
    with pytest.raises(ValueError):
        load.set_hourly_extraction_load(np.ones(10))
    with pytest.raises(ValueError):
        load.set_hourly_injection_load(np.ones(10))


def test_monthly_based_on_hourly_multi_year():
    load = HourlyGeothermalLoadMultiYear(extraction_load=np.arange(0, 8760 * 2, 1),
                                         injection_load=np.arange(0, 8760 * 2, 1) * 2)
    heating = np.array([729, 1459, 2189, 2919, 3649, 4379, 5109, 5839, 6569, 7299, 8029, 8759, 9489,
                        10219, 10949, 11679, 12409, 13139, 13869, 14599, 15329, 16059, 16789, 17519])
    heating_bl = np.array([np.sum(np.arange(0, 8760 * 2, 1)[i - 730:i]) for i in range(730, 8760 * 2 + 1, 730)])
    assert np.allclose(load.monthly_peak_extraction_simulation_period, heating)
    assert np.allclose(load.monthly_peak_injection_simulation_period, heating * 2)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period, heating_bl)
    assert np.allclose(load.monthly_baseload_injection_simulation_period, heating_bl * 2)
    assert np.allclose(load.monthly_baseload_extraction_power_simulation_period, heating_bl / 730)
    assert np.allclose(load.monthly_baseload_injection_power_simulation_period, heating_bl * 2 / 730)
    assert np.allclose(load.monthly_average_injection_power_simulation_period, heating_bl / 730)


def test_resample_to_monthly_multiyear():
    load = HourlyGeothermalLoadMultiYear()
    peak, baseload = load.resample_to_monthly(np.tile(np.linspace(0, 729, 730), 24))
    assert np.array_equal(peak, np.full(24, 729))
    assert np.array_equal(baseload, np.full(24, 266085))
    load.all_months_equal = False
    peak, baseload = load.resample_to_monthly(np.tile(np.linspace(0, 729, 730), 24))
    assert np.array_equal(peak,
                          np.tile(np.array([729., 685., 729., 729., 729., 729., 729., 729., 729., 729., 729., 729.]),
                                  2))
    assert np.array_equal(baseload, np.tile(np.array([266176., 234864., 275780., 259140., 275836., 259100.,
                                                      275892., 276088., 258920., 276144., 258880., 276200.]), 2))


def test_eq_multiyear():
    profile_1 = HourlyGeothermalLoadMultiYear()
    profile_2 = MonthlyGeothermalLoadAbsolute()
    assert not profile_1 == profile_2
    assert profile_1 == profile_1

    profile_2 = HourlyGeothermalLoadMultiYear()
    assert profile_1 == profile_2

    profile_1.hourly_injection_load = np.linspace(0, 10000, 8760 * 55)
    profile_2.hourly_injection_load = np.linspace(0, 10000, 8760 * 54)
    assert profile_1 != profile_2
    assert profile_2 != profile_1

    profile_2.hourly_injection_load = np.linspace(0, 10001, 8760 * 55)
    assert profile_1 != profile_2
    assert profile_2 != profile_1

    profile_2.hourly_injection_load = np.linspace(0, 10000, 8760 * 55)
    assert profile_1 == profile_2

    profile_1.hourly_extraction_load = np.linspace(0, 8759, 8760 * 55)
    assert profile_1 != profile_2

    profile_2.hourly_extraction_load = np.linspace(0, 8759, 8760 * 55)
    assert profile_1 == profile_2


def test_add_multiyear():
    load_1 = HourlyGeothermalLoadMultiYear(extraction_load=np.arange(0, 8760, 1),
                                           injection_load=np.full(8760, 2))
    load_2 = HourlyGeothermalLoadMultiYear(injection_load=np.arange(0, 8760 * 2, 1) + 1,
                                           extraction_load=np.full(8760 * 2, 3))

    with pytest.raises(TypeError):
        load_1 + 55

    with pytest.raises(ValueError):
        load_1 + load_2

    load_1 = HourlyGeothermalLoadMultiYear(extraction_load=np.arange(0, 8760 * 2, 1),
                                           injection_load=np.full(8760 * 2, 2))

    result = load_1 + load_2

    assert np.allclose(result._hourly_extraction_load, load_1._hourly_extraction_load + load_2._hourly_extraction_load)
    assert np.allclose(result._hourly_injection_load, load_1._hourly_injection_load + load_2._hourly_injection_load)
    assert np.allclose(result.hourly_extraction_load, load_1.hourly_extraction_load + load_2.hourly_extraction_load)
    assert np.allclose(result.hourly_injection_load, load_1.hourly_injection_load + load_2.hourly_injection_load)

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

    # monthly load
    load_2 = MonthlyGeothermalLoadAbsolute(*load_case(1))

    with pytest.raises(TypeError):
        load_1 + load_2


def test_yearly_loads_multiyear():
    load = HourlyGeothermalLoadMultiYear(extraction_load=np.linspace(0, 8759 * 2 + 1, 8760 * 2),
                                         injection_load=np.linspace(0, 8759 * 2 + 1, 8760 * 2) * 2)
    assert np.array_equal(load.yearly_injection_load_simulation_period, [76728840, 115102020 * 2])
    assert np.array_equal(load.yearly_extraction_load_simulation_period, [38364420, 115102020])
    assert np.array_equal(load.yearly_injection_peak_simulation_period, [17518, 35038])
    assert np.array_equal(load.yearly_extraction_peak_simulation_period, [8759, 17519])


def test_depreciation_warning():
    with pytest.raises(DeprecationWarning):
        HourlyGeothermalLoadMultiYear(hourly_heating=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])


def test_repr_():
    load = HourlyGeothermalLoadMultiYear(extraction_load=np.linspace(0, 8759 * 2 + 1, 8760 * 2),
                                         injection_load=np.linspace(0, 8759 * 2 + 1, 8760 * 2) * 2)

    assert 'Multiyear hourly geothermal load\n' \
           'Peak injection duration [hour]: 6.0\n' \
           'Peak extraction duration [hour]: 6.0' == load.__repr__()
