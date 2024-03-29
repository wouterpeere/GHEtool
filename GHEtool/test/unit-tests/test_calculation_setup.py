import pytest

from GHEtool import *


def test_initialising_setups():
    test = CalculationSetup()
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
    test = CalculationSetup()
    with pytest.raises(ValueError):
        test.restore_backup()


def test_backup_functionality():
    test = CalculationSetup()
    test.make_backup()
    test.L3_sizing = True
    assert test.L2_sizing is False
    assert test._backup.L2_sizing is True
    test.restore_backup()
    assert test.L2_sizing is True
    assert test.L3_sizing is False


def test_properties():
    test = CalculationSetup()
    assert test.L2_sizing == test._L2_sizing
    assert test.L3_sizing == test._L3_sizing
    assert test.L4_sizing == test._L4_sizing


def test_update_variables():
    test = CalculationSetup()
    assert test.quadrant_sizing == 0
    test.update_variables(quadrant_sizing=1)
    assert test.quadrant_sizing == 1


def test_more_than_one_option():
    test = CalculationSetup()
    with pytest.raises(ValueError):
        test._check_and_set_sizing(True, True, False)
    with pytest.raises(ValueError):
        test._check_and_set_sizing(False, True, True)
    with pytest.raises(ValueError):
        test._check_and_set_sizing(True, False, True)


def test_error_quadrant():
    with pytest.raises(ValueError):
        CalculationSetup(quadrant_sizing=5)
    CalculationSetup(quadrant_sizing=0)


def test_equal_unequal():
    setup1 = CalculationSetup(2, False, True, False)
    setup2 = CalculationSetup(2, False, True, False)
    setup3 = CalculationSetup(2, True, False, False)
    assert setup1 == setup2
    assert not setup2 == setup3
    assert not setup2 == Borefield()


def test_assign_incorrect_variable():
    setup = CalculationSetup()
    with pytest.raises(ValueError):
        setup.update_variables(test='test')
