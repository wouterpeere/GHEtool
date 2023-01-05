import pytest
import numpy as np

from GHEtool import *
from GHEtool.VariableClasses.BaseClass import BaseClassVariables


class TestClass(BaseClassVariables):

    def __init__(self):
        self.test_string = "test"
        self.test_int = 12
        self.test_float = 12.5
        self.test_tuple = (12, 13, 14)
        self.test_list = [14, 13, 12]
        self.test_numpy = np.array([15, 18, 16])
        self.test_set = set([12, 14, 16])
        self.test_dictionary = {"a": 1, "b": 2}
        self.test_variable_class = GroundData(1, 2, 3)

    def clear(self):
        self.test_string = None
        self.test_int = None
        self.test_float = None
        self.test_tuple = None
        self.test_list = None
        self.test_numpy = None
        self.test_set = None
        self.test_dictionary = None
        self.test_variable_class = GroundData()


class TestClassesWithSlots(BaseClassVariables):

    __slots__ = 'test_string', 'test_int', 'test_float', 'test_tuple', 'test_list', 'test_numpy',\
                'test_set', 'test_dictionary', 'test_variable_class'

    def __init__(self):
        self.test_string = "test"
        self.test_int = 12
        self.test_float = 12.5
        self.test_tuple = (12, 13, 14)
        self.test_list = [14, 13, 12]
        self.test_numpy = np.array([15, 18, 16])
        self.test_set = set([12, 14, 16])
        self.test_dictionary = {"a": 1, "b": 2}
        self.test_variable_class = GroundData(1, 2, 3)


def test_without_slots():
    test_class = TestClass()
    dictionary = test_class.__to_dict__()
    assert dictionary["test_string"] == 'test'
    assert dictionary["test_int"] == 12
    assert dictionary["test_float"] == 12.5
    assert dictionary["test_tuple"] == {'value': [12, 13, 14], 'type': 'tuple'}
    assert dictionary["test_list"] == [14, 13, 12]
    assert dictionary["test_set"] == {'value': [16, 12, 14], 'type': 'set'}
    assert dictionary["test_numpy"] == {'value': [15, 18, 16], 'type': 'np.ndarray'}
    assert dictionary["test_dictionary"] == {"a": 1, "b": 2}
    assert dictionary["test_variable_class"] == {'k_s': 1, 'Tg': 2, 'Rb': 3, 'flux': 0.06,
                                                 'volumetric_heat_capacity': 2400000.0,
                                                 'alpha': 4.1666666666666667e-07}

    test_class2 = TestClass()
    test_class2.clear()
    test_class2.__from_dict__(dictionary)
    dictionary = test_class2.__to_dict__()
    assert dictionary["test_string"] == 'test'
    assert dictionary["test_int"] == 12
    assert dictionary["test_float"] == 12.5
    assert dictionary["test_tuple"] == {'value': [12, 13, 14], 'type': 'tuple'}
    assert dictionary["test_list"] == [14, 13, 12]
    assert dictionary["test_set"] == {'value': [16, 12, 14], 'type': 'set'}
    assert dictionary["test_numpy"] == {'value': [15, 18, 16], 'type': 'np.ndarray'}
    assert dictionary["test_dictionary"] == {"a": 1, "b": 2}
    assert dictionary["test_variable_class"] == {'k_s': 1, 'Tg': 2, 'Rb': 3, 'flux': 0.06,
                                                 'volumetric_heat_capacity': 2400000.0,
                                                 'alpha': 4.1666666666666667e-07}


def test_with_slots():
    test_class = TestClass()
    dictionary = test_class.__to_dict__()
    assert dictionary["test_string"] == 'test'
    assert dictionary["test_int"] == 12
    assert dictionary["test_float"] == 12.5
    assert dictionary["test_tuple"] == {'value': [12, 13, 14], 'type': 'tuple'}
    assert dictionary["test_list"] == [14, 13, 12]
    assert dictionary["test_set"] == {'value': [16, 12, 14], 'type': 'set'}
    assert dictionary["test_numpy"] == {'value': [15, 18, 16], 'type': 'np.ndarray'}
    assert dictionary["test_dictionary"] == {"a": 1, "b": 2}
    assert dictionary["test_variable_class"] == {'k_s': 1, 'Tg': 2, 'Rb': 3, 'flux': 0.06,
                                                 'volumetric_heat_capacity': 2400000.0,
                                                 'alpha': 4.1666666666666667e-07}

    test_class2 = TestClass()
    test_class2.clear()
    test_class2.__from_dict__(dictionary)
    dictionary = test_class2.__to_dict__()
    assert dictionary["test_string"] == 'test'
    assert dictionary["test_int"] == 12
    assert dictionary["test_float"] == 12.5
    assert dictionary["test_tuple"] == {'value': [12, 13, 14], 'type': 'tuple'}
    assert dictionary["test_list"] == [14, 13, 12]
    assert dictionary["test_set"] == {'value': [16, 12, 14], 'type': 'set'}
    assert dictionary["test_numpy"] == {'value': [15, 18, 16], 'type': 'np.ndarray'}
    assert dictionary["test_dictionary"] == {"a": 1, "b": 2}
    assert dictionary["test_variable_class"] == {'k_s': 1, 'Tg': 2, 'Rb': 3, 'flux': 0.06,
                                                 'volumetric_heat_capacity': 2400000.0,
                                                 'alpha': 4.1666666666666667e-07}

