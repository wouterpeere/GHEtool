import numpy as np
import pytest

from GHEtool import *
from GHEtool.VariableClasses import PressureDrop
from GHEtool.Methods.pressure_drop_calculation import calculate_pressure_drop_horizontal, calculate_total_pressure_drop, \
    create_pressure_drop_curve


def test_borehole():
    single_u = SingleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.2)
    pressure_drop = PressureDrop(single_u, fluid_data, flow_data, 0, 100, 0.02 - 0.0037 / 2, 15, 0, 0.02 - 0.0037 / 2,
                                 15, 0, 8, 1, 1)

    pressure_drop_series = PressureDrop(single_u, fluid_data, flow_data,
                                        0, 100, 0.02 - 0.0037 / 2, 15, 0, 0.02 - 0.0037 / 2, 15, 0, 8, 2, 1)
    pressure_drop_tichelmann = PressureDrop(single_u, fluid_data, flow_data,
                                            0, 100, 0.02 - 0.0037 / 2, 15, 0, 0.02 - 0.0037 / 2, 15, 0, 8, 1, 2)
    pressure_drop_both = PressureDrop(single_u, fluid_data, flow_data,
                                      0, 100, 0.02 - 0.0037 / 2, 15, 0, 0.02 - 0.0037 / 2, 15, 0, 8, 2, 2)

    assert np.isclose(pressure_drop.calculate_pressure_drop_borehole(),
                      pressure_drop_series.calculate_pressure_drop_borehole())
    assert np.isclose(pressure_drop.calculate_pressure_drop_borehole(),
                      pressure_drop_tichelmann.calculate_pressure_drop_borehole())
    assert np.isclose(pressure_drop.calculate_pressure_drop_borehole(),
                      pressure_drop_both.calculate_pressure_drop_borehole())


def test_lateral():
    single_u = SingleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.2)
    pressure_drop = PressureDrop(single_u, fluid_data, flow_data, 0, 100, 0.02 - 0.0037 / 2, 15, 0, 0, 0, 0, 8, 1, 1)
    pressure_drop_double = PressureDrop(single_u, fluid_data, ConstantFlowRate(mfr=0.4), 0, 100, 0.02 - 0.0037 / 2, 15,
                                        0, 0, 0, 0, 8, 1, 1)
    pressure_drop_four = PressureDrop(single_u, fluid_data, ConstantFlowRate(mfr=0.8), 0, 100, 0.02 - 0.0037 / 2, 15, 0,
                                      0, 0, 0, 8, 1, 1)

    pressure_drop_series = PressureDrop(single_u, fluid_data, flow_data,
                                        0, 100, 0.02 - 0.0037 / 2, 15, 0, 0, 0, 0, 8, 2, 1)
    pressure_drop_tichelmann = PressureDrop(single_u, fluid_data, flow_data,
                                            0, 100, 0.02 - 0.0037 / 2, 15, 0, 0, 0, 0, 8, 1, 2)
    pressure_drop_both = PressureDrop(single_u, fluid_data, flow_data,
                                      0, 100, 0.02 - 0.0037 / 2, 15, 0, 0, 0, 0, 8, 2, 2)

    assert np.isclose(pressure_drop.calculate_pressure_drop_lateral(), 0.26307939880441045 * 2)
    assert np.isclose(pressure_drop_series.calculate_pressure_drop_lateral(),
                      pressure_drop_double.calculate_pressure_drop_lateral())
    assert np.isclose(pressure_drop_tichelmann.calculate_pressure_drop_lateral(),
                      pressure_drop_double.calculate_pressure_drop_lateral())
    assert np.isclose(pressure_drop_both.calculate_pressure_drop_lateral(),
                      pressure_drop_four.calculate_pressure_drop_lateral())

    pressure_drop.minor_losses_lateral = 2
    assert np.isclose(pressure_drop.calculate_pressure_drop_lateral(), 0.5635804695478487)

    pressure_drop.fluid_data = TemperatureDependentFluidData('MPG', 25)
    assert np.isclose(pressure_drop.calculate_pressure_drop_lateral(temperature=20), 0.7050447750402659)


def test_main_header():
    single_u = SingleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.2)
    pressure_drop = PressureDrop(single_u, fluid_data, flow_data, 0, 100, 0.02 - 0.0037 / 2, 15, 0, 0.02 - 0.0037 / 2,
                                 15, 0, 8, 1, 1)
    pressure_drop_eight = PressureDrop(single_u, fluid_data, ConstantFlowRate(mfr=1.6), 0, 100, 0.02 - 0.0037 / 2, 15,
                                       0, 0.02 - 0.0037 / 2, 15, 0, 8, 1, 1)

    pressure_drop_series = PressureDrop(single_u, fluid_data, flow_data,
                                        0, 100, 0.02 - 0.0037 / 2, 15, 0, 0.02 - 0.0037 / 2, 15, 0, 8, 2, 1)
    pressure_drop_tichelmann = PressureDrop(single_u, fluid_data, flow_data,
                                            0, 100, 0.02 - 0.0037 / 2, 15, 0, 0.02 - 0.0037 / 2, 15, 0, 8, 1, 2)
    pressure_drop_both = PressureDrop(single_u, fluid_data, flow_data,
                                      0, 100, 0.02 - 0.0037 / 2, 15, 0, 0.02 - 0.0037 / 2, 15, 0, 8, 2, 2)

    assert np.isclose(pressure_drop.calculate_pressure_drop_main(),
                      pressure_drop_eight.calculate_pressure_drop_lateral())
    assert np.isclose(pressure_drop_series.calculate_pressure_drop_main(),
                      pressure_drop_eight.calculate_pressure_drop_lateral())
    assert np.isclose(pressure_drop_tichelmann.calculate_pressure_drop_main(),
                      pressure_drop_eight.calculate_pressure_drop_lateral())
    assert np.isclose(pressure_drop_both.calculate_pressure_drop_main(),
                      pressure_drop_eight.calculate_pressure_drop_lateral())

    pressure_drop.minor_losses_main = 2
    pressure_drop_eight.minor_losses_lateral = 2
    assert np.isclose(pressure_drop.calculate_pressure_drop_main(),
                      pressure_drop_eight.calculate_pressure_drop_lateral())

    pressure_drop.fluid_data = TemperatureDependentFluidData('MPG', 25)
    pressure_drop_eight.fluid_data = TemperatureDependentFluidData('MPG', 25)
    assert np.isclose(pressure_drop.calculate_pressure_drop_main(temperature=20),
                      pressure_drop_eight.calculate_pressure_drop_lateral(temperature=20))


def test_total_pressure_drop():
    single_u = SingleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.2)
    pressure_drop = PressureDrop(single_u, fluid_data, flow_data, 0, 100, 0.02 - 0.0037 / 2, 15, 1, 0.02 - 0.0037 / 2,
                                 15, 2, 8, 1, 1)
    assert np.isclose(pressure_drop.calculate_total_pressure_drop(),
                      pressure_drop.calculate_pressure_drop_borehole() + pressure_drop.calculate_pressure_drop_lateral()
                      + pressure_drop.calculate_pressure_drop_main())


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
