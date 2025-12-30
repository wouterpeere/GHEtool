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
