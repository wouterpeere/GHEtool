import pytest

from GHEtool import *
from GHEtool.VariableClasses.FluidData.CommercialFluids import *

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
    assert fluid.__export__() == {'name': 'MPG', 'percentage': 25, 'type': 'mass percentage'}


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


def test_freezing_point():
    fluid = ConstantFluidData(0.5, 1000, 4186, 0.001)
    with pytest.raises(ValueError):
        fluid.test_freezing(5)

    fluid = TemperatureDependentFluidData('MPG', 30)

    assert not fluid.test_freezing(-5)
    assert fluid.test_freezing(-50)


def test_with_volume_percentage():
    fluid_vol_per = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)
    mass_per = fluid_vol_per._convert_to_mass_percentage(25)
    fluid_mass_per = TemperatureDependentFluidData('MPG', mass_per)
    assert fluid_vol_per.create_constant(5) == fluid_mass_per.create_constant(5)


def test_stability_convert_percentages():
    # check circular behaviour
    fluid = TemperatureDependentFluidData('MPG', 20)

    assert np.isclose(20, fluid._convert_to_vol_percentage(fluid._convert_to_mass_percentage(20)))
    assert np.isclose(5, fluid._convert_to_vol_percentage(fluid._convert_to_mass_percentage(5)))

    fluid = TemperatureDependentFluidData('MEG', 20)
    assert np.isclose(20, fluid._convert_to_vol_percentage(fluid._convert_to_mass_percentage(20)))
    assert np.isclose(5, fluid._convert_to_vol_percentage(fluid._convert_to_mass_percentage(5)))

    fluid = TemperatureDependentFluidData('Thermox DTX', 28, mass_percentage=False)
    assert np.isclose(20, fluid._convert_to_vol_percentage(fluid._convert_to_mass_percentage(20)))
    assert np.isclose(5, fluid._convert_to_vol_percentage(fluid._convert_to_mass_percentage(5)))


def test_temperature_dependent_fluid_data_neg_temperatures():
    fluid = TemperatureDependentFluidData('MPG', 25)
    assert np.isclose(fluid.k_f(-20), 0.44057954246124154)
    fluid = TemperatureDependentFluidData('Thermox DTX', 25)
    assert np.isclose(fluid.k_f(-25), 0.4851181912179882)


def test_commercial_fluids_data():
    fluid = ThermoxDTX(0.28)
    assert np.isclose(fluid.freeze_point(0.28), -15)
    assert np.isclose(fluid.conductivity(10), 0.475)
    assert np.isclose(fluid.conductivity(5), 0.473)
    assert np.isclose(fluid.density(10), 1046)
    assert np.isclose(fluid.specific_heat(10), 3780)
    assert np.isclose(fluid.viscosity(10), 3.28 * fluid.density(10) * 1e-6)

    assert np.allclose(fluid.conductivity([10, 12]), [0.475, 0.4758])
    assert np.allclose(fluid.density([10, 12]), [1046, 1045.6])
    assert np.allclose(fluid.specific_heat([10, 12]), [3780, 3780.])
    assert np.allclose(fluid.viscosity([10, 12]), [0.00343088, 0.003216388])

    fluid = TemperatureDependentFluidData('Thermox DTX', 28, mass_percentage=False)
    assert np.isclose(fluid.freezing_point, -15)
    assert np.isclose(fluid.k_f(10), 0.475)
    assert np.isclose(fluid.k_f(5), 0.473)
    assert np.isclose(fluid.rho(10), 1046)
    assert np.isclose(fluid.cp(10), 3780)
    assert np.isclose(fluid.mu(10), 3.28 * fluid.rho(10) * 1e-6)

    assert (np.isclose(fluid.rho(100), fluid.rho(80)))

    fluid = CoolflowNTP(0.33)
    assert np.isclose(fluid.freeze_point(0.33), -15)
    assert np.isclose(fluid.conductivity(10), 0.444)
    assert np.isclose(fluid.conductivity(5), 0.443)
    assert np.isclose(fluid.density(10), 1037)
    assert np.isclose(fluid.specific_heat(10), 3820)
    assert np.isclose(fluid.viscosity(10), 5.46 * fluid.density(10) * 1e-6)

    fluid = TemperatureDependentFluidData('Coolflow NTP', 33, mass_percentage=False)
    assert np.isclose(fluid.freezing_point, -15)
    assert np.isclose(fluid.k_f(10), 0.444)
    assert np.isclose(fluid.k_f(5), 0.443)
    assert np.isclose(fluid.rho(10), 1037)
    assert np.isclose(fluid.cp(10), 3820)
    assert np.isclose(fluid.mu(10), 5.46 * fluid.rho(10) * 1e-6)

    # test bounds error
    assert np.isclose(fluid.k_f(-100), 0.435)
    assert np.isclose(fluid.mu(-100), 0.02204968)
    assert np.isclose(fluid.rho(-100), 1046.0)
    assert np.isclose(fluid.cp(-100), 3770.0)

    with pytest.raises(ValueError):
        fluid = ThermoxDTX(100)

    # test kilfrost
    fluid = KilfrostGEO(0.35)
    assert np.isclose(fluid.freeze_point(0.35), -17.5)
    assert np.isclose(fluid.conductivity(10), 0.504)
    assert np.isclose(fluid.conductivity(5), 0.497)
    assert np.isclose(fluid.density(10), 1148.5)
    assert np.isclose(fluid.specific_heat(10), 3176)
    assert np.isclose(fluid.viscosity(10), 3.6821 * 1e-3)

    fluid = TemperatureDependentFluidData('Kilfrost GEO', 35, mass_percentage=False)
    assert np.isclose(fluid.freezing_point, -17.5)
    assert np.isclose(fluid.k_f(10), 0.504)
    assert np.isclose(fluid.k_f(5), 0.497)
    assert np.isclose(fluid.rho(10), 1148.5)
    assert np.isclose(fluid.cp(10), 3176)
    assert np.isclose(fluid.mu(10), 3.6821 * 1e-3)

    # test kilfrost GEO Plus
    fluid = KilfrostGEOPlus(0.42)
    assert np.isclose(fluid.freeze_point(0.42), -20)
    assert np.isclose(fluid.conductivity(10), 0.494)
    assert np.isclose(fluid.conductivity(5), 0.487)
    assert np.isclose(fluid.density(10), 1162.8)
    assert np.isclose(fluid.specific_heat(10), 2960)
    assert np.isclose(fluid.viscosity(10), 3.9509 * 1e-3)

    fluid = TemperatureDependentFluidData('Kilfrost GEO Plus', 42, mass_percentage=False)
    assert np.isclose(fluid.freezing_point, -20)
    assert np.isclose(fluid.k_f(10), 0.494)
    assert np.isclose(fluid.k_f(5), 0.487)
    assert np.isclose(fluid.rho(10), 1162.8)
    assert np.isclose(fluid.cp(10), 2960)
    assert np.isclose(fluid.mu(10), 3.9509 * 1e-3)


def test_temp():
    temp = []
    for i in [0, 10, 20, 30, 40, 50, 60]:
        fluid = TemperatureDependentFluidData('MMA', i, mass_percentage=False)
        temp.append(round(fluid.freezing_point, 3))
    print(temp)
