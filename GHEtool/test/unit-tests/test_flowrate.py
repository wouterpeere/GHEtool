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


def test_repr_constant_flow_rate():
    fluid = ConstantFlowRate(mfr=0.2)
    assert fluid.__repr__() == {'mfr': 0.2}
    fluid = ConstantFlowRate(vfr=0.2)
    assert fluid.__repr__() == {'vfr': 0.2}


def test_eq():
    fluid = ConstantFlowRate(mfr=0.2)
    fluid2 = ConstantFlowRate(vfr=0.2)
    fluid3 = ConstantFluidData(1, 1, 1, 1)
    fluid4 = ConstantFlowRate(vfr=0.2)

    assert fluid != fluid2
    assert fluid3 != fluid2
    assert fluid4 == fluid2
