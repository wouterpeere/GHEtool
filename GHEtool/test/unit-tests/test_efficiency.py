"""
This file contains the test for the efficiency data
"""
import pytest

from GHEtool.VariableClasses.Efficiency import *


def test_SCOP():
    scop = SCOP(50)
    assert scop.get_SCOP(12, test=5) == 50
    assert scop.get_COP(12, test=5) == 50
    with pytest.raises(ValueError):
        SCOP(0)


def test_SEER():
    seer = SEER(50)
    assert seer.get_SEER(12, test=5) == 50
    assert seer.get_EER(12, test=5) == 50
    with pytest.raises(ValueError):
        SEER(0)
