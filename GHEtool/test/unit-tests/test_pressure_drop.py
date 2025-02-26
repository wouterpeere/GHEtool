import numpy as np

from GHEtool import *
from GHEtool.Methods.pressure_drop_calculation import calculate_pressure_drop_horizontal, calculate_total_pressure_drop, \
    create_pressure_drop_curve


def test_horizontal():
    fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)

    assert np.isclose(calculate_pressure_drop_horizontal(fluid_data, 0.02 - 0.0037 / 2, 15, 0), 0.26307939880441045)
    assert np.isclose(calculate_pressure_drop_horizontal(fluid_data, 0.02 - 0.0037 / 2, 15, 2), 0.3005010707434382)


def test_total_pressure_drop():
    single_u = SingleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    double_u = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    fluid_data = FluidData(0.3, 0.568, 998, 4180, 1e-3)

    assert np.isclose(calculate_total_pressure_drop(single_u, fluid_data, 100, 0.02 - 0.0037 / 2, 10, 2),
                      35.307092460895696)
    assert np.isclose(calculate_total_pressure_drop(double_u, fluid_data, 100, 0.02 - 0.0037 / 2, 10, 2),
                      11.139813565855187)


def test_range_pressure_drop():
    single_u = SingleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)

    pressure, _ = create_pressure_drop_curve(single_u, fluid_data, 100, 0.02 - 0.0037 / 2, 10, 2)
    assert np.allclose(pressure, np.array(
        [0, 0.25311388, 0.50658373, 0.76040955, 1.90081784, 2.79351152, 3.81007873, 4.95814128, 6.23317941,
         7.63146176, 9.14983034, 10.78556091, 12.53626754, 14.39983464, 16.37436709, 18.45815002, 20.64962988,
         22.94737642, 25.3500745, 27.85650679, 30.46554156, 33.1761225, 35.98726063, 38.89802652, 41.90754461,
         45.0149878, 48.21957292, 51.52055679, 54.9172327, 58.40892744]))
