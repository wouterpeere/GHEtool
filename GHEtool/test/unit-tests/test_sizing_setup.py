import pytest

from GHEtool import *


def test_initialising_setups():
    test = SizingSetup()
    test.L2_sizing = True
    assert test.L2_sizing
    assert not test.L3_sizing
    assert not test.L4_sizing
    test.L3_sizing = True
    assert test.L3_sizing
    assert not test.L2_sizing
    assert not test.L4_sizing
    test.L4_sizing = True
    assert test.L4_sizing
    assert not test.L3_sizing
    assert not test.L2_sizing


def test_no_backup():
    test = SizingSetup()
    try:
        test.restore_backup()
    except ValueError:
        assert True


def test_backup_functionality():
    test = SizingSetup()
    test.make_backup()
    test.L3_sizing = True
    assert test.L2_sizing is False
    assert test._backup.L2_sizing is True
    test.restore_backup()
    assert test.L2_sizing is True
    assert test.L3_sizing is False


def test_properties():
    test = SizingSetup()
    assert test.L2_sizing == test._L2_sizing
    assert test.L3_sizing == test._L3_sizing
    assert test.L4_sizing == test._L4_sizing


def test_update_variables():
    test = SizingSetup()
    assert test.use_constant_Rb
    test.update_variables(use_constant_Rb=False)
    assert not test.use_constant_Rb


def test_more_than_one_option():
    test = SizingSetup()
    try:
        test._check_and_set_sizing(True, True, False)
        assert False     # pragma: no cover
    except ValueError:
        assert True
