import pytest

import numpy as np

from GHEtool.VariableClasses import MonthlyGeothermalLoadAbsolute, HourlyGeothermalLoad, MonthlyGeothermalLoadMultiYear
from GHEtool.Validation.cases import load_case


def test_checks():
    load = MonthlyGeothermalLoadAbsolute()
    assert not load._check_input(2)
    assert not load._check_input(np.ones(11))
    assert not load._check_input(-1 * np.ones(12))
    assert load._check_input([1] * 12)
    assert load._check_input(np.ones(12))


def test_start_month_general():
    load = MonthlyGeothermalLoadAbsolute()
    assert load.start_month == 1
    with pytest.raises(ValueError):
        load.start_month = 1.5
    with pytest.raises(ValueError):
        load.start_month = 0
    with pytest.raises(ValueError):
        load.start_month = 13
    load.start_month = 12
    assert load.start_month == 12
    load.start_month = 1
    assert load.start_month == 1


def test_imbalance():
    load = MonthlyGeothermalLoadAbsolute(np.ones(12) * 10, np.ones(12), np.ones(12), np.ones(12))
    assert load.imbalance == -108
    load = MonthlyGeothermalLoadAbsolute(np.ones(12), np.ones(12) * 10, np.ones(12), np.ones(12))
    assert load.imbalance == 108


def test_baseload_extraction():
    load = MonthlyGeothermalLoadAbsolute()
    assert np.allclose(load.baseload_extraction, np.zeros(12))
    load.baseload_extraction = np.linspace(0, 11, 12)
    assert np.allclose(load.baseload_extraction, np.linspace(0, 11, 12))
    load.set_baseload_extraction(np.linspace(1, 12, 12))
    assert np.allclose(load.baseload_extraction, np.linspace(1, 12, 12))
    assert np.allclose(load.baseload_extraction / 730, load.monthly_baseload_extraction_power)
    assert np.allclose(load.monthly_baseload_extraction_power, load.peak_extraction)
    with pytest.raises(ValueError):
        load.set_baseload_extraction(np.ones(11))


def test_baseload_injection():
    load = MonthlyGeothermalLoadAbsolute()
    assert np.allclose(load.baseload_injection, np.zeros(12))
    load.baseload_injection = np.linspace(0, 11, 12)
    assert np.allclose(load.baseload_injection, np.linspace(0, 11, 12))
    load.set_baseload_injection(np.linspace(1, 12, 12))
    assert np.allclose(load.baseload_injection, np.linspace(1, 12, 12))
    assert np.allclose(load.baseload_injection / 730, load.monthly_baseload_injection_power)
    assert np.allclose(load.monthly_baseload_injection_power, load.peak_injection)

    with pytest.raises(ValueError):
        load.set_baseload_injection(np.ones(11))


def test_peak_extraction():
    load = MonthlyGeothermalLoadAbsolute()
    assert np.allclose(load.peak_extraction, np.zeros(12))
    load.peak_extraction = np.linspace(0, 11, 12)
    assert np.allclose(load.peak_extraction, np.linspace(0, 11, 12))
    load.set_peak_extraction(np.linspace(1, 12, 12))
    assert np.allclose(load.peak_extraction, np.linspace(1, 12, 12))
    load.set_baseload_extraction(np.ones(12) * 730 * 5)
    assert np.allclose(load.peak_extraction, np.array([5., 5., 5., 5., 5., 6., 7., 8., 9., 10., 11., 12.]))
    with pytest.raises(ValueError):
        load.set_peak_extraction(np.ones(11))


def test_peak_injection():
    load = MonthlyGeothermalLoadAbsolute()
    assert np.allclose(load.peak_injection, np.zeros(12))
    load.peak_injection = np.linspace(0, 11, 12)
    assert np.allclose(load.peak_injection, np.linspace(0, 11, 12))
    load.set_peak_injection(np.linspace(1, 12, 12))
    assert np.allclose(load.peak_injection, np.linspace(1, 12, 12))
    load.set_baseload_injection(np.ones(12) * 730 * 5)
    assert np.allclose(load.peak_injection, np.array([5., 5., 5., 5., 5., 6., 7., 8., 9., 10., 11., 12.]))
    with pytest.raises(ValueError):
        load.set_peak_injection(np.ones(11))


def test_times():
    load = MonthlyGeothermalLoadAbsolute()
    load.peak_injection_duration = 6
    load.peak_extraction_duration = 7
    assert load.peak_extraction_duration == 7 * 3600
    assert load.peak_injection_duration == 6 * 3600
    load.peak_duration = 8
    assert load.peak_extraction_duration == 8 * 3600
    assert load.peak_injection_duration == 8 * 3600

    load.simulation_period = 20
    assert load.time_L3[-1] == 20 * 3600 * 8760
    assert load.time_L4[-1] == 20 * 3600 * 8760

    load.simulation_period = 100
    assert not np.isinf(load.time_L4.any())
    assert load.ty == 100 * 8760 * 3600

    with pytest.raises(ValueError):
        load.simulation_period = 0


def test_monthly_average_load():
    load = MonthlyGeothermalLoadAbsolute()
    load.baseload_injection = np.ones(12) * 400
    load.baseload_extraction = np.ones(12) * 500

    assert np.isclose(np.average(load.monthly_baseload_injection_power) * 8760, 400 * 12)
    assert np.isclose(np.average(load.monthly_baseload_extraction_power) * 8760, 500 * 12)
    assert np.allclose(load.monthly_baseload_injection_power, load.peak_injection)
    assert np.allclose(load.monthly_baseload_extraction_power, load.peak_extraction)

    assert np.allclose(load.monthly_baseload_injection_simulation_period,
                       np.tile(load.monthly_baseload_injection, 20))
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       np.tile(load.monthly_baseload_extraction, 20))
    assert np.allclose(load.monthly_peak_extraction_simulation_period,
                       np.tile(load.peak_extraction, 20))
    assert np.allclose(load.monthly_peak_injection_simulation_period,
                       np.tile(load.peak_injection, 20))
    assert np.allclose(load.monthly_baseload_injection_simulation_period,
                       np.tile(load.baseload_injection, 20))
    assert np.allclose(load.monthly_baseload_extraction_simulation_period,
                       np.tile(load.baseload_extraction, 20))

    assert np.allclose(load.monthly_average_injection_power,
                       load.monthly_baseload_injection_power - load.monthly_baseload_extraction_power)
    assert np.allclose(load.monthly_average_injection_power_simulation_period,
                       load.monthly_baseload_injection_power_simulation_period - load.monthly_baseload_extraction_power_simulation_period)

    # test now with different month loads
    temp_cooling = load.monthly_baseload_injection
    temp_heating = load.monthly_baseload_extraction

    load.all_months_equal = False
    assert not np.allclose(load.monthly_baseload_injection_power, temp_cooling)
    assert not np.allclose(load.monthly_baseload_extraction_power, temp_heating)

    assert np.isclose(np.sum(np.multiply(load.monthly_baseload_injection_power, load.UPM)), 400 * 12)
    assert np.isclose(np.sum(np.multiply(load.monthly_baseload_extraction_power, load.UPM)), 500 * 12)


def test_params_last_year():
    load = MonthlyGeothermalLoadAbsolute(*load_case(2))
    assert np.allclose(load._calculate_last_year_params(False),
                       (21600.0, 240000.0, 65753.42465753425, 9132.420091324202))
    assert np.allclose(load._calculate_last_year_params(True),
                       (21600.0, 160000.0, 25753.424657534248, -9132.420091324202))
    load.peak_extraction = np.ones(12) * 160
    load.peak_injection = np.ones(12) * 240
    assert np.allclose(load._calculate_last_year_params(False),
                       (21600.0, 240000.0, 65753.42465753425, 9132.420091324202))
    assert np.allclose(load._calculate_last_year_params(True),
                       (21600.0, 160000.0, 25753.424657534248, -9132.420091324202))


def test_params_first_year():
    load = MonthlyGeothermalLoadAbsolute(*load_case(2))
    assert np.allclose(load._calculate_first_year_params(False),
                       (21600.0, 18396000.0, 21024000.0, 240000.0, 6410.9589041095915, 65753.42465753425))
    assert np.allclose(load._calculate_first_year_params(True),
                       (21600.0, 0, 2628000.0, 160000.0, 0, 25753.424657534248))
    temp = load.peak_injection
    temp[0] = 250
    load.peak_injection = temp
    assert np.allclose(load._calculate_first_year_params(False),
                       (21600, 0, 2628000, 250000.0, 0, -25753.424657534248))

    load.peak_extraction = np.ones(12) * 160
    load.peak_injection = np.ones(12) * 240

    assert np.allclose(load._calculate_first_year_params(False),
                       (21600, 18396000.0, 21024000.0, 240000.0, 6410.9589041095915, 65753.42465753425))
    assert np.allclose(load._calculate_first_year_params(True),
                       (21600.0, 0, 2628000.0, 160000.0, 0, 25753.424657534248))


def test_get_month_index():
    load = MonthlyGeothermalLoadAbsolute()
    test_equal = np.array([2] * 12)
    test_unequal = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 10])
    test_unequal_2 = np.array([2] * 12)
    test_unequal_2[3] = 30
    test_unequal_2[4] = 30

    assert load.get_month_index(test_equal, test_equal) == 11
    assert load.get_month_index(test_unequal, test_equal) == 10
    assert load.get_month_index(test_unequal, test_unequal) == 10
    assert load.get_month_index(test_equal, test_unequal) == 10
    assert load.get_month_index(test_equal, test_unequal_2) == 4


def test_dummy_peak_duration():
    test = MonthlyGeothermalLoadAbsolute()
    assert None is test.peak_duration


def test_yearly_heating_cooling():
    load = MonthlyGeothermalLoadAbsolute(*load_case(2))
    assert load.yearly_average_extraction_load == 160000
    assert load.yearly_average_injection_load == 240000


def test_eq():
    load_1 = MonthlyGeothermalLoadAbsolute(*load_case(2))
    load_2 = MonthlyGeothermalLoadAbsolute(*load_case(2))

    assert load_1 == load_2
    load_2.simulation_period = 55
    assert load_1 != load_2

    load_1.simulation_period = 55
    assert load_1 == load_2
    load_1.baseload_injection = [i + 1 for i in load_1.baseload_injection]

    assert load_1 != load_2
    load_2.baseload_injection = [i + 1 for i in load_2.baseload_injection]
    assert load_1 == load_2

    load_1.simulation_period = 55
    assert load_1 == load_2
    load_1.baseload_extraction = [i + 1 for i in load_1.baseload_extraction]

    assert load_1 != load_2
    load_2.baseload_extraction = [i + 1 for i in load_2.baseload_extraction]
    assert load_1 == load_2

    load_1.simulation_period = 55
    assert load_1 == load_2
    load_1.peak_extraction = [i + 1 for i in load_1.peak_extraction]

    assert load_1 != load_2
    load_2.peak_extraction = [i + 1 for i in load_2.peak_extraction]
    assert load_1 == load_2

    load_1.simulation_period = 55
    assert load_1 == load_2
    load_1.peak_injection = [i + 1 for i in load_1.peak_injection]

    assert load_1 != load_2
    load_2.peak_injection = [i + 1 for i in load_2.peak_injection]
    assert load_1 == load_2

    load_2 = HourlyGeothermalLoad()
    assert load_1 != load_2


def test_add():
    load_1 = MonthlyGeothermalLoadAbsolute(*load_case(2))
    load_2 = MonthlyGeothermalLoadAbsolute(*load_case(1))
    load_1.dhw = 10000
    load_2.dhw = 50000
    load_1.simulation_period = 20
    load_2.simulation_period = 30

    with pytest.raises(TypeError):
        load_1 + 55

    with pytest.warns():
        result = load_1 + load_2

    assert result.simulation_period == 30
    assert np.allclose(result.baseload_extraction, load_1.baseload_extraction + load_2.baseload_extraction)
    assert np.allclose(result.baseload_injection, load_1.baseload_injection + load_2.baseload_injection)
    assert np.allclose(result._peak_extraction, load_1._peak_extraction + load_2._peak_extraction)
    assert np.allclose(result._peak_injection, load_1._peak_injection + load_2._peak_injection)

    load_2.simulation_period = 20
    load_2.peak_extraction_duration = 18

    with pytest.warns():
        result = load_1 + load_2
        assert result.peak_extraction_duration == 18 * 3600
    load_1.peak_extraction_duration = 18
    try:
        with pytest.warns():
            result = load_1 + load_2
        assert False  # pragma: no cover
    except:
        assert True

    load_1.peak_injection_duration = 18
    with pytest.warns():
        result = load_1 + load_2
        assert result.peak_injection_duration == 18 * 3600
    load_2.peak_injection_duration = 18
    try:
        with pytest.warns():
            result = load_1 + load_2
        assert False  # pragma: no cover
    except:
        assert True

    # add hourly load
    load_hourly = HourlyGeothermalLoad(np.full(8760, 10), np.full(8760, 20), 30)

    with pytest.warns():
        result = load_1 + load_hourly  # simulation period not equal

    assert result.simulation_period == 30
    assert np.allclose(result._baseload_extraction,
                       load_1._baseload_extraction +
                       load_hourly.resample_to_monthly(load_hourly._hourly_extraction_load)[
                           1])
    assert np.allclose(result._baseload_injection,
                       load_1._baseload_injection + load_hourly.resample_to_monthly(load_hourly._hourly_injection_load)[
                           1])
    assert np.allclose(result._peak_extraction,
                       load_1._peak_extraction + load_hourly.resample_to_monthly(load_hourly._hourly_extraction_load)[
                           0])
    assert np.allclose(result._peak_injection,
                       load_1._peak_injection + load_hourly.resample_to_monthly(load_hourly._hourly_injection_load)[0])

    load_hourly.simulation_period = 20
    with pytest.warns():
        result = load_1 + load_hourly


def test_different_start_month():
    load = MonthlyGeothermalLoadAbsolute(baseload_extraction=np.arange(1, 13, 1),
                                         baseload_injection=np.arange(1, 13, 1),
                                         peak_injection=np.arange(1, 13, 1),
                                         peak_extraction=np.arange(1, 13, 1))
    load.start_month = 2
    result = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1])
    assert np.allclose(load.baseload_extraction, result)
    assert np.allclose(load.baseload_injection, result)
    assert np.allclose(load.peak_extraction, result)
    assert np.allclose(load.peak_injection, result)
    assert np.allclose(load.monthly_baseload_extraction_simulation_period, np.tile(result, 20))
    assert np.allclose(load.monthly_baseload_injection_simulation_period, np.tile(result, 20))
    assert np.allclose(load.monthly_peak_extraction_simulation_period, np.tile(result, 20))
    assert np.allclose(load.monthly_peak_injection_simulation_period, np.tile(result, 20))

    load.peak_injection = np.zeros(12)
    load.peak_extraction = np.zeros(12)
    assert np.allclose(load.monthly_peak_extraction_simulation_period, np.tile(result, 20) / 730)
    assert np.allclose(load.monthly_peak_injection_simulation_period, np.tile(result, 20) / 730)


def test_yearly_loads():
    load = MonthlyGeothermalLoadAbsolute(*load_case(2))
    load.simulation_period = 10
    assert np.allclose(load.yearly_injection_load_simulation_period, [240000] * 10)
    assert np.allclose(load.yearly_extraction_load_simulation_period, [160000] * 10)
    assert np.allclose(load.yearly_injection_peak_simulation_period, [240] * 10)
    assert np.allclose(load.yearly_extraction_peak_simulation_period, [160] * 10)


def test_depreciation_warning():
    with pytest.raises(DeprecationWarning):
        MonthlyGeothermalLoadAbsolute(baseload_heating=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])


def test_eq():
    load = MonthlyGeothermalLoadAbsolute(*load_case(2))
    load2 = MonthlyGeothermalLoadAbsolute(*load_case(1))
    load3 = MonthlyGeothermalLoadMultiYear(*load_case(2))
    load4 = MonthlyGeothermalLoadAbsolute(*load_case(1))

    assert load != load3
    assert load != load2
    assert load2 != load3
    assert load2 == load4
