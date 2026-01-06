"""
This file contains the test for the pipedata
"""
import math
import pytest

from GHEtool.VariableClasses.PipeData import *
from GHEtool.VariableClasses import ConstantFluidData, ConstantFlowRate, TemperatureDependentFluidData
import matplotlib.pyplot as plt
import numpy as np
import pygfunction as gt


### Test U-pipes
def test_empty_class():
    assert not SingleUTube().check_values()
    assert not DoubleUTube().check_values()
    assert not MultipleUTube().check_values()


def test_axissym():
    single = SingleUTube(1, 0.016, 0.02, 2, 0.02)
    double = DoubleUTube(1, 0.016, 0.02, 2, 0.02)
    np.testing.assert_array_almost_equal(single._axis_symmetrical_pipe,
                                         [(-0.02, 2.4492935982947064e-18), (0.02, -4.898587196589413e-18)])
    np.testing.assert_array_almost_equal(double._axis_symmetrical_pipe,
                                         [(-0.02, 2.4492935982947064e-18), (0.02, -4.898587196589413e-18),
                                          (-3.673940397442059e-18, -0.02), (6.123233995736766e-18, 0.02)])
    np.testing.assert_array_almost_equal(single._axis_symmetrical_pipe,
                                         MultipleUTube(1, 0.16, 0.02, 2, 0.02, 1)._axis_symmetrical_pipe)
    np.testing.assert_array_almost_equal(double._axis_symmetrical_pipe,
                                         MultipleUTube(1, 0.16, 0.02, 2, 0.02, 2)._axis_symmetrical_pipe)


def test_calculate_thermal_resistance():
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.2)
    single = SingleUTube(1, 0.016, 0.02, 2, 0.02)
    double = DoubleUTube(1, 0.016, 0.02, 2, 0.02)
    Us = MultipleUTube(1, 0.016, 0.02, 2, 0.02, 1)
    Ud = MultipleUTube(1, 0.016, 0.02, 2, 0.02, 2)

    single.calculate_resistances(fluid_data, flow_data)
    double.calculate_resistances(fluid_data, flow_data)
    Us.calculate_resistances(fluid_data, flow_data)
    Ud.calculate_resistances(fluid_data, flow_data)
    assert np.isclose(single.R_p, 0.017757199605368243)
    assert np.isclose(single.R_f, 0.008698002460890118)
    assert np.isclose(double.R_p, 0.017757199605368243)
    assert np.isclose(double.R_f, 0.017963387333190542)
    assert np.allclose((single.R_f, single.R_p), (Us.R_f, Us.R_p))
    assert np.allclose((double.R_f, double.R_p), (Ud.R_f, Ud.R_p))


def test_equivalent_borehole_resistance_U_tubes():
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.2)
    single = SingleUTube(1, 0.016, 0.02, 2, 0.04)
    double = DoubleUTube(1, 0.016, 0.02, 2, 0.04)
    single.calculate_resistances(fluid_data, flow_data)
    double.calculate_resistances(fluid_data, flow_data)
    borehole = gt.boreholes.Borehole(100, 1, 0.07, 0, 0)
    pipe = single.pipe_model(2, borehole)
    assert np.isclose(pipe.effective_borehole_thermal_resistance(0.1, 4180), 0.13637413925456277)
    pipe = double.pipe_model(2, borehole)
    assert np.isclose(pipe.effective_borehole_thermal_resistance(0.2, 4180), 0.09065168435087693)

    flow_data = ConstantFlowRate(mfr=0.4, flow_per_borehole=False)
    single.calculate_resistances(fluid_data, flow_data, nb_of_boreholes=2)
    double.calculate_resistances(fluid_data, flow_data, nb_of_boreholes=2)
    pipe = single.pipe_model(2, borehole)
    assert np.isclose(pipe.effective_borehole_thermal_resistance(0.1, 4180), 0.13637413925456277)
    pipe = double.pipe_model(2, borehole)
    assert np.isclose(pipe.effective_borehole_thermal_resistance(0.2, 4180), 0.09065168435087693)


def test_convective_resistance():
    # TODO add variable flow rate as well
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.2)
    single = SingleUTube(1, 0.016, 0.02, 2, 0.04)
    double = DoubleUTube(1, 0.016, 0.02, 2, 0.04)

    assert np.isclose(single.calculate_convective_resistance(flow_data, fluid_data), 0.00869800367167177)
    assert np.isclose(single.calculate_convective_resistance(flow_data, fluid_data, temperature=5), 0.00869800367167177)
    assert np.allclose(single.calculate_convective_resistance(flow_data, fluid_data, temperature=np.array([5, 6])),
                       [0.00869800367167177, 0.00869800367167177])
    fluid_data = TemperatureDependentFluidData('MPG', 30)
    assert np.isclose(single.calculate_convective_resistance(flow_data, fluid_data, temperature=5), 0.2011253894370123)
    assert np.allclose(single.calculate_convective_resistance(flow_data, fluid_data, temperature=np.array([5, 6])),
                       [0.2011253894370123, 0.20075604])
    # test array-model
    individual = []
    temp_range = np.arange(-5, 20, 1)
    for temp in temp_range:
        single.calculate_resistances(fluid_data, flow_data, temperature=temp)
        individual.append(single.R_f)
    array = single.calculate_convective_resistance(flow_data, fluid_data, temperature=temp_range)
    assert np.allclose(array, individual)

    temp_range = np.arange(-5, 20, 1)
    individual = []
    for temp in temp_range:
        double.calculate_resistances(fluid_data, flow_data, temperature=temp)
        individual.append(double.R_f)
    array = double.calculate_convective_resistance(flow_data, fluid_data, temperature=temp_range)
    assert np.allclose(array, individual)

    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    individual = []
    temp_range = np.arange(-5, 20, 1)
    for temp in temp_range:
        single.calculate_resistances(fluid_data, flow_data, temperature=temp)
        individual.append(single.R_f)
    array = single.calculate_convective_resistance(flow_data, fluid_data, temperature=temp_range)
    assert np.allclose(array, individual)

    temp_range = np.arange(-5, 20, 1)
    individual = []
    for temp in temp_range:
        double.calculate_resistances(fluid_data, flow_data, temperature=temp)
        individual.append(double.R_f)
    array = double.calculate_convective_resistance(flow_data, fluid_data, temperature=temp_range)
    assert np.allclose(array, individual)


def test_draw_internals(monkeypatch):
    pipe = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05)
    monkeypatch.setattr(plt, 'show', lambda: None)
    pipe.draw_borehole_internal(0.075)
    assert pipe.R_f == 0
    assert pipe.R_p == 0
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.2)
    pipe.calculate_resistances(fluid_data, flow_data)
    pipe.draw_borehole_internal(0.075)


def test_pipe_data():
    data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    assert data.k_g == 1
    assert data.r_in == 0.015
    assert data.r_out == 0.02
    assert data.k_p == 0.4
    assert data.D_s == 0.05
    assert data.number_of_pipes == 2


def test_pipe_data_equal():
    data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    data2 = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    assert data == data2


def test_pipe_data_unequal():
    data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    data2 = MultipleUTube(1, 0.016, 0.02, 0.4, 0.05, 2)
    assert data != data2


### Test Coaxial pipes
k_g = 1.0  # Grout thermal conductivity [W/m.K]
k_p = 0.4  # Pipe thermal conductivity [W/m.K]
r_in_in = 0.0221  # Inside pipe inner radius [m]
r_in_out = 0.025  # Inside pipe outer radius [m]
r_out_in = 0.0487  # Outer pipe inside radius [m]
r_out_out = 0.055  # Outer pipe outside radius [m]


def test_empty_coaxial():
    assert not CoaxialPipe().check_values()


def test_draw_coaxial_internals(monkeypatch):
    pipe = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g)
    monkeypatch.setattr(plt, 'show', lambda: None)
    pipe.draw_borehole_internal(0.075)
    assert pipe.R_ff == 0
    assert pipe.R_fp == 0
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.2)
    pipe.calculate_resistances(fluid_data, flow_data)
    pipe.draw_borehole_internal(0.075)


def test_calculate_resistance_coaxial():
    pipe = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=True)
    fluid = TemperatureDependentFluidData('MPG', 20)
    flow_data = ConstantFlowRate(mfr=0.5)
    pipe.calculate_resistances(fluid, flow_data, temperature=20)
    assert np.isclose(pipe.R_fp, 0.11803503887356001)
    assert np.isclose(pipe.R_ff, 0.16491519753761458)
    pipe = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=False)
    flow_data = ConstantFlowRate(mfr=0.5)
    pipe.calculate_resistances(fluid, flow_data, temperature=20)
    assert np.isclose(pipe.R_fp, 0.11803503887356001)
    assert np.isclose(pipe.R_ff, 0.16491519753761458)
    flow_data = ConstantFlowRate(mfr=1, flow_per_borehole=False)
    pipe.calculate_resistances(fluid, flow_data, temperature=20, nb_of_boreholes=2)
    assert np.isclose(pipe.R_fp, 0.11803503887356001)
    assert np.isclose(pipe.R_ff, 0.16491519753761458)


def test_calculate_resistance_coaxial_different_outer_conductivity():
    pipe = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=True, k_p_out=0.2)
    fluid = TemperatureDependentFluidData('MPG', 20)
    flow_data = ConstantFlowRate(mfr=0.5)
    pipe.calculate_resistances(fluid, flow_data, temperature=20)
    assert np.isclose(pipe.R_fp, 0.1664396892206207)
    assert np.isclose(pipe.R_ff, 0.16491519753761458)


def test_calculate_borehole_equivalent_resistance_coaxial():
    pipe = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=True)
    fluid = TemperatureDependentFluidData('MPG', 20)
    flow_data = ConstantFlowRate(mfr=0.5)
    pipe.calculate_resistances(fluid, flow_data, temperature=20)
    borehole = gt.boreholes.Borehole(100, 1, 0.075, 0, 0)
    model = pipe.pipe_model(2, borehole)
    assert np.isclose(model.effective_borehole_thermal_resistance(0.5, 4180), 0.17312532151975354)
    pipe = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=False)
    fluid = TemperatureDependentFluidData('MPG', 20)
    flow_data = ConstantFlowRate(mfr=0.5)
    pipe.calculate_resistances(fluid, flow_data, temperature=20)
    model = pipe.pipe_model(2, borehole)
    assert np.isclose(model.effective_borehole_thermal_resistance(0.5, 4180), 0.17312532151975354)

    # pygfunction itself
    is_inner_inlet = True
    for i in range(1, 12, 2):
        pipe_ghe = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=False)
        fluid = TemperatureDependentFluidData('MPG', 20)
        flow_data = ConstantFlowRate(mfr=0.5)
        pipe_ghe.calculate_resistances(fluid, flow_data, temperature=20)
        pipe = gt.pipes.Coaxial(pos=(0., 0.),
                                r_in=np.array([r_out_in, r_in_in]) if is_inner_inlet else
                                np.array([r_in_in, r_out_in]),
                                r_out=np.array([r_out_out, r_in_out]) if is_inner_inlet else
                                np.array([r_in_out, r_out_out]),
                                borehole=borehole, k_s=i, k_g=k_g, R_ff=pipe_ghe.R_ff, R_fp=pipe_ghe.R_fp, J=2)


def test_calculate_borehole_equivalent_resistance_coaxial_different_outer_conductivity():
    pipe = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=True, k_p_out=0.2)
    fluid = TemperatureDependentFluidData('MPG', 20)
    flow_data = ConstantFlowRate(mfr=0.5)
    pipe.calculate_resistances(fluid, flow_data, temperature=20)
    borehole = gt.boreholes.Borehole(100, 1, 0.075, 0, 0)
    model = pipe.pipe_model(2, borehole)
    assert np.isclose(model.effective_borehole_thermal_resistance(0.5, 4180), 0.22128574562981232)


def test_pipe_data_equal_coaxial():
    data = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=True)
    data2 = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=True)
    assert data == data2


def test_pipe_data_unequal_coaxial():
    data = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=True)
    data2 = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=False)
    assert data != data2


def test_pipe_data_unequal_cross():
    data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    data2 = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=True)
    assert data != data2
    assert data2 != data


def test_reynolds_number():
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.2)
    double = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    assert np.isclose(double.Re(fluid_data=fluid_data, flow_rate_data=flow_data), 4244.131815783876)
    coaxial = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=True)
    assert np.isclose(coaxial.Re(fluid_data=fluid_data, flow_rate_data=flow_data), 1727.5977540504243)
    assert np.isclose(7234.108922823884, Separatus(1.5).Re(fluid_data, flow_data))

    # now with a flow per borefield
    flow_data = ConstantFlowRate(mfr=0.4, flow_per_borehole=False)
    double = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    assert np.isclose(double.Re(fluid_data=fluid_data, flow_rate_data=flow_data, nb_of_boreholes=2), 4244.131815783876)
    coaxial = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=True)
    assert np.isclose(coaxial.Re(fluid_data=fluid_data, flow_rate_data=flow_data, nb_of_boreholes=2),
                      1727.5977540504243)
    assert np.isclose(7234.108922823884, Separatus(1.5).Re(fluid_data, flow_data, nb_of_boreholes=2))

    flow_data = ConstantFlowRate(mfr=0.2, flow_per_borehole=False, series_factor=2)
    double = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    assert np.isclose(double.Re(fluid_data=fluid_data, flow_rate_data=flow_data, nb_of_boreholes=2), 4244.131815783876)
    coaxial = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=True)
    assert np.isclose(coaxial.Re(fluid_data=fluid_data, flow_rate_data=flow_data, nb_of_boreholes=2),
                      1727.5977540504243)
    assert np.isclose(7234.108922823884, Separatus(1.5).Re(fluid_data, flow_data, nb_of_boreholes=2))


def test_pressure_drop():
    fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow_data = ConstantFlowRate(mfr=0.3)
    single = MultipleUTube(1, 0.02, 0.02, 0.4, 0.05, 1)
    double = MultipleUTube(1, 0.013, 0.016, 0.4, 0.05, 2)
    assert np.isclose(single.pressure_drop(fluid_data, flow_data, 100), 4.474549607676448)
    assert np.isclose(single.pressure_drop(fluid_data, flow_data, 100, False), 4.4688388696204555)
    assert np.isclose(double.pressure_drop(fluid_data, flow_data, 100), 10.347836812519452)
    assert np.isclose(double.pressure_drop(fluid_data, flow_data, 100, False), 10.339838859988387)
    coaxial = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=True)
    assert np.isclose(coaxial.pressure_drop(fluid_data, flow_data, 100), 0.1639237572210245)
    assert np.isclose(19.84145159678991, Separatus(1.5).pressure_drop(fluid_data, flow_data, 100))

    # with flow rate per borefield
    flow_data = ConstantFlowRate(mfr=0.6, flow_per_borehole=False)
    single = MultipleUTube(1, 0.02, 0.02, 0.4, 0.05, 1)
    double = MultipleUTube(1, 0.013, 0.016, 0.4, 0.05, 2)
    assert np.isclose(single.pressure_drop(fluid_data, flow_data, 100, nb_of_boreholes=2), 4.474549607676448)
    assert np.isclose(single.pressure_drop(fluid_data, flow_data, 100, nb_of_boreholes=2, include_bend=False),
                      4.4688388696204555)
    assert np.isclose(double.pressure_drop(fluid_data, flow_data, 100, nb_of_boreholes=2), 10.347836812519452)
    assert np.isclose(double.pressure_drop(fluid_data, flow_data, 100, nb_of_boreholes=2, include_bend=False),
                      10.339838859988387)
    coaxial = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=True)
    assert np.isclose(coaxial.pressure_drop(fluid_data, flow_data, 100, nb_of_boreholes=2), 0.1639237572210245)
    assert np.isclose(19.84145159678991, Separatus(1.5).pressure_drop(fluid_data, flow_data, 100, nb_of_boreholes=2))

    flow_data = ConstantFlowRate(mfr=0.3, flow_per_borehole=False, series_factor=2)
    single = MultipleUTube(1, 0.02, 0.02, 0.4, 0.05, 1)
    double = MultipleUTube(1, 0.013, 0.016, 0.4, 0.05, 2)
    assert np.isclose(single.pressure_drop(fluid_data, flow_data, 100, nb_of_boreholes=2), 4.474549607676448)
    assert np.isclose(single.pressure_drop(fluid_data, flow_data, 100, nb_of_boreholes=2, include_bend=False),
                      4.4688388696204555)
    assert np.isclose(double.pressure_drop(fluid_data, flow_data, 100, nb_of_boreholes=2), 10.347836812519452)
    assert np.isclose(double.pressure_drop(fluid_data, flow_data, 100, nb_of_boreholes=2, include_bend=False),
                      10.339838859988387)
    coaxial = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=True)
    assert np.isclose(coaxial.pressure_drop(fluid_data, flow_data, 100, nb_of_boreholes=2), 0.1639237572210245)
    assert np.isclose(19.84145159678991, Separatus(1.5).pressure_drop(fluid_data, flow_data, 100, nb_of_boreholes=2))


def test_turbocollector():
    turbo = Turbocollector(1.5, 0.013, 0.016, 0.035, 1)
    flow_borehole = ConstantFlowRate(vfr=0.25)
    flow_borefield = ConstantFlowRate(vfr=0.5, flow_per_borehole=False)
    fluid = TemperatureDependentFluidData('MPG', 25)

    assert np.isclose(turbo.Re(fluid, flow_borehole, temperature=5),
                      turbo.Re(fluid, flow_borefield, temperature=5, nb_of_boreholes=2))
    # TODO test Rb en Dp
    assert np.isclose(turbo.pressure_drop(fluid, flow_borehole, 100, temperature=5),
                      turbo.pressure_drop(fluid, flow_borefield, 100, temperature=5, nb_of_boreholes=2))
    borehole = gt.boreholes.Borehole(100, 1, 0.07, 0, 0)
    turbo1 = turbo
    turbo.calculate_resistances(fluid, flow_borehole, temperature=5)
    turbo1.calculate_resistances(fluid, flow_borefield, temperature=5, nb_of_boreholes=2)

    assert np.isclose(turbo.pipe_model(2, borehole).effective_borehole_thermal_resistance(
        flow_borehole.mfr_borehole(fluid, temperature=5), fluid.cp(temperature=5)),
        turbo1.pipe_model(2, borehole).effective_borehole_thermal_resistance(
            flow_borefield.mfr_borehole(fluid, temperature=5, nb_of_boreholes=2), fluid.cp(temperature=5)))

    # test array-model
    individual = []
    temp_range = np.arange(-5, 20, 1)
    for temp in temp_range:
        turbo.calculate_resistances(fluid, flow_borehole, temperature=temp)
        individual.append(turbo.R_f)
    array = turbo.calculate_convective_resistance(flow_borehole, fluid, temperature=temp_range)
    assert np.allclose(array, individual)

    individual = []
    temp_range = np.arange(-5, 20, 1)
    turbo.number_of_pipes = 2
    for temp in temp_range:
        turbo.calculate_resistances(fluid, flow_borehole, temperature=temp)
        individual.append(turbo.R_f)
    array = turbo.calculate_convective_resistance(flow_borehole, fluid, temperature=temp_range)
    assert np.allclose(array, individual)


def test_conical_pipe_get_pipe_model():
    pipe = ConicalPipe(1.5, 0.0135, 0.013, 80, 160, 0.016, 0.4, 0.035, 1)
    with pytest.raises(ValueError):
        pipe._get_pipe_model(1)
    with pytest.raises(ValueError):
        pipe._get_pipe_model(170)

    assert pipe._top_pipe == MultipleUTube(1.5, 0.0135, 0.016, 0.4, 0.035, 1)
    assert pipe._end_pipe == MultipleUTube(1.5, 0.013, 0.016, 0.4, 0.035, 1)

    assert pipe._top_pipe == pipe._get_pipe_model(80)[0]
    assert pipe._top_pipe == pipe._get_pipe_model(80)[1]
    assert MultipleUTube(1.5, 0.01325, 0.016, 0.4, 0.035, 1) == pipe._get_pipe_model(160)[0]
    assert pipe._end_pipe == pipe._get_pipe_model(160)[1]


def test_conical_resistances():
    pipe = ConicalPipe(1.5, 0.0135, 0.013, 80, 160, 0.016, 0.4, 0.035, 1)
    pipe.use_approx = True
    begin_pipe = SingleUTube(1.5, 0.0135, 0.016, 0.4, 0.035)
    fluid = TemperatureDependentFluidData('MPG', 20).create_constant(0)
    flow = ConstantFlowRate(vfr=0.2)

    # below threshold
    pipe.calculate_resistances(fluid, flow, 60)
    begin_pipe.calculate_resistances(fluid, flow, borehole_length=60)

    assert pipe.R_p == begin_pipe.R_p
    assert pipe.R_f == begin_pipe.R_f

    pipe.calculate_resistances(fluid, flow, 100)
    assert np.isclose(0.06797080927504552, pipe.R_p)
    assert np.isclose(0.18460159035588664, pipe.R_f)

    pipe.calculate_resistances(fluid, flow, 200)
    assert np.isclose(0.07360723858372777, pipe.R_p)
    assert np.isclose(0.17492415197256533, pipe.R_f)

    flow = ConstantFlowRate(vfr=0.4, flow_per_borehole=False)

    pipe.calculate_resistances(fluid, flow, 60, nb_of_boreholes=2)
    begin_pipe.calculate_resistances(fluid, flow, borehole_length=60, nb_of_boreholes=2)

    assert pipe.R_p == begin_pipe.R_p
    assert pipe.R_f == begin_pipe.R_f

    pipe.calculate_resistances(fluid, flow, 100, nb_of_boreholes=2)
    assert np.isclose(0.06797080927504552, pipe.R_p)
    assert np.isclose(0.18460159035588664, pipe.R_f)

    pipe.calculate_resistances(fluid, flow, 200, nb_of_boreholes=2)
    assert np.isclose(0.07360723858372777, pipe.R_p)
    assert np.isclose(0.17492415197256533, pipe.R_f)

    flow = ConstantFlowRate(vfr=0.2)

    pipe.use_approx = False
    # below threshold
    pipe.calculate_resistances(fluid, flow, 60)
    begin_pipe.calculate_resistances(fluid, flow, borehole_length=60)

    assert np.isclose(pipe.R_p, begin_pipe.R_p)
    assert np.isclose(pipe.R_f, begin_pipe.R_f)

    pipe.calculate_resistances(fluid, flow, 100)
    assert np.isclose(0.06797080927504552, pipe.R_p)
    assert np.isclose(0.18460159035588664, pipe.R_f)

    pipe.calculate_resistances(fluid, flow, 200)
    assert np.isclose(0.07358834823796871, pipe.R_p)
    assert np.isclose(0.17880743362651824, pipe.R_f)


def test_conical_pressure_drop():
    pipe = ConicalPipe(1.5, 0.0135, 0.013, 80, 160, 0.016, 0.4, 0.035, 1)
    fluid = TemperatureDependentFluidData('MPG', 20).create_constant(0)
    flow = ConstantFlowRate(vfr=0.2)
    assert 0 == pipe._pressure_conical(fluid, flow, end=80)


def test_conical_pressure_drop_total():
    pipe = ConicalPipe(1.5, 0.0135, 0.013, 80, 160, 0.016, 0.4, 0.035, 1)
    pipe_double = ConicalPipe(1.5, 0.0135, 0.013, 80, 160, 0.016, 0.4, 0.035, 2)
    pipe.use_approx = True
    pipe_double.use_approx = True
    fluid = TemperatureDependentFluidData('MPG', 20).create_constant(0)
    flow = ConstantFlowRate(vfr=0.2)

    assert pipe._top_pipe.pressure_drop(fluid, flow, 60) == pipe.pressure_drop(fluid, flow, 60)
    assert np.isclose(13.287983793150875, pipe.pressure_drop(fluid, flow, 100))
    assert np.isclose(31.27107478947142, pipe.pressure_drop(fluid, flow, 180))
    assert pipe_double._top_pipe.pressure_drop(fluid, flow, 60) == pipe_double.pressure_drop(fluid, flow, 60)
    assert np.isclose(6.640762214442462, pipe_double.pressure_drop(fluid, flow, 100))
    assert np.isclose(12.552561831103098, pipe_double.pressure_drop(fluid, flow, 180))

    # more accurate simulate using the average integral theorem
    pipe.use_approx = False
    pipe_double.use_approx = False
    fluid = TemperatureDependentFluidData('MPG', 20).create_constant(0)
    flow = ConstantFlowRate(vfr=0.2)

    assert np.isclose(7.94740480425995, pipe.pressure_drop(fluid, flow, 60))
    assert np.isclose(13.287595907784938, pipe.pressure_drop(fluid, flow, 100))
    # this is significantly lower than the approximation, since there is a laminar-transient boundary crossed
    # in the approximation, this causes the whole conical section to become transient, where the more accurate method
    # only makes part of it transient, leading to a lower pressure drop in the end
    assert np.isclose(28.880311539363454, pipe.pressure_drop(fluid, flow, 180))
    assert np.isclose(pipe_double._top_pipe.pressure_drop(fluid, flow, 60), pipe_double.pressure_drop(fluid, flow, 60))
    assert np.isclose(6.640568081247919, pipe_double.pressure_drop(fluid, flow, 100))
    assert np.isclose(12.539012292217867, pipe_double.pressure_drop(fluid, flow, 180))

    fluid = TemperatureDependentFluidData('MPG', 20)
    flow = ConstantFlowRate(mfr=0.2)

    assert np.isclose(7.790713878176526, pipe.pressure_drop(fluid, flow, 60, temperature=0))
    assert np.isclose(13.025770150586625, pipe.pressure_drop(fluid, flow, 100, temperature=0))
    assert np.isclose(12.292102456222025, pipe_double.pressure_drop(fluid, flow, 180, temperature=0))

    flow = ConstantFlowRate(mfr=0.4, flow_per_borehole=False)
    assert np.isclose(7.790713878176526, pipe.pressure_drop(fluid, flow, 60, temperature=0, nb_of_boreholes=2))
    assert np.isclose(13.025770150586625, pipe.pressure_drop(fluid, flow, 100, temperature=0, nb_of_boreholes=2))
    assert np.isclose(12.292102456222025, pipe_double.pressure_drop(fluid, flow, 180, temperature=0, nb_of_boreholes=2))


def test_conical_reynolds():
    pipe = ConicalPipe(1.5, 0.0135, 0.013, 80, 160, 0.016, 0.4, 0.035, 1)
    pipe_double = ConicalPipe(1.5, 0.0135, 0.013, 80, 160, 0.016, 0.4, 0.035, 2)
    begin_pipe = SingleUTube(1.5, 0.0135, 0.016, 0.4, 0.035)
    fluid = TemperatureDependentFluidData('MPG', 20).create_constant(0)
    flow = ConstantFlowRate(vfr=0.2)
    assert begin_pipe.Re(fluid, flow) == pipe.Re(fluid, flow, borehole_length=60)
    assert np.isclose(begin_pipe.Re(fluid, flow) / 2, pipe_double.Re(fluid, flow, borehole_length=60))
    pipe = ConicalPipe(1.5, 0.0135, 0.013, 0, 100, 0.016, 0.4, 0.035, 1)
    assert np.isclose(2273.275997711447, pipe.Re(fluid, flow, borehole_length=100))
    assert np.isclose(1116.4960021656223, pipe_double.Re(fluid, flow, borehole_length=100))
    pipe = ConicalPipe(1.5, 0.0135, 0.013, 0, 100, 0.016, 0.4, 0.035, 1)
    assert np.isclose(2294.99693335425, pipe.Re(fluid, flow, borehole_length=200))

    pipe = ConicalPipe(1.5, 0.0135, 0.013, 80, 160, 0.016, 0.4, 0.035, 1)
    pipe_double = ConicalPipe(1.5, 0.0135, 0.013, 80, 160, 0.016, 0.4, 0.035, 2)
    begin_pipe = SingleUTube(1.5, 0.0135, 0.016, 0.4, 0.035)
    fluid = TemperatureDependentFluidData('MPG', 20).create_constant(0)
    flow = ConstantFlowRate(vfr=0.4, flow_per_borehole=False)
    assert begin_pipe.Re(fluid, flow, nb_of_boreholes=2) == pipe.Re(fluid, flow, borehole_length=60, nb_of_boreholes=2)
    assert np.isclose(begin_pipe.Re(fluid, flow, nb_of_boreholes=2) / 2,
                      pipe_double.Re(fluid, flow, borehole_length=60, nb_of_boreholes=2))
    pipe = ConicalPipe(1.5, 0.0135, 0.013, 0, 100, 0.016, 0.4, 0.035, 1)
    assert np.isclose(2273.275997711447, pipe.Re(fluid, flow, borehole_length=100, nb_of_boreholes=2))
    assert np.isclose(1116.4960021656223, pipe_double.Re(fluid, flow, borehole_length=100, nb_of_boreholes=2))
    pipe = ConicalPipe(1.5, 0.0135, 0.013, 0, 100, 0.016, 0.4, 0.035, 1)
    assert np.isclose(2294.99693335425, pipe.Re(fluid, flow, borehole_length=200, nb_of_boreholes=2))

    flow = ConstantFlowRate(mfr=0.2)
    pipe = ConicalPipe(1.5, 0.0135, 0.013, 80, 160, 0.016, 0.4, 0.035, 1)

    assert begin_pipe.Re(fluid, flow) == pipe.Re(fluid, flow, borehole_length=70)
    assert np.isclose(begin_pipe.Re(fluid, flow) / 2, pipe_double.Re(fluid, flow, borehole_length=60))
    pipe = ConicalPipe(1.5, 0.0135, 0.013, 0, 100, 0.016, 0.4, 0.035, 1)
    assert np.isclose(2228.5248303199014, pipe.Re(fluid, flow, borehole_length=100))
    assert np.isclose(1094.5169289975574, pipe_double.Re(fluid, flow, borehole_length=100))
    pipe = ConicalPipe(1.5, 0.0135, 0.013, 0, 100, 0.016, 0.4, 0.035, 1)
    assert np.isclose(2249.818172820547, pipe.Re(fluid, flow, borehole_length=200))


def test_explicit_method_errors():
    single = SingleUTube(1.5, 0.013, 0.016, 0.04, 0.035)
    double = DoubleUTube(1.5, 0.013, 0.016, 0.04, 0.035)
    triple = MultipleUTube(1.5, 0.013, 0.016, 0.04, 0.035, 3)
    flow_borehole = ConstantFlowRate(vfr=0.25)
    fluid = TemperatureDependentFluidData('MPG', 25).create_constant(0)
    borehole = gt.boreholes.Borehole(100, 1, 0.075, 0, 0)

    with pytest.raises(NotImplementedError):
        single.explicit_model_borehole_resistance(fluid, flow_borehole, 2, borehole, order=3)
    with pytest.raises(NotImplementedError):
        double.explicit_model_borehole_resistance(fluid, flow_borehole, 2, borehole, order=2)
    with pytest.raises(NotImplementedError):
        triple.explicit_model_borehole_resistance(fluid, flow_borehole, 2, borehole, order=2)


def test_repr_():
    single = MultipleUTube(1, 0.018, 0.02, 0.4, 0.05, 1)
    double = MultipleUTube(1, 0.013, 0.016, 0.4, 0.05, 2)
    coaxial = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, k_p, k_g, is_inner_inlet=True)
    separatus = Separatus(2)
    turbo = Turbocollector(1.5, 0.013, 0.016, 0.05, 1)
    vario = ConicalPipe(1.5, 0.0135, 0.013, 80, 160, 0.016, 0.4, 0.035, 1)
    assert {'diameter [mm]': 40,
            'epsilon [mm]': 0.001,
            'k_g [W/(m·K)]': 1,
            'k_p [W/(m·K)]': 0.4,
            'nb_of_tubes': 1,
            'spacing [mm]': 50.0,
            'thickness [mm]': 2.0,
            'type': 'U'} == single.__export__()
    assert {'diameter [mm]': 32,
            'epsilon [mm]': 0.001,
            'k_g [W/(m·K)]': 1,
            'k_p [W/(m·K)]': 0.4,
            'nb_of_tubes': 2,
            'spacing [mm]': 50.0,
            'thickness [mm]': 3.0,
            'type': 'U'} == double.__export__()
    assert {'epsilon [mm]': 1e-06,
            'inner_diameter [mm]': 50.0,
            'inner_thickness [mm]': 2.8999999999999986,
            'k_g [W/(m·K)]': 1.0,
            'k_p_in [W/(m·K)]': 0.4,
            'k_p_out [W/(m·K)]': 0.4,
            'outer_diameter [mm]': 110.0,
            'outer_thickness [mm]': 6.299999999999997,
            'type': 'Coaxial'} == coaxial.__export__()
    assert {'k_g [W/(m·K)]': 2, 'type': 'Separatus'} == separatus.__export__()
    assert {'diameter [mm]': 32.0,
            'k_g [W/(m·K)]': 1.5,
            'nb_of_tubes': 1,
            'spacing [mm]': 50.0,
            'thickness [mm]': 3.0,
            'type': 'Turbocollector'} == turbo.__export__()
    assert {'begin conical [m]': 80,
            'diameter [mm]': 32.0,
            'end conical [m]': 160,
            'end thickness [mm]': 3.0,
            'epsilon [mm]': 0.001,
            'k_g [W/(m·K)]': 1.5,
            'k_p [W/(m·K)]': 0.4,
            'nb_of_tubes': 1,
            'spacing [mm]': 35.0,
            'start thickness [mm]': 2.5,
            'type': 'Conical'} == vario.__export__()
