import pytest

from GHEtool.VariableClasses import GroundFluxTemperature, GroundConstantTemperature, GroundDataBaseClass


def test_empty():
    ground_flux_temperature = GroundFluxTemperature()
    ground_constant_temperature = GroundConstantTemperature()
    assert not ground_constant_temperature.check_values()
    assert not ground_flux_temperature.check_values()


def test_ground_data_equal():
    data = GroundFluxTemperature(3, 10, 2.4*10**6, 0.06)
    data2 = GroundFluxTemperature(3, 10, 2.4*10**6, 0.06)
    assert data == data2
    data = GroundConstantTemperature(3, 10, 2.4*10**6)
    data2 = GroundConstantTemperature(3, 10, 2.4*10**6)
    assert data == data2


def test_ground_data_unequal():
    data = GroundFluxTemperature(3, 10, 2.4*10**6)
    data2 = GroundFluxTemperature(3, 11, 2.4*10**6)
    assert data != data2
    data = GroundConstantTemperature(3, 10, 2.4*10**6)
    data2 = GroundConstantTemperature(3, 11, 2.4*10**6)
    assert data != data2


def test_alpha():
    data = GroundFluxTemperature(3)
    assert data.alpha == 3 / data.volumetric_heat_capacity
    data = GroundFluxTemperature()
    assert data.alpha is None


def test_Tg():
    ground_flux_temperature = GroundFluxTemperature(3, 10, 2.4*10**6, 0.06)
    ground_constant_temperature = GroundConstantTemperature(3, 10)

    assert ground_constant_temperature.calculate_Tg() == 10
    assert ground_flux_temperature.calculate_Tg(0) == 10
    assert ground_flux_temperature.calculate_Tg(100) == 11
