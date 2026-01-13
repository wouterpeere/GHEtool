import pytest

import numpy as np

from GHEtool import *


def test_constant_flow_rate():
    with pytest.raises(ValueError):
        ConstantFlowRate(mfr=5, vfr=5)


def test_check_values_constant_flow_rate():
    flow = ConstantFlowRate()
    assert not flow.check_values()
    flow = ConstantFlowRate(mfr=5)
    assert flow.check_values()
    flow = ConstantFlowRate(vfr=5)
    assert flow.check_values()


def test_conversion_mass_flow_volume_flow():
    fluid = ConstantFluidData(0.568, 998, 4180, 1e-3)
    flow = ConstantFlowRate(mfr=0.2)
    assert flow.mfr() == 0.2
    assert np.isclose(flow.vfr(fluid), 0.20040080160320642)
    with pytest.raises(ValueError):
        flow.vfr()

    flow = ConstantFlowRate(vfr=0.2)
    assert flow.vfr()
    assert np.isclose(flow.mfr(fluid), 0.2 * 998 / 1000)
    with pytest.raises(ValueError):
        flow.mfr()


def test_flow_rate_borefield_series1():
    bor_mfr = ConstantFlowRate(mfr=1, flow_per_borehole=False)
    bor_vfr = ConstantFlowRate(vfr=1, flow_per_borehole=False)

    with pytest.raises(ValueError):
        bor_mfr.mfr_borehole()
    with pytest.raises(ValueError):
        bor_mfr.vfr_borehole()
    assert np.isclose(bor_mfr.mfr_borehole(nb_of_boreholes=2), 0.5)
    assert np.isclose(bor_mfr.mfr_borehole(nb_of_boreholes=2, series_factor=2), 1)
    assert np.isclose(bor_mfr.mfr_borefield(), 1)
    assert np.isclose(bor_mfr.mfr_borefield(nb_of_boreholes=6), 1)
    assert np.isclose(bor_mfr.mfr_borefield(nb_of_boreholes=6, series_factor=2), 1)

    with pytest.raises(ValueError):
        bor_vfr.vfr_borehole()
    with pytest.raises(ValueError):
        bor_vfr.mfr_borehole()
    with pytest.raises(ValueError):
        bor_vfr.mfr_borefield()
    with pytest.raises(ValueError):
        bor_mfr.vfr_borefield()
    assert np.isclose(bor_vfr.vfr_borehole(nb_of_boreholes=2), 0.5)
    assert np.isclose(bor_vfr.vfr_borehole(nb_of_boreholes=2, series_factor=2), 1)
    assert np.isclose(bor_vfr.vfr_borefield(), 1)
    assert np.isclose(bor_vfr.vfr_borefield(nb_of_boreholes=6), 1)
    assert np.isclose(bor_vfr.vfr_borefield(nb_of_boreholes=6, series_factor=2), 1)


def test_flow_rate_borehole():
    bor_mfr = ConstantFlowRate(mfr=1, flow_per_borehole=True)
    bor_vfr = ConstantFlowRate(vfr=1, flow_per_borehole=True)
    with pytest.raises(ValueError):
        bor_mfr.mfr_borefield()
    with pytest.raises(ValueError):
        bor_vfr.mfr_borefield()
    assert np.isclose(bor_mfr.mfr_borehole(nb_of_boreholes=2), 1)
    assert np.isclose(bor_mfr.mfr_borehole(nb_of_boreholes=2, series_factor=2), 1)
    assert np.isclose(bor_mfr.mfr_borefield(nb_of_boreholes=6), 6)
    assert np.isclose(bor_mfr.mfr_borefield(nb_of_boreholes=6, series_factor=2), 3)

    with pytest.raises(ValueError):
        bor_vfr.vfr_borefield()
    with pytest.raises(ValueError):
        bor_mfr.vfr_borefield()
    assert np.isclose(bor_vfr.vfr_borehole(nb_of_boreholes=2), 1)
    assert np.isclose(bor_vfr.vfr_borehole(nb_of_boreholes=2, series_factor=2), 1)
    assert np.isclose(bor_vfr.vfr_borefield(nb_of_boreholes=6), 6)
    assert np.isclose(bor_vfr.vfr_borefield(nb_of_boreholes=6, series_factor=2), 3)

    bor_mfr = ConstantFlowRate(mfr=1, flow_per_borehole=True, series_factor=2)
    bor_vfr = ConstantFlowRate(vfr=1, flow_per_borehole=True, series_factor=2)
    with pytest.raises(ValueError):
        bor_mfr.mfr_borefield()
    with pytest.raises(ValueError):
        bor_mfr.vfr_borehole()
    with pytest.raises(ValueError):
        bor_vfr.mfr_borehole()
    assert np.isclose(bor_mfr.mfr_borehole(nb_of_boreholes=2), 1)
    assert np.isclose(bor_mfr.mfr_borehole(nb_of_boreholes=2, series_factor=2), 1)
    assert np.isclose(bor_mfr.mfr_borefield(nb_of_boreholes=6), 3)
    assert np.isclose(bor_mfr.mfr_borefield(nb_of_boreholes=6, series_factor=2), 3)

    with pytest.raises(ValueError):
        bor_vfr.vfr_borefield()
    with pytest.raises(ValueError):
        bor_mfr.vfr_borefield()
    assert np.isclose(bor_vfr.vfr_borehole(nb_of_boreholes=2), 1)
    assert np.isclose(bor_vfr.vfr_borehole(nb_of_boreholes=2, series_factor=2), 1)
    assert np.isclose(bor_vfr.vfr_borefield(nb_of_boreholes=6), 3)
    assert np.isclose(bor_vfr.vfr_borefield(nb_of_boreholes=6, series_factor=2), 3)


def test_flow_rate_borefield_series2():
    bor_mfr = ConstantFlowRate(mfr=1, flow_per_borehole=False, series_factor=2)
    bor_vfr = ConstantFlowRate(vfr=1, flow_per_borehole=False, series_factor=2)

    with pytest.raises(ValueError):
        bor_mfr.mfr_borehole()
    assert np.isclose(bor_mfr.mfr_borehole(nb_of_boreholes=2), 1)
    assert np.isclose(bor_mfr.mfr_borehole(nb_of_boreholes=2, series_factor=2), 1)
    assert np.isclose(bor_mfr.mfr_borefield(), 1)
    assert np.isclose(bor_mfr.mfr_borefield(nb_of_boreholes=6), 1)
    assert np.isclose(bor_mfr.mfr_borefield(nb_of_boreholes=6, series_factor=2), 1)

    with pytest.raises(ValueError):
        bor_vfr.vfr_borehole()
    assert np.isclose(bor_vfr.vfr_borehole(nb_of_boreholes=2), 1)
    assert np.isclose(bor_vfr.vfr_borehole(nb_of_boreholes=2, series_factor=2), 1)
    assert np.isclose(bor_vfr.vfr_borefield(), 1)
    assert np.isclose(bor_vfr.vfr_borefield(nb_of_boreholes=6), 1)
    assert np.isclose(bor_vfr.vfr_borefield(nb_of_boreholes=6, series_factor=2), 1)


def test_multiple_temperatures():
    bor_mfr = ConstantFlowRate(mfr=1, flow_per_borehole=False, series_factor=2)
    fluid = TemperatureDependentFluidData('MPG', 20)
    assert np.isclose(bor_mfr.mfr_borefield(nb_of_boreholes=2, fluid_data=fluid, temperature=np.array([2, 3])), 1)
    assert np.allclose(bor_mfr.vfr_borefield(nb_of_boreholes=2, fluid_data=fluid, temperature=np.array([2, 3])),
                       [0.98066981, 0.98086133])


def test_repr_constant_flow_rate():
    fluid = ConstantFlowRate(mfr=0.2)
    assert fluid.__export__() == {'mfr per borehole [kg/s]': 0.2}
    fluid = ConstantFlowRate(vfr=0.2)
    assert fluid.__export__() == {'vfr per borehole [l/s]': 0.2}
    fluid = ConstantFlowRate(mfr=0.2, flow_per_borehole=False, series_factor=2)
    assert fluid.__export__() == {'mfr per borefield [kg/s]': 0.2, 'series factor [-]': 2}
    fluid = ConstantFlowRate(vfr=0.2, flow_per_borehole=False, series_factor=2)
    assert fluid.__export__() == {'vfr per borefield [l/s]': 0.2, 'series factor [-]': 2}


def test_eq():
    fluid = ConstantFlowRate(mfr=0.2)
    fluid2 = ConstantFlowRate(vfr=0.2)
    fluid3 = ConstantFluidData(1, 1, 1, 1)
    fluid4 = ConstantFlowRate(vfr=0.2)

    assert fluid != fluid2
    assert fluid3 != fluid2
    assert fluid2 != fluid3
    assert fluid4 == fluid2

    fluid = VariableHourlyFlowRate(mfr=np.full(8760, 1))
    fluid2 = VariableHourlyFlowRate(vfr=np.full(8760, 1))
    fluid3 = ConstantFluidData(1, 1, 1, 1)
    fluid4 = VariableHourlyFlowRate(vfr=np.full(8760, 1))
    assert fluid != fluid2
    assert fluid3 != fluid2
    assert fluid2 != fluid3
    assert fluid4 == fluid2

    fluid = VariableHourlyMultiyearFlowRate(mfr=np.full(8760, 1))
    fluid2 = VariableHourlyMultiyearFlowRate(vfr=np.full(8760, 1))
    fluid3 = ConstantFluidData(1, 1, 1, 1)
    fluid4 = VariableHourlyMultiyearFlowRate(vfr=np.full(8760, 1))
    assert fluid != fluid2
    assert fluid3 != fluid2
    assert fluid2 != fluid3
    assert fluid4 == fluid2

    fluid = ConstantDeltaTFlowRate(delta_temp_extraction=5, delta_temp_injection=4)
    fluid2 = ConstantDeltaTFlowRate()
    fluid3 = ConstantFluidData(1, 1, 1, 1)
    fluid4 = ConstantDeltaTFlowRate()
    assert fluid != fluid2
    assert fluid3 != fluid2
    assert fluid2 != fluid3
    assert fluid4 == fluid2


def test_variable_hourly_flow_rate():
    fluid = TemperatureDependentFluidData('MPG', 20).create_constant(0)
    with pytest.raises(ValueError):
        VariableHourlyFlowRate(mfr=np.full(8760, 8760), vfr=np.full(8760, 8760))
    with pytest.raises(ValueError):
        VariableHourlyFlowRate(mfr=np.full(8760 * 12, 1))
    with pytest.raises(ValueError):
        VariableHourlyFlowRate(vfr=np.full(8760 * 12, 1))

    # flow per borehole
    flow = VariableHourlyFlowRate(mfr=np.linspace(0, 8760, 8760))
    with pytest.raises(ValueError):
        flow.vfr_borehole()
    with pytest.raises(ValueError):
        flow.vfr_borehole(simulation_period=1)
    with pytest.raises(ValueError):
        flow.vfr_borefield()
    with pytest.raises(ValueError):
        flow.mfr_borefield()
    with pytest.raises(ValueError):
        flow.vfr_borefield(simulation_period=1)
    with pytest.raises(ValueError):
        flow.mfr_borefield(simulation_period=1)
    assert np.allclose(flow.mfr_borehole(simulation_period=2, fluid_data=fluid, nb_of_boreholes=2),
                       np.tile(np.linspace(0, 8760, 8760), 2))
    assert np.allclose(flow.mfr_borefield(simulation_period=2, nb_of_boreholes=2, fluid_data=fluid),
                       np.tile(np.linspace(0, 8760, 8760) * 2, 2))
    assert np.allclose(flow.vfr_borehole(simulation_period=2, fluid_data=fluid, nb_of_boreholes=2),
                       np.tile(np.linspace(0, 8760, 8760) / fluid.rho() * 1000, 2))
    assert np.allclose(flow.vfr_borefield(simulation_period=2, nb_of_boreholes=2, fluid_data=fluid),
                       np.tile(np.linspace(0, 8760, 8760) * 2 / fluid.rho() * 1000, 2))

    flow = VariableHourlyFlowRate(vfr=np.linspace(0, 8760, 8760))
    with pytest.raises(ValueError):
        flow.mfr_borehole()
    with pytest.raises(ValueError):
        flow.mfr_borehole(simulation_period=1)
    with pytest.raises(ValueError):
        flow.vfr_borefield()
    with pytest.raises(ValueError):
        flow.mfr_borefield()
    assert np.allclose(flow.mfr_borehole(simulation_period=2, fluid_data=fluid, nb_of_boreholes=2),
                       np.tile(np.linspace(0, 8760, 8760) / 1000 * fluid.rho(), 2))
    assert np.allclose(flow.mfr_borefield(simulation_period=2, nb_of_boreholes=2, fluid_data=fluid),
                       np.tile(np.linspace(0, 8760, 8760) * 2 / 1000 * fluid.rho(), 2))
    assert np.allclose(flow.vfr_borehole(simulation_period=2, fluid_data=fluid, nb_of_boreholes=2),
                       np.tile(np.linspace(0, 8760, 8760), 2))
    assert np.allclose(flow.vfr_borefield(simulation_period=2, nb_of_boreholes=2, fluid_data=fluid),
                       np.tile(np.linspace(0, 8760, 8760) * 2, 2))

    # flow per borefield
    flow = VariableHourlyFlowRate(mfr=np.linspace(0, 8760, 8760), flow_per_borehole=False)
    with pytest.raises(ValueError):
        flow.mfr_borehole(simulation_period=1, fluid_data=fluid)
    with pytest.raises(ValueError):
        flow.vfr_borehole(simulation_period=1, fluid_data=fluid)
    with pytest.raises(ValueError):
        flow.vfr_borefield(simulation_period=1)
    assert np.allclose(flow.mfr_borehole(simulation_period=2, fluid_data=fluid, nb_of_boreholes=2),
                       np.tile(np.linspace(0, 8760, 8760) / 2, 2))
    assert np.allclose(flow.mfr_borefield(simulation_period=2, nb_of_boreholes=2, fluid_data=fluid),
                       np.tile(np.linspace(0, 8760, 8760), 2))
    assert np.allclose(flow.vfr_borehole(simulation_period=2, fluid_data=fluid, nb_of_boreholes=2),
                       np.tile(np.linspace(0, 8760, 8760) / 2 / fluid.rho() * 1000, 2))
    assert np.allclose(flow.vfr_borefield(simulation_period=2, nb_of_boreholes=2, fluid_data=fluid),
                       np.tile(np.linspace(0, 8760, 8760) / fluid.rho() * 1000, 2))

    flow = VariableHourlyFlowRate(vfr=np.linspace(0, 8760, 8760), flow_per_borehole=False)
    with pytest.raises(ValueError):
        flow.mfr_borehole(simulation_period=1, fluid_data=fluid)
    with pytest.raises(ValueError):
        flow.vfr_borehole(simulation_period=1, fluid_data=fluid)
    with pytest.raises(ValueError):
        flow.mfr_borefield(simulation_period=1)
    assert np.allclose(flow.mfr_borehole(simulation_period=2, fluid_data=fluid, nb_of_boreholes=2),
                       np.tile(np.linspace(0, 8760, 8760) / 2 / 1000 * fluid.rho(), 2))
    assert np.allclose(flow.mfr_borefield(simulation_period=2, nb_of_boreholes=2, fluid_data=fluid),
                       np.tile(np.linspace(0, 8760, 8760) / 1000 * fluid.rho(), 2))
    assert np.allclose(flow.vfr_borehole(simulation_period=2, fluid_data=fluid, nb_of_boreholes=2),
                       np.tile(np.linspace(0, 8760, 8760) / 2, 2))
    assert np.allclose(flow.vfr_borefield(simulation_period=2, nb_of_boreholes=2, fluid_data=fluid),
                       np.tile(np.linspace(0, 8760, 8760), 2))


def test_variable_hourly_multiyear_flow_rate():
    fluid = TemperatureDependentFluidData('MPG', 20).create_constant(0)
    with pytest.raises(ValueError):
        VariableHourlyMultiyearFlowRate(mfr=np.full(8760, 8760), vfr=np.full(8760, 8760))
    with pytest.raises(ValueError):
        VariableHourlyMultiyearFlowRate(mfr=np.full(8760 * 12 - 1, 1))
    with pytest.raises(ValueError):
        VariableHourlyMultiyearFlowRate(vfr=np.full(8760 * 12 - 1, 1))

    # flow per borehole
    flow = VariableHourlyMultiyearFlowRate(mfr=np.tile(np.linspace(0, 8760, 8760), 2))
    with pytest.raises(ValueError):
        flow.vfr_borehole()
    with pytest.raises(ValueError):
        flow.vfr_borefield()
    with pytest.raises(ValueError):
        flow.mfr_borefield()
    assert np.allclose(flow.mfr_borehole(fluid_data=fluid, nb_of_boreholes=2),
                       np.tile(np.linspace(0, 8760, 8760), 2))
    assert np.allclose(flow.mfr_borefield(nb_of_boreholes=2, fluid_data=fluid),
                       np.tile(np.linspace(0, 8760, 8760) * 2, 2))
    assert np.allclose(flow.vfr_borehole(fluid_data=fluid, nb_of_boreholes=2),
                       np.tile(np.linspace(0, 8760, 8760) / fluid.rho() * 1000, 2))
    assert np.allclose(flow.vfr_borefield(nb_of_boreholes=2, fluid_data=fluid),
                       np.tile(np.linspace(0, 8760, 8760) * 2 / fluid.rho() * 1000, 2))

    flow = VariableHourlyMultiyearFlowRate(vfr=np.tile(np.linspace(0, 8760, 8760), 2))
    with pytest.raises(ValueError):
        flow.mfr_borehole()
    with pytest.raises(ValueError):
        flow.vfr_borefield()
    with pytest.raises(ValueError):
        flow.mfr_borefield()
    assert np.allclose(flow.mfr_borehole(fluid_data=fluid, nb_of_boreholes=2),
                       np.tile(np.linspace(0, 8760, 8760) / 1000 * fluid.rho(), 2))
    assert np.allclose(flow.mfr_borefield(nb_of_boreholes=2, fluid_data=fluid),
                       np.tile(np.linspace(0, 8760, 8760) * 2 / 1000 * fluid.rho(), 2))
    assert np.allclose(flow.vfr_borehole(fluid_data=fluid, nb_of_boreholes=2),
                       np.tile(np.linspace(0, 8760, 8760), 2))
    assert np.allclose(flow.vfr_borefield(nb_of_boreholes=2, fluid_data=fluid),
                       np.tile(np.linspace(0, 8760, 8760) * 2, 2))

    # flow per borefield
    flow = VariableHourlyMultiyearFlowRate(mfr=np.tile(np.linspace(0, 8760, 8760), 2), flow_per_borehole=False)
    with pytest.raises(ValueError):
        flow.mfr_borehole(fluid_data=fluid)
    with pytest.raises(ValueError):
        flow.vfr_borehole(fluid_data=fluid)
    with pytest.raises(ValueError):
        flow.vfr_borefield()
    assert np.allclose(flow.mfr_borehole(fluid_data=fluid, nb_of_boreholes=2),
                       np.tile(np.linspace(0, 8760, 8760) / 2, 2))
    assert np.allclose(flow.mfr_borefield(nb_of_boreholes=2, fluid_data=fluid),
                       np.tile(np.linspace(0, 8760, 8760), 2))
    assert np.allclose(flow.vfr_borehole(fluid_data=fluid, nb_of_boreholes=2),
                       np.tile(np.linspace(0, 8760, 8760) / 2 / fluid.rho() * 1000, 2))
    assert np.allclose(flow.vfr_borefield(nb_of_boreholes=2, fluid_data=fluid),
                       np.tile(np.linspace(0, 8760, 8760) / fluid.rho() * 1000, 2))

    flow = VariableHourlyMultiyearFlowRate(vfr=np.tile(np.linspace(0, 8760, 8760), 2), flow_per_borehole=False)
    with pytest.raises(ValueError):
        flow.mfr_borehole(fluid_data=fluid)
    with pytest.raises(ValueError):
        flow.vfr_borehole(fluid_data=fluid)
    with pytest.raises(ValueError):
        flow.mfr_borefield()
    assert np.allclose(flow.mfr_borehole(fluid_data=fluid, nb_of_boreholes=2),
                       np.tile(np.linspace(0, 8760, 8760) / 2 / 1000 * fluid.rho(), 2))
    assert np.allclose(flow.mfr_borefield(nb_of_boreholes=2, fluid_data=fluid),
                       np.tile(np.linspace(0, 8760, 8760) / 1000 * fluid.rho(), 2))
    assert np.allclose(flow.vfr_borehole(fluid_data=fluid, nb_of_boreholes=2),
                       np.tile(np.linspace(0, 8760, 8760) / 2, 2))
    assert np.allclose(flow.vfr_borefield(nb_of_boreholes=2, fluid_data=fluid),
                       np.tile(np.linspace(0, 8760, 8760), 2))


def test_constant_delta_t_flow_rate():
    with pytest.raises(ValueError):
        ConstantDeltaTFlowRate(delta_temp_extraction=0)
    with pytest.raises(ValueError):
        ConstantDeltaTFlowRate(delta_temp_extraction=0)
    with pytest.raises(ValueError):
        ConstantDeltaTFlowRate(series_factor=0)

    flow = ConstantDeltaTFlowRate(delta_temp_extraction=4, delta_temp_injection=5)
    fluid = ConstantFluidData(0.5, 2000, 4000, 1e-3)
    with pytest.raises(ValueError):
        flow.mfr_borehole()
    with pytest.raises(ValueError):
        flow.mfr_borehole(nb_of_boreholes=2)
    with pytest.raises(ValueError):
        flow.mfr_borehole(nb_of_boreholes=2, fluid_data=fluid)

    assert np.isclose(flow.mfr_borefield(fluid_data=fluid, power=1), 1 / 4 / 4)
    assert np.isclose(flow.mfr_borefield(fluid_data=fluid, power=-1), 1 / 4 / 5)
    assert np.allclose(
        flow.mfr_borefield(fluid_data=fluid, power=np.array([1, -1]), nb_of_boreholes=2, series_factor=2),
        [1 / 4 / 4, 1 / 4 / 5])
    assert np.allclose(
        flow.vfr_borefield(fluid_data=fluid, power=np.array([1, -1]), nb_of_boreholes=2, series_factor=2),
        np.array([1 / 4 / 4, 1 / 4 / 5]) / 2000 * 1000)
    assert np.allclose(flow.mfr_borehole(fluid_data=fluid, power=np.array([1, -1]), nb_of_boreholes=2),
                       np.array([1 / 4 / 4, 1 / 4 / 5]) / 2)
    assert np.allclose(flow.vfr_borehole(fluid_data=fluid, power=np.array([1, -1]), nb_of_boreholes=2),
                       np.array([1 / 4 / 4, 1 / 4 / 5]) / 2000 * 1000 / 2)
    assert np.allclose(flow.mfr_borehole(fluid_data=fluid, power=np.array([1, -1]), nb_of_boreholes=2, series_factor=2),
                       np.array([1 / 4 / 4, 1 / 4 / 5]))
    assert np.allclose(flow.vfr_borehole(fluid_data=fluid, power=np.array([1, -1]), nb_of_boreholes=2, series_factor=2),
                       np.array([1 / 4 / 4, 1 / 4 / 5]) / 2000 * 1000)
    flow = ConstantDeltaTFlowRate(delta_temp_extraction=4, delta_temp_injection=5, series_factor=2)
    assert np.allclose(flow.mfr_borehole(fluid_data=fluid, power=np.array([1, -1]), nb_of_boreholes=2),
                       np.array([1 / 4 / 4, 1 / 4 / 5]))
    assert np.allclose(flow.vfr_borehole(fluid_data=fluid, power=np.array([1, -1]), nb_of_boreholes=2),
                       np.array([1 / 4 / 4, 1 / 4 / 5]) / 2000 * 1000)


def test_repr_constant_hourly_flow_rate():
    flow = VariableHourlyFlowRate(mfr=np.linspace(0, 8760, 8760))
    assert flow.__export__() == {'type': 'Hourly mfr per borehole [kg/s]'}
    flow = VariableHourlyFlowRate(vfr=np.linspace(0, 8760, 8760))
    assert flow.__export__() == {'type': 'Hourly vfr per borehole [l/s]'}
    flow = VariableHourlyFlowRate(mfr=np.linspace(0, 8760, 8760), flow_per_borehole=False, series_factor=2)
    assert flow.__export__() == {'type': 'Hourly mfr per borefield [kg/s]', 'series factor [-]': 2}
    flow = VariableHourlyFlowRate(vfr=np.linspace(0, 8760, 8760), flow_per_borehole=False, series_factor=2)
    assert flow.__export__() == {'type': 'Hourly vfr per borefield [l/s]', 'series factor [-]': 2}


def test_repr_constant_hourly_multiyear_flow_rate():
    flow = VariableHourlyMultiyearFlowRate(mfr=np.linspace(0, 8760, 8760))
    assert flow.__export__() == {'type': 'Hourly multiyear mfr per borehole [kg/s]'}
    flow = VariableHourlyMultiyearFlowRate(vfr=np.linspace(0, 8760, 8760))
    assert flow.__export__() == {'type': 'Hourly multiyear vfr per borehole [l/s]'}
    flow = VariableHourlyMultiyearFlowRate(mfr=np.linspace(0, 8760, 8760), flow_per_borehole=False, series_factor=2)
    assert flow.__export__() == {'type': 'Hourly multiyear mfr per borefield [kg/s]', 'series factor [-]': 2}
    flow = VariableHourlyMultiyearFlowRate(vfr=np.linspace(0, 8760, 8760), flow_per_borehole=False, series_factor=2)
    assert flow.__export__() == {'type': 'Hourly multiyear vfr per borefield [l/s]', 'series factor [-]': 2}


def test_repr_constant_delta_temp_flow_rate():
    flow = ConstantDeltaTFlowRate(delta_temp_extraction=5, delta_temp_injection=6, series_factor=2)
    assert flow.__export__() == {'delta T in cooling': 6,
                                 'delta T in heating': 5,
                                 'series factor': 2,
                                 'type': 'Constant delta T flow rate'}
