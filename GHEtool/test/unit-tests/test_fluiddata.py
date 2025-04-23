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


def test_constant_fluid_data():
    fluid = ConstantFluidData(0.568, 998, 4180, 1e-3)
    assert fluid.k_f() == 0.568
    assert fluid.rho() == 998
    assert fluid.cp() == 4180
    assert fluid.mu() == 1e-3
    assert fluid.freezing_point is None
    assert fluid.k_f(temperature=0) == 0.568
    assert fluid.rho(temperature=0) == 998
    assert fluid.cp(temperature=0) == 4180
    assert fluid.mu(temperature=0) == 1e-3
    fluid = ConstantFluidData(0.568, 998, 4180, 1e-3, -5)
    assert fluid.freezing_point == -5


def test_check_constant_fluid_data():
    fluid = ConstantFluidData(0.568, 998, 4180, 1e-3)
    assert fluid.check_values()


def test_equal():
    fluid1 = ConstantFluidData(0.568, 998, 4180, 1e-3)
    fluid2 = ConstantFluidData(0.568, 998, 4180, 2e-3)
    fluid3 = ConstantFluidData(0.568, 998, 4180, 1e-3)
    fluid = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    assert fluid2 != fluid1
    assert fluid1 == fluid3
    assert fluid != fluid1


def test_repr_constant_fluid_data():
    fluid = ConstantFluidData(0.568, 998, 4180, 1e-3)
    assert fluid.__export__() == {'Pr': 7.359154929577465,
                                  'cp [J/(kg·K)]': 4180,
                                  'freezing_point [°C]': None,
                                  'k_f [W/(m·K)]': 0.568,
                                  'mu [Pa·s]': 0.001,
                                  'nu [m²/s]': 1.002004008016032e-06,
                                  'rho [kg/m³]': 998}


def test_temperature_dependent_fluid_data():
    for fluid_str in ('Water', 'MEG', 'MPG', 'MMA', 'MEA'):
        for percentage in (0, 10, 20, 30):
            for temperature in np.linspace(TemperatureDependentFluidData(fluid_str, percentage).freezing_point, 100,
                                           200):
                fluid = TemperatureDependentFluidData(fluid_str, percentage)
                fluid_gt = gt.media.Fluid(fluid_str, percentage, temperature)
                assert np.isclose(fluid.k_f(temperature), fluid_gt.thermal_conductivity(), rtol=5e-3)
                assert np.isclose(fluid.cp(temperature), fluid_gt.specific_heat_capacity(), rtol=5e-3)
                assert np.isclose(fluid.rho(temperature), fluid_gt.density(), rtol=5e-3)
                assert np.isclose(fluid.mu(temperature), fluid_gt.dynamic_viscosity(), rtol=5e-3)


def test_create_constant():
    fluid = TemperatureDependentFluidData('MPG', 25)
    constant_fluid = fluid.create_constant(20)
    assert constant_fluid == ConstantFluidData(0.46785241126305993, 1019.2775612579634, 3920.4675112024747,
                                               0.0024452566486468344, -9.786660880295903)


def test_repr_temperature_dependent_fluid_data():
    fluid = TemperatureDependentFluidData('MPG', 25)
    assert fluid.__export__() == {'name': 'MPG', 'percentage': 25}


def test_check_values_temperature_dependent_fluid_data():
    fluid = TemperatureDependentFluidData('MPG', 25)
    assert fluid.check_values()


def test_eq_temperature_dependent_fluid_data():
    fluid = TemperatureDependentFluidData('MPG', 25)
    fluid1 = TemperatureDependentFluidData('MPG', 35)
    fluid2 = TemperatureDependentFluidData('MEG', 25)
    fluid3 = TemperatureDependentFluidData('MPG', 25)
    fluid4 = ConstantFluidData(0.568, 998, 4180, 1e-3)

    assert fluid != fluid4
    assert fluid != fluid1
    assert fluid == fluid3
    assert fluid != fluid2


def test_multiple_temperature_dependent_fluid_data():
    fluid = TemperatureDependentFluidData('MEA', 30)
    fluid.k_f(temperature=np.array([-5, 0, 5, 10, 15, 40, 50, 60]))


def test_unsupported_fluid():
    with pytest.raises(ValueError):
        TemperatureDependentFluidData('Ai', 30)
