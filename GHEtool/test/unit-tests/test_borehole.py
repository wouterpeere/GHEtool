import copy

import pygfunction as gt
import numpy as np
import pytest

from GHEtool import FluidData, DoubleUTube, SingleUTube, MultipleUTube, ConstantFluidData, ConstantFlowRate, \
    TemperatureDependentFluidData, ConicalPipe
from GHEtool.VariableClasses import Borehole

fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
flow_data = ConstantFlowRate(mfr=0.2)
pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
old_fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)


def test_load_old_fluid_data():
    borehole = Borehole(fluid_data=old_fluid_data, pipe_data=pipe_data)
    assert borehole.fluid_data == fluid_data
    assert borehole.flow_data == flow_data


def test_del_flow_data():
    borehole = Borehole()
    assert borehole.flow_data is None
    borehole.flow_data = flow_data
    assert borehole.flow_data == flow_data
    del borehole.flow_data
    assert borehole.flow_data is None


def test_fluid_data_without_pipe():
    borehole = Borehole()
    assert borehole.fluid_data is None
    borehole.fluid_data = fluid_data
    assert borehole.fluid_data == fluid_data
    del borehole.fluid_data
    assert borehole.fluid_data is None


def test_fluid_data_with_pipe_first_added():
    borehole = Borehole()
    borehole.pipe_data = pipe_data
    assert borehole.pipe_data.R_f == 0
    borehole.fluid_data = fluid_data
    assert borehole.pipe_data.R_f == 0
    borehole.pipe_data.calculate_resistances(fluid_data, flow_data)
    assert np.isclose(0.01663038005086118, borehole.pipe_data.R_f)


def test_fluid_data_with_pipe_later_added():
    borehole = Borehole()
    borehole.pipe_data = pipe_data
    borehole.fluid_data = fluid_data
    assert borehole.pipe_data.R_f == 0
    borehole.pipe_data.calculate_resistances(fluid_data, flow_data)
    assert np.isclose(0.01663038005086118, borehole.pipe_data.R_f)


def test_pipe_data():
    borehole = Borehole()
    assert borehole.pipe_data is None
    borehole.pipe_data = pipe_data
    assert borehole.pipe_data == pipe_data
    assert borehole.pipe_data.R_p == 0
    borehole.pipe_data.calculate_resistances(fluid_data, flow_data)
    assert np.isclose(0.11446505967405429, borehole.pipe_data.R_p)
    del borehole.pipe_data
    assert borehole.pipe_data is None


def test_equivalent_loading():
    borehole1 = Borehole()
    borehole2 = Borehole()

    borehole1.fluid_data = fluid_data
    borehole1.pipe_data = copy.copy(pipe_data)

    borehole2.pipe_data = copy.copy(pipe_data)
    borehole2.fluid_data = fluid_data

    assert borehole2 == borehole1
    assert not borehole1 == fluid_data
    borehole1._pipe_data.k_g = 3
    assert not borehole1 == borehole2


def test_calculate_Rb():
    borehole = Borehole()
    borehole.pipe_data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    borehole.fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    borehole.flow_data = ConstantFlowRate(mfr=0.2)

    assert np.isclose(borehole.calculate_Rb(100, 1, 0.075, 3), 0.09483159131195469)

    borehole.fluid_data = TemperatureDependentFluidData('MPG', 25)
    with pytest.raises(TypeError):
        np.isclose(borehole.calculate_Rb(100, 1, 0.075, 3), 0.09483159131195469)
    assert np.isclose(borehole.calculate_Rb(100, 1, 0.075, 3, temperature=20), 0.13807578911314267)

    borehole.fluid_data = TemperatureDependentFluidData('Thermox DTX', 25)
    with pytest.raises(TypeError):
        np.isclose(borehole.calculate_Rb(100, 1, 0.075, 3), 0.09483159131195469)
    assert np.isclose(borehole.calculate_Rb(100, 1, 0.075, 3, temperature=20), 0.13513271096418708)


def test_Rb():
    borehole = Borehole()
    assert borehole.get_Rb(100, 1, 0.07, 2) == 0.12

    # set pipe and fluid data
    borehole.fluid_data = fluid_data
    borehole.pipe_data = pipe_data
    borehole.flow_data = flow_data

    assert np.isclose(borehole.calculate_Rb(100, 1, 0.075, 3), 0.09483159131195469)

    # set Rb
    borehole.Rb = 0.12
    assert borehole.get_Rb(100, 1, 0.07, 2) == 0.12

    # set pipe and fluid data
    borehole.fluid_data = fluid_data
    borehole.pipe_data = pipe_data
    borehole.flow_data = flow_data

    assert np.isclose(borehole.calculate_Rb(100, 1, 0.075, 3), 0.09483159131195469)
    del borehole.pipe_data
    assert borehole.get_Rb(100, 1, 0.07, 2) == 0.12
    borehole.pipe_data = pipe_data
    assert np.isclose(borehole.calculate_Rb(100, 1, 0.075, 3), 0.09483159131195469)
    del borehole.fluid_data
    assert borehole.get_Rb(100, 1, 0.07, 2) == 0.12
    borehole.fluid_data = fluid_data
    assert np.isclose(borehole.calculate_Rb(100, 1, 0.075, 3), 0.09483159131195469)


def test_calculate_Rb_no_data():
    borehole = Borehole()
    with pytest.raises(ValueError):
        borehole.calculate_Rb(100, 1, 0.075, 3)


def test_Rb_values():
    borehole = Borehole()
    mfr_range = np.arange(0.05, 0.55, 0.05)
    pipe_data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, number_of_pipes=2, epsilon=1e-6)
    borehole.pipe_data = pipe_data
    Rb_list = []
    for mfr in mfr_range:
        fluid_data = FluidData(mfr, 0.568, 998, 4180, 1e-3)
        borehole.fluid_data = fluid_data
        Rb_list.append(borehole.get_Rb(100, 1, 0.075, 3))

    assert np.allclose(Rb_list, [0.2696064888020322, 0.16229265041543758, 0.11073836048982678, 0.09483159131195469,
                                 0.08742765267449451, 0.08315828854931047, 0.08046372254501538, 0.07864703705590415,
                                 0.07735912210040842, 0.07640933344353783])


def test_assign_by_initiation():
    borehole = Borehole(fluid_data, pipe_data, flow_data)
    assert np.isclose(borehole.calculate_Rb(100, 1, 0.075, 3), 0.09483159131195469)
    assert not borehole.use_constant_Rb


def test_repr_():
    borehole = Borehole()
    borehole.pipe_data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    borehole.fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    borehole.flow_data = ConstantFlowRate(vfr=0.2)

    assert {'fluid': {'Pr': 7.359154929577465,
                      'cp [J/(kg·K)]': 4180,
                      'freezing_point [°C]': None,
                      'k_f [W/(m·K)]': 0.568,
                      'mu [Pa·s]': 0.001,
                      'nu [m²/s]': 1.002004008016032e-06,
                      'rho [kg/m³]': 998},
            'pipe': {'diameter [mm]': 40,
                     'epsilon [mm]': 0.001,
                     'k_g [W/(m·K)]': 1,
                     'k_p [W/(m·K)]': 0.4,
                     'nb_of_tubes': 2,
                     'spacing [mm]': 50.0,
                     'thickness [mm]': 5.0,
                     'type': 'U'},
            'flow': {'vfr [l/s]': 0.2}} == borehole.__export__()

    borehole = Borehole()
    assert {'Rb': 0.12} == borehole.__export__()


def test_calculate_rb_range():
    borehole = Borehole()
    borehole.pipe_data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    borehole.fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    borehole.flow_data = ConstantFlowRate(mfr=0.2)

    val = borehole.calculate_Rb(100, 1, 0.075, 3, temperature=5)
    assert np.allclose([val, val, val], borehole.calculate_Rb(100, 1, 0.075, 3, temperature=np.array([1, 5, 10])))

    # with temperature dependent range
    borehole.fluid_data = TemperatureDependentFluidData('MPG', 25)

    assert np.allclose(np.array([borehole.calculate_Rb(100, 1, 0.075, 3, temperature=1),
                                 borehole.calculate_Rb(100, 1, 0.075, 3, temperature=5),
                                 borehole.calculate_Rb(100, 1, 0.075, 3, temperature=10)]),
                       borehole.calculate_Rb(100, 1, 0.075, 3, temperature=np.array([1, 5, 10])))


def test_uncertainty():
    borehole = Borehole()
    borehole.pipe_data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    borehole.fluid_data = TemperatureDependentFluidData('MPG', 25)
    borehole.flow_data = ConstantFlowRate(mfr=0.2)

    nb_of_points = [10, 25, 50, 75, 100]

    for idx, nb in enumerate(nb_of_points):
        calculated = borehole.calculate_Rb(100, 1, 0.075, 3,
                                           temperature=np.linspace(borehole.fluid_data.freezing_point, 100, 500),
                                           nb_of_points=nb)
        manual = np.array([borehole.calculate_Rb(100, 1, 0.075, 3, temperature=i) for i in
                           np.linspace(borehole.fluid_data.freezing_point, 100, 500)])

        diff = calculated - manual
        print(max(diff), max(diff / manual))


def test_saved_data_reynolds():
    borehole = Borehole()
    borehole.pipe_data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    borehole.fluid_data = TemperatureDependentFluidData('MPG', 25)
    borehole.flow_data = ConstantFlowRate(vfr=0.3)

    resistance1 = borehole.calculate_Rb(100, 1, 0.075, 3, temperature=np.array([0, 1, 2, 5]))
    assert borehole._stored_interp_data == {'D': 1,
                                            'H': 100,
                                            'flow': "{'vfr [l/s]': 0.3}",
                                            'fluid': "{'name': 'MPG', 'percentage': 25, 'type': 'mass percentage'}",
                                            'k_s': 3,
                                            'pipe': "{'type': 'U', 'nb_of_tubes': 2, 'thickness [mm]': 5.0, 'diameter "
                                                    "[mm]': 40.0, 'spacing [mm]': 50.0, 'k_g [W/(m·K)]': 1, 'k_p "
                                                    "[W/(m·K)]': 0.4, 'epsilon [mm]': 0.001}",
                                            'r_b': 0.075}
    resistance2 = borehole.calculate_Rb(110, 1, 0.075, 3, temperature=np.array([0, 1, 2, 5]))
    assert not np.allclose(resistance1, resistance2)
    assert borehole._stored_interp_data == {'D': 1,
                                            'H': 110,
                                            'flow': "{'vfr [l/s]': 0.3}",
                                            'fluid': "{'name': 'MPG', 'percentage': 25, 'type': 'mass percentage'}",
                                            'k_s': 3,
                                            'pipe': "{'type': 'U', 'nb_of_tubes': 2, 'thickness [mm]': 5.0, 'diameter "
                                                    "[mm]': 40.0, 'spacing [mm]': 50.0, 'k_g [W/(m·K)]': 1, 'k_p "
                                                    "[W/(m·K)]': 0.4, 'epsilon [mm]': 0.001}",
                                            'r_b': 0.075}
    assert np.allclose(resistance1, borehole.calculate_Rb(100, 1, 0.075, 3, temperature=np.array([0, 1, 2, 5])))


def test_saved_data_reynolds_commercial():
    borehole = Borehole()
    borehole.pipe_data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    borehole.fluid_data = TemperatureDependentFluidData('Thermox DTX', 25)
    borehole.flow_data = ConstantFlowRate(vfr=0.3)

    assert np.allclose([0.12849791, 0.12843995, 0.1283812, 0.12820668],
                       borehole.calculate_Rb(100, 1, 0.075, 3, temperature=np.array([0, 1, 2, 5])))


def test_borehole_resistance_conical():
    borehole = Borehole()
    borehole.pipe_data = ConicalPipe(1.5, 0.0135, 0.013, 80, 160, 0.016, 0.4, 0.035, 1)
    borehole.fluid_data = TemperatureDependentFluidData('MEG', 25)
    borehole.flow_data = ConstantFlowRate(vfr=0.3)
    assert np.allclose([0.12693282, 0.12664951, 0.12644177, 0.12588726],
                       borehole.calculate_Rb(60, 1, 0.075, 3, temperature=np.array([0, 1, 2, 5])))
    borehole.pipe_data = SingleUTube(1.5, 0.0135, 0.016, 0.4, 0.035)
    assert np.allclose([0.12693282, 0.12664951, 0.12644177, 0.12588726],
                       borehole.calculate_Rb(60, 1, 0.075, 3, temperature=np.array([0, 1, 2, 5])))
    borehole.pipe_data = ConicalPipe(1.5, 0.0135, 0.013, 80, 160, 0.016, 0.4, 0.035, 1)
    borehole.fluid_data = TemperatureDependentFluidData('MEG', 25)
    borehole.flow_data = ConstantFlowRate(vfr=0.3)
    assert np.allclose([0.13332881, 0.13306602, 0.1328651, 0.13232777],
                       borehole.calculate_Rb(120, 1, 0.075, 3, temperature=np.array([0, 1, 2, 5])))
