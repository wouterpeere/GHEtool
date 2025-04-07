import numpy as np
import pytest

from GHEtool import *
from GHEtool.Methods.pressure_drop_calculation import calculate_pressure_drop_horizontal, calculate_total_pressure_drop, \
    create_pressure_drop_curve


def test_horizontal():
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.2)

    assert np.isclose(calculate_pressure_drop_horizontal(fluid_data, flow_data, 0.02 - 0.0037 / 2, 15, 0),
                      0.26307939880441045)
    assert np.isclose(calculate_pressure_drop_horizontal(fluid_data, flow_data, 0.02 - 0.0037 / 2, 15, 2),
                      0.3005010707434382)
    fluid_data = TemperatureDependentFluidData('MPG', 25)
    assert np.isclose(
        calculate_pressure_drop_horizontal(fluid_data, flow_data, 0.02 - 0.0037 / 2, 15, 0, temperature=20),
        0.33420109590883734)


def test_total_pressure_drop():
    single_u = SingleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    double_u = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.3)

    assert np.isclose(calculate_total_pressure_drop(single_u, fluid_data, flow_data, 100, 0.02 - 0.0037 / 2, 10, 2),
                      35.307092460895696)
    assert np.isclose(calculate_total_pressure_drop(double_u, fluid_data, flow_data, 100, 0.02 - 0.0037 / 2, 10, 2),
                      11.139813565855187)
    fluid_data = TemperatureDependentFluidData('MPG', 25)
    assert np.isclose(
        calculate_total_pressure_drop(double_u, fluid_data, flow_data, 100, 0.02 - 0.0037 / 2, 10, 2, temperature=20),
        11.139813565855187)


def test_range_pressure_drop():
    single_u = SingleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.2)

    pressure, _ = create_pressure_drop_curve(single_u, fluid_data, flow_data, 100, 0.02 - 0.0037 / 2, 10, 2)
    assert np.allclose(pressure, np.array(
        [0., 0.2531815, 0.50685423, 0.76101819, 1.90189987, 2.7952022, 3.8125133, 4.961455, 6.23750754, 7.63693955,
         9.15659304, 10.79374378, 12.54600583, 14.41126361, 16.38762198, 18.4733661, 20.6669424, 22.96692063,
         25.37198565, 27.88092014, 30.49259237, 33.20594602, 36.01999211, 38.93380122, 41.94649778, 45.05725469,
         48.26528879, 51.56985689, 54.97025229, 58.46580177]))

    fluid_data = TemperatureDependentFluidData('Water', 0)
    with pytest.raises(TypeError):
        pressure, _ = create_pressure_drop_curve(single_u, fluid_data, flow_data, 100, 0.02 - 0.0037 / 2, 10, 2)
