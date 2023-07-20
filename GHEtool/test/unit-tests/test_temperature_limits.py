import numpy as np
from GHEtool.VariableClasses import ConstantTemperatureLimit, MonthlyTemperatureLimit, HourlyTemperatureLimit


# tests for constant temperature limit
def test_constant_init():
    constant = ConstantTemperatureLimit(2, 5)
    assert constant.constant_limits
    assert constant._max_temperature == 5
    assert constant._min_temperature == 2


def test_constant_set_limits():
    constant = ConstantTemperatureLimit()
    constant.set_min_temperature(3)
    constant.set_max_temperature(15)
    assert constant._max_temperature == 15
    assert constant._min_temperature == 3


def test_constant_check():
    constant = ConstantTemperatureLimit()
    assert constant.check_input(2)
    assert constant.check_input(2.5)
    assert not constant.check_input([3, 4])
    assert not constant.check_input(np.array([3, 4]))
    try:
        constant.set_min_temperature([3])
        assert False  # pragma: no cover
    except ValueError:
        assert True
    try:
        constant.set_max_temperature([3])
        assert False  # pragma: no cover
    except ValueError:
        assert True
    try:
        constant.set_min_temperature(20)
        assert False  # pragma: no cover
    except ValueError:
        assert True
    try:
        constant.set_max_temperature(-2)
        assert False  # pragma: no cover
    except ValueError:
        assert True


def test_constant_monthly_limits():
    constant = ConstantTemperatureLimit(2, 15)
    assert np.allclose(constant.get_min_temperature_monthly(2), np.full(2 * 12, 2))
    assert np.allclose(constant.get_max_temperature_monthly(2), np.full(2 * 12, 15))


def test_constant_hourly_limits():
    constant = ConstantTemperatureLimit(2, 15)
    assert np.allclose(constant.get_min_temperature_hourly(2), np.full(2 * 8760, 2))
    assert np.allclose(constant.get_max_temperature_hourly(2), np.full(2 * 8760, 15))


# test monthly limits
def test_monthly_init():
    monthly = MonthlyTemperatureLimit(np.linspace(-12, -1, 12), np.linspace(0, 11, 12))
    assert not monthly.constant_limits
    assert np.allclose(monthly._max_temperature, np.linspace(0, 11, 12))
    assert np.allclose(monthly._min_temperature, np.linspace(-12, -1, 12))


def test_monthly_set_limits():
    monthly = MonthlyTemperatureLimit(np.zeros(12), np.ones(12))
    monthly.set_min_temperature(np.linspace(-12, -1, 12))
    monthly.set_max_temperature(np.linspace(0, 11, 12))
    assert np.allclose(monthly._max_temperature, np.linspace(0, 11, 12))
    assert np.allclose(monthly._min_temperature, np.linspace(-12, -1, 12))
    monthly.set_max_temperature([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    monthly.set_min_temperature([-12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1])
    assert np.allclose(monthly._max_temperature, np.linspace(0, 11, 12))
    assert np.allclose(monthly._min_temperature, np.linspace(-12, -1, 12))


def test_monthly_check():
    monthly = MonthlyTemperatureLimit(np.zeros(12), np.ones(12))
    assert not monthly.check_input(2)
    assert not monthly.check_input(2.5)
    assert not monthly.check_input([3, 4])
    assert not monthly.check_input(np.array([3, 4]))
    assert monthly.check_input(np.ones(12))
    assert monthly.check_input([1]*12)
    try:
        monthly.set_min_temperature([3])
        assert False  # pragma: no cover
    except ValueError:
        assert True
    try:
        monthly.set_max_temperature([3])
        assert False  # pragma: no cover
    except ValueError:
        assert True
    try:
        monthly.set_min_temperature(3)
        assert False  # pragma: no cover
    except ValueError:
        assert True
    try:
        monthly.set_max_temperature(3)
        assert False  # pragma: no cover
    except ValueError:
        assert True
    try:
        arr = np.zeros(12)
        arr[1] = 100
        monthly.set_min_temperature(arr)
        assert False  # pragma: no cover
    except ValueError:
        assert True
    try:
        arr = np.ones(12)
        arr[1] = -100
        monthly.set_max_temperature(arr)
        assert False  # pragma: no cover
    except ValueError:
        assert True


def test_monthly_monthly_limits():
    monthly = MonthlyTemperatureLimit(np.linspace(-12, -1, 12), np.linspace(0, 11, 12))
    assert np.allclose(monthly.get_max_temperature_monthly(2), np.tile(np.linspace(0, 11, 12), 2))
    assert np.allclose(monthly.get_min_temperature_monthly(2), np.tile(np.linspace(-12, -1, 12), 2))


def test_monthly_hourly_limits():
    monthly = MonthlyTemperatureLimit(np.linspace(-12, -1, 12), np.linspace(0, 11, 12))
    UPM = np.array([744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744])
    assert np.allclose(monthly.get_max_temperature_hourly(2, UPM), np.tile(np.repeat(np.linspace(0, 11, 12), UPM), 2))
    assert np.allclose(monthly.get_min_temperature_hourly(2, UPM), np.tile(np.repeat(np.linspace(-12, -1, 12), UPM), 2))


# test hourly limits
def test_hourly_limits():
    hourly = HourlyTemperatureLimit(np.linspace(-12, -1, 8760), np.linspace(0, 11, 8760))
    assert not hourly.constant_limits
    assert np.allclose(hourly._max_temperature, np.linspace(0, 11, 8760))
    assert np.allclose(hourly._min_temperature, np.linspace(-12, -1, 8760))


def test_hourly_set_limits():
    hourly = HourlyTemperatureLimit(np.zeros(8760), np.ones(8760))
    hourly.set_min_temperature(np.linspace(-12, -1, 8760))
    hourly.set_max_temperature(np.linspace(0, 11, 8760))
    assert np.allclose(hourly._max_temperature, np.linspace(0, 11, 8760))
    assert np.allclose(hourly._min_temperature, np.linspace(-12, -1, 8760))
    hourly.set_max_temperature(list(range(8760)))
    hourly.set_min_temperature(list(range(-8760, 0, 1)))
    assert np.allclose(hourly._max_temperature, np.linspace(0, 8759, 8760))
    assert np.allclose(hourly._min_temperature, np.linspace(-8760, -1, 8760))


def test_hourly_check():
    hourly = HourlyTemperatureLimit(np.zeros(8760), np.ones(8760))
    assert not hourly.check_input(2)
    assert not hourly.check_input(2.5)
    assert not hourly.check_input([3, 4])
    assert not hourly.check_input(np.array([3, 4]))
    assert hourly.check_input(np.ones(8760))
    assert hourly.check_input([1] * 8760)
    try:
        hourly.set_min_temperature([3])
        assert False  # pragma: no cover
    except ValueError:
        assert True
    try:
        hourly.set_max_temperature([3])
        assert False  # pragma: no cover
    except ValueError:
        assert True
    try:
        hourly.set_min_temperature(3)
        assert False  # pragma: no cover
    except ValueError:
        assert True
    try:
        hourly.set_max_temperature(3)
        assert False  # pragma: no cover
    except ValueError:
        assert True
    try:
        arr = np.zeros(8760)
        arr[1] = 100
        hourly.set_min_temperature(arr)
        assert False  # pragma: no cover
    except ValueError:
        assert True
    try:
        arr = np.ones(8760)
        arr[1] = -100
        hourly.set_max_temperature(arr)
        assert False  # pragma: no cover
    except ValueError:
        assert True


def test_hourly_monthly_limits():
    hourly = HourlyTemperatureLimit(np.linspace(-12, -1, 8760), np.linspace(0, 11, 8760))
    try:
        hourly.get_min_temperature_monthly(3)
        assert False  # pragma: no cover
    except RuntimeError:
        assert True
    try:
        hourly.get_max_temperature_monthly(3)
        assert False  # pragma: no cover
    except RuntimeError:
        assert True


def test_hourly_hourly_limits():
    hourly = HourlyTemperatureLimit(np.linspace(-12, -1, 8760), np.linspace(0, 11, 8760))
    UPM = np.array([744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744])
    assert np.allclose(hourly.get_max_temperature_hourly(2, UPM), np.tile(hourly._max_temperature, 2))
    assert np.allclose(hourly.get_min_temperature_hourly(2, UPM), np.tile(hourly._min_temperature, 2))
