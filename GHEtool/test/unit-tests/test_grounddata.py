import pytest

import numpy as np

from GHEtool.VariableClasses import GroundFluxTemperature, GroundConstantTemperature, GroundTemperatureGradient, \
    GroundLayer
from GHEtool.VariableClasses import FluidData


def test_ground_layer_class():
    layer_1 = GroundLayer(1, 2, 3)
    layer_2 = GroundLayer(2, 2, 3)
    assert layer_1 != layer_2
    layer_2 = GroundLayer(1, 2, 3)
    assert layer_1 == layer_2
    layer_1 = GroundConstantTemperature(10, 10)
    assert layer_1 != layer_2
    assert layer_2 != layer_1
    assert 10 == layer_2.non_negative(10)
    assert None is layer_2.non_negative(None)
    with pytest.raises(ValueError):
        layer_2.non_negative(0)
    with pytest.raises(ValueError):
        layer_2.non_negative(-10)


def test_empty():
    ground_flux_temperature = GroundFluxTemperature()
    ground_constant_temperature = GroundConstantTemperature()
    assert not ground_constant_temperature.check_values()
    assert not ground_flux_temperature.check_values()


def test_ground_data_equal():
    data = GroundFluxTemperature(3, 10, 2.4 * 10 ** 6, 0.06)
    data2 = GroundFluxTemperature(3, 10, 2.4 * 10 ** 6, 0.06)
    assert data == data2
    data = GroundConstantTemperature(3, 10, 2.4 * 10 ** 6)
    data2 = GroundConstantTemperature(3, 10, 2.4 * 10 ** 6)
    assert data == data2


def test_ground_data_unequal():
    data = GroundFluxTemperature(3, 10, 2.4 * 10 ** 6)
    data2 = GroundFluxTemperature(3, 11, 2.4 * 10 ** 6)
    assert data != data2
    data = GroundConstantTemperature(3, 10, 2.4 * 10 ** 6)
    data2 = GroundConstantTemperature(3, 11, 2.4 * 10 ** 6)
    assert data != data2
    fluid = FluidData(0.3, 3, 9710, 4165, 0.0001)
    assert fluid != data


def test_alpha():
    data = GroundFluxTemperature(3)
    assert np.isclose(data.alpha(100), 3 / data.volumetric_heat_capacity(100))
    data = GroundFluxTemperature()
    assert data.alpha() is None


def test_Tg():
    ground_flux_temperature = GroundFluxTemperature(3, 10, 2.4 * 10 ** 6, 0.06)
    ground_constant_temperature = GroundConstantTemperature(3, 10)
    ground_temperature_gradient = GroundTemperatureGradient(3, 10, 2.4 * 10 ** 6, 2)

    assert ground_constant_temperature.calculate_Tg(100) == 10
    assert ground_constant_temperature.calculate_Tg(100, 1) == 10
    assert ground_flux_temperature.calculate_Tg(0) == 10
    assert ground_flux_temperature.calculate_Tg(100) == 11
    assert ground_flux_temperature.calculate_Tg(100, 10) == 11.1
    assert ground_temperature_gradient.calculate_Tg(0) == 10
    assert ground_temperature_gradient.calculate_Tg(100) == 11
    assert ground_temperature_gradient.calculate_Tg(100, 10) == 11.1
    assert np.isclose(ground_temperature_gradient.calculate_Tg(100, 99.9), 11.998999999999114)


def test_delta_H():
    ground_flux_temperature = GroundFluxTemperature(3, 11, 2.4 * 10 ** 6, 0.06)
    ground_constant_temperature = GroundConstantTemperature(3, 11)
    ground_temperature_gradient = GroundTemperatureGradient(3, 11, 2.4 * 10 ** 6, 2)

    assert ground_constant_temperature.calculate_delta_H(1) == 0
    assert ground_temperature_gradient.calculate_delta_H(1) == 100
    assert ground_flux_temperature.calculate_delta_H(1) == 100
    assert ground_constant_temperature.max_depth(15) == 0
    assert ground_temperature_gradient.max_depth(15) == 400
    assert ground_flux_temperature.max_depth(15) == 400


def test_one_ground_layer_data():
    ground_data = GroundConstantTemperature(3, 10)
    assert ground_data.k_s(0) == 3
    assert ground_data.k_s(1) == 3
    assert ground_data.k_s(10) == 3
    assert ground_data.k_s(1000) == 3
    assert ground_data.k_s(1000, 1) == 3
    assert ground_data.k_s(10e8) == 3

    assert ground_data.volumetric_heat_capacity(0) == 2400000
    assert ground_data.volumetric_heat_capacity(1) == 2400000
    assert ground_data.volumetric_heat_capacity(10) == 2400000
    assert ground_data.volumetric_heat_capacity(1000) == 2400000
    assert ground_data.volumetric_heat_capacity(1000, 1) == 2400000
    assert ground_data.volumetric_heat_capacity(10e8) == 2400000


def test_ground_data_add_multiple_layers():
    layer_1 = GroundLayer(k_s=1, thickness=10)
    layer_2 = GroundLayer(k_s=2, thickness=15)
    layer_3 = GroundLayer(k_s=1, thickness=20)
    layer_4 = GroundLayer(k_s=2, thickness=None)

    constant = GroundConstantTemperature()
    constant.add_layer_on_bottom(layer_1)
    constant.add_layer_on_bottom(layer_2)
    constant.add_layer_on_bottom(layer_3)
    constant.add_layer_on_bottom(layer_4)

    assert np.array_equal(constant.layer_depths, [0, 10, 25, 45])
    assert constant.layers[0] == layer_1
    assert constant.layers[1] == layer_2
    assert constant.layers[2] == layer_3
    assert constant.layers[3] == layer_4

    constant_2 = GroundConstantTemperature()
    constant_2.add_layer_on_bottom([layer_1, layer_2, layer_3, layer_4])
    assert constant_2 == constant_2
    assert np.array_equal(constant_2.layer_depths, [0, 10, 25, 45])

    constant = GroundConstantTemperature()
    constant.add_layer_on_bottom(layer_4)
    assert constant.layers[0] == layer_4
    assert np.array_equal(constant.layer_depths, [0])
    try:
        constant.add_layer_on_bottom(layer_1)
        assert False  # pragma: no cover
    except ValueError:
        assert True

    constant = GroundConstantTemperature(3, 10)
    assert np.array_equal(constant.layer_depths, [0])
    assert constant.layers[0] == GroundLayer(3)
    try:
        constant.add_layer_on_bottom(layer_1)
        assert False  # pragma: no cover
    except ValueError:
        assert True

    constant_top = GroundConstantTemperature()
    constant_top.add_layer_on_top(layer_4)
    constant_top.add_layer_on_top(layer_3)
    constant_top.add_layer_on_top(layer_2)
    constant_top.add_layer_on_top(layer_1)

    assert np.array_equal(constant_top.layer_depths, [0, 10, 25, 45])
    assert constant_top.layers[0] == layer_1
    assert constant_top.layers[1] == layer_2
    assert constant_top.layers[2] == layer_3
    assert constant_top.layers[3] == layer_4

    assert constant_2 == constant_top
    constant_2_top = GroundConstantTemperature()
    constant_2_top.add_layer_on_top([layer_4, layer_3, layer_2, layer_1])
    assert constant_2_top == constant_2
    assert np.array_equal(constant_2_top.layer_depths, [0, 10, 25, 45])

    try:
        constant_2_top.add_layer_on_top(layer_4)
        assert False  # pragma: no cover
    except ValueError:
        assert True

    constant = GroundConstantTemperature(3, 10)
    try:
        constant.add_layer_on_top(layer_4)
        assert False  # pragma: no cover
    except ValueError:
        assert True

    constant_mixed = GroundConstantTemperature()
    constant_mixed.add_layer_on_top(layer_2)
    constant_mixed.add_layer_on_bottom(layer_3)
    constant_mixed.add_layer_on_top(layer_1)
    constant_mixed.add_layer_on_bottom(layer_4)


def test_check():
    ground_data = GroundConstantTemperature()
    try:
        ground_data.check_depth(0)
        assert False  # pragma: no cover
    except ValueError:
        assert True
    ground_data = GroundConstantTemperature(3, 10)
    ground_data.layers[0].thickness = 100
    with pytest.warns():
        assert ground_data.check_depth(100000000)
    ground_data.last_layer_infinite = False
    try:
        ground_data.check_depth(1000)
        assert False  # pragma: no cover
    except ValueError:
        assert True
    try:
        with pytest.warns():
            assert ground_data.check_depth(10)
            assert ground_data.check_depth(100)
        assert False  # pragma: no cover
    except:
        assert True


def test_multilayer_values():
    k_s_array = [1, 2, 1, 2]
    depth_array = [0, 10, 15, 20]
    constant = GroundConstantTemperature()
    assert 1 == constant.calculate_value(depth_array, np.cumsum(depth_array), k_s_array, 0, 0)
    assert 1 == constant.calculate_value(depth_array, np.cumsum(depth_array), k_s_array, 1, 0)
    assert 1 == constant.calculate_value(depth_array, np.cumsum(depth_array), k_s_array, 5, 0)
    assert 1 == constant.calculate_value(depth_array, np.cumsum(depth_array), k_s_array, 10, 0)
    assert 1 == constant.calculate_value(depth_array, np.cumsum(depth_array), k_s_array, 0, 0)
    with pytest.raises(ValueError):
        constant.calculate_value(depth_array, np.cumsum(depth_array), k_s_array, 1, 1)
    assert 1 == constant.calculate_value(depth_array, np.cumsum(depth_array), k_s_array, 5, 1)
    assert 1 == constant.calculate_value(depth_array, np.cumsum(depth_array), k_s_array, 10, 1)
    assert np.isclose(1 * 10 / 11 + 2 * 1 / 11,
                      constant.calculate_value(depth_array, np.cumsum(depth_array), k_s_array, 11, 0))
    assert np.isclose(((1 * 10 / 11 + 2 * 1 / 11) * 11 - 1) / 10,
                      constant.calculate_value(depth_array, np.cumsum(depth_array), k_s_array, 11, 1))
    assert np.isclose(2,
                      constant.calculate_value(depth_array, np.cumsum(depth_array), k_s_array, 11, 10))
    assert np.isclose(1 * 10 / 20 + 2 * 10 / 20,
                      constant.calculate_value(depth_array, np.cumsum(depth_array), k_s_array, 20, 0))
    assert np.isclose(1 * 10 / 24 + 2 * 14 / 24,
                      constant.calculate_value(depth_array, np.cumsum(depth_array), k_s_array, 24, 0))
    assert np.isclose(1 * 10 / 25 + 2 * 15 / 25,
                      constant.calculate_value(depth_array, np.cumsum(depth_array), k_s_array, 25, 0))
    assert np.isclose(1 * 10 / 30 + 2 * 15 / 30 + 1 * 5 / 30,
                      constant.calculate_value(depth_array, np.cumsum(depth_array),
                                               k_s_array, 30, 0))
    assert np.isclose(1.99997, constant.calculate_value(depth_array, np.cumsum(depth_array), k_s_array, 1000000, 0))

    layer_1 = GroundLayer(k_s=1, thickness=10)
    layer_2 = GroundLayer(k_s=2, thickness=15)
    layer_3 = GroundLayer(k_s=1, thickness=20)
    layer_4 = GroundLayer(k_s=2, thickness=None)

    constant = GroundConstantTemperature()
    constant.add_layer_on_bottom([layer_1, layer_2, layer_3, layer_4])
    assert 1 * 10 / 30 + 2 * 15 / 30 + 1 * 5 / 30 == constant.k_s(30)
    assert 2400000.0 == constant.volumetric_heat_capacity(30)


def test_repr_():
    ground_flux_temperature = GroundFluxTemperature(3, 11, 2.4 * 10 ** 6, 0.06)
    ground_constant_temperature = GroundConstantTemperature(3, 11)
    ground_temperature_gradient = GroundTemperatureGradient(3, 11, 2.4 * 10 ** 6, 2)
    assert 'Ground flux temperature\n' \
           '\tGround surface temperature [°C]: 11\n' \
           '\tGround flux [W/m²]: 0.06\n' \
           '\tConductivity [W/(m·K)]: 3\n' \
           '\tVolumetric heat capacity [MJ/(m³·K)]: 2.4' == ground_flux_temperature.__repr__()
    assert 'Constant ground temperature\n' \
           '\tGround temperature at infinity [°C]: 11\n' \
           '\tConductivity [W/(m·K)]: 3\n' \
           '\tVolumetric heat capacity [MJ/(m³·K)]: 2.4' == ground_constant_temperature.__repr__()
    assert 'Ground gradient temperature\n' \
           '\tGround surface temperature [°C]: 11\n' \
           '\tGradient [K/100m]: 2\n' \
           '\tConductivity [W/(m·K)]: 3\n' \
           '\tVolumetric heat capacity [MJ/(m³·K)]: 2.4' == ground_temperature_gradient.__repr__()

    # layers
    layer_1 = GroundLayer(k_s=1, thickness=10)
    layer_2 = GroundLayer(k_s=2, thickness=15)
    layer_3 = GroundLayer(k_s=1, thickness=20)
    layer_4 = GroundLayer(k_s=2, thickness=None)

    constant = GroundConstantTemperature()
    constant.add_layer_on_bottom([layer_1, layer_2, layer_3, layer_4])
    assert 'Constant ground temperature\n' \
           '\tGround temperature at infinity [°C]: None\n' \
           '\tLayers:\n' \
           '\t- Thickness [m]: 10, Conductivity [W/(m·K)]: 1, Volumetric heat capacity [MJ/(m³·K)]: 2.4\n' \
           '\t- Thickness [m]: 15, Conductivity [W/(m·K)]: 2, Volumetric heat capacity [MJ/(m³·K)]: 2.4\n' \
           '\t- Thickness [m]: 20, Conductivity [W/(m·K)]: 1, Volumetric heat capacity [MJ/(m³·K)]: 2.4\n' \
           '\t- Thickness [m]: None, Conductivity [W/(m·K)]: 2, Volumetric heat capacity [MJ/(m³·K)]: 2.4' \
           == constant.__repr__()
