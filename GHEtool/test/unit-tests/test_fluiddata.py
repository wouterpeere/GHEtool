import pytest

from GHEtool import *

import numpy as np
import pygfunction as gt


def test_fluid_data():
    data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    assert data.mfr == 0.2
    assert data.k_f == 0.568
    assert data.rho == 998
    assert data.Cp == 4180
    assert data.mu == 1e-3
    assert np.isclose(data.vfr, 0.20040080160320642)


def test_prandtl():
    data = FluidData()
    data.import_fluid_from_pygfunction(gt.media.Fluid('water', 100))
    assert np.isclose(data.Pr, 7.0030835773088835)


def test_fluid_data_equal():
    data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    data2 = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    assert data == data2


def test_fluid_data_unequal():
    data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    data2 = FluidData(0.2, 0.567, 998, 4180, 1e-3)
    assert data != data2


def test_unequal_cross():
    data_fluid = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    data_ground = GroundConstantTemperature(3, 10)
    assert data_ground != data_fluid
    assert data_fluid != data_ground


def test_set_mfr():
    data_fluid = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    data_fluid.set_mass_flow_rate(10)
    assert data_fluid.mfr == 10


def test_set_vfr():
    with pytest.raises(ValueError):
        FluidData(0.2, 0.568, 998, 4180, 1e-3, 0.2)
    data_fluid = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    assert data_fluid.flow_rate._vfr is None
    assert np.isclose(data_fluid.vfr, 0.20040080160320642)
    data_fluid.vfr = 0.2
    assert data_fluid.flow_rate._mfr is None
    assert data_fluid.vfr == 0.2
    assert np.isclose(data_fluid.mfr, 0.2 * 998 / 1000)

    data_fluid.mfr = 0.2
    assert data_fluid.flow_rate._mfr == 0.2
    assert data_fluid.flow_rate._vfr is None
    assert np.isclose(data_fluid.vfr, 0.20040080160320642)
    assert data_fluid.mfr == 0.2

    data_fluid = FluidData(None, 0.568, 998, 4180, 1e-3, 0.2)
    assert data_fluid.flow_rate._mfr is None
    assert data_fluid.vfr == 0.2
    assert np.isclose(data_fluid.mfr, 0.2 * 998 / 1000)


def test_import_fluid_from_pygfunction():
    data_fluid = FluidData()
    data_fluid.set_mass_flow_rate(0.2)
    test_data = gt.media.Fluid('MPG', 20)
    data_fluid.import_fluid_from_pygfunction(test_data)
    assert data_fluid.mu == test_data.mu
    assert data_fluid.rho == test_data.rho
    assert data_fluid.Cp == test_data.cp
    assert data_fluid.k_f == test_data.k


def test_repr_():
    data_fluid = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    assert 'Fluid parameters\n' \
           '\tThermal conductivity of the fluid [W/(m·K)]: 0.568\n' \
           '\tDensity of the fluid [kg/m³]: 998.000\n' \
           '\tThermal capacity of the fluid [J/(kg·K)]: 4180.000\n' \
           '\tDynamic viscosity [Pa·s]: 0.001\n' \
           '\tMass flow rate [kg/s] : 0.2' == data_fluid.__repr__()

    data_fluid = FluidData(None, 0.568, 998, 4180, 1e-3, 0.2)
    assert 'Fluid parameters\n' \
           '\tThermal conductivity of the fluid [W/(m·K)]: 0.568\n' \
           '\tDensity of the fluid [kg/m³]: 998.000\n' \
           '\tThermal capacity of the fluid [J/(kg·K)]: 4180.000\n' \
           '\tDynamic viscosity [Pa·s]: 0.001\n' \
           '\tVolume flow rate [l/s]: 0.2' == data_fluid.__repr__()
