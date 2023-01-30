# import pytest
import numpy as np
import pygfunction as gt
import json

from GHEtool import *
from GHEtool.VariableClasses.BaseClass import BaseClass


class TestClass(BaseClass):

    def __init__(self):
        self.test_string = "test"
        self.test_int = 12
        self.test_float = 12.5
        self.test_bool = True
        self.test_tuple = (12, 13, 14)
        self.test_list = [14, 13, 12]
        self.test_numpy = np.array([15, 18, 16])
        self.test_set = set([12, 14, 16])
        self.test_dictionary = {"a": 1, "b": 2}
        self.test_variable_class = GroundData(1, 2, 3)
        self.test_pygfunction = gt.boreholes.rectangle_field(2, 1, 6, 6, 100, 4, 0.075)

    def clear(self):
        self.test_string = None
        self.test_int = None
        self.test_float = None
        self.test_tuple = None
        self.test_bool = None
        self.test_list = None
        self.test_numpy = None
        self.test_set = None
        self.test_dictionary = None
        self.test_variable_class = GroundData()
        self.test_pygfunction = None


class TestClassesWithSlots(BaseClass):

    __slots__ = 'test_string', 'test_int', 'test_float', 'test_tuple', 'test_list', 'test_numpy',\
                'test_set', 'test_dictionary', 'test_variable_class', 'test_pygfunction', 'test_bool'

    def __init__(self):
        self.test_string = "test"
        self.test_int = 12
        self.test_float = 12.5
        self.test_bool = True
        self.test_tuple = (12, 13, 14)
        self.test_list = [14, 13, 12]
        self.test_numpy = np.array([15, 18, 16])
        self.test_set = set([12, 14, 16])
        self.test_dictionary = {"a": 1, "b": 2}
        self.test_variable_class = GroundData(1, 2, 3)
        self.test_pygfunction = gt.boreholes.rectangle_field(2, 1, 6, 6, 100, 4, 0.075)

    def clear(self):
        self.test_string = None
        self.test_int = None
        self.test_float = None
        self.test_tuple = None
        self.test_bool = None
        self.test_list = None
        self.test_numpy = None
        self.test_set = None
        self.test_dictionary = None
        self.test_variable_class = GroundData()
        self.test_pygfunction = None


def test_without_slots():
    test_class = TestClass()
    dictionary = test_class._to_dict()
    assert dictionary["test_string"] == 'test'
    assert dictionary["test_int"] == 12
    assert dictionary["test_float"] == 12.5
    assert dictionary["test_bool"]
    assert dictionary["test_tuple"] == {'value': [12, 13, 14], 'type': 'tuple'}
    assert dictionary["test_list"] == [14, 13, 12]
    assert dictionary["test_set"] == {'value': [16, 12, 14], 'type': 'set'}
    assert dictionary["test_numpy"] == {'value': [15, 18, 16], 'type': 'np.ndarray'}
    assert dictionary["test_dictionary"] == {"a": 1, "b": 2}
    assert dictionary["test_variable_class"] == {'k_s': 1, 'Tg': 2, 'Rb': 3, 'flux': 0.06,
                                                 'volumetric_heat_capacity': 2400000.0,
                                                 'alpha': 4.1666666666666667e-07}
    assert dictionary["test_pygfunction"] == {'value': [{'H': 100.0, 'D': 4.0, 'r_b': 0.075, 'x': 0.0, 'y': 0.0,
                                                        'tilt': 0.0, 'orientation': 3.141592653589793},
                                                       {'H': 100.0, 'D': 4.0, 'r_b': 0.075,
                                                        'x': 6.0, 'y': 0.0, 'tilt': 0.0, 'orientation': 0.0}],
                                              'type': 'pygfunction.Borehole'}

    test_class2 = TestClass()
    test_class2.clear()
    assert not test_class2.check_values()
    test_class2._from_dict(dictionary)
    dictionary = test_class2._to_dict()
    assert isinstance(test_class2.test_pygfunction[0], gt.boreholes.Borehole)
    assert isinstance(test_class2.test_tuple, tuple)
    assert isinstance(test_class2.test_list, list)
    assert isinstance(test_class2.test_set, set)
    assert isinstance(test_class2.test_numpy, np.ndarray)
    assert dictionary["test_string"] == 'test'
    assert dictionary["test_int"] == 12
    assert dictionary["test_float"] == 12.5
    assert dictionary["test_bool"]
    assert dictionary["test_tuple"] == {'value': [12, 13, 14], 'type': 'tuple'}
    assert dictionary["test_list"] == [14, 13, 12]
    assert dictionary["test_set"] == {'value': [16, 12, 14], 'type': 'set'}
    assert dictionary["test_numpy"] == {'value': [15, 18, 16], 'type': 'np.ndarray'}
    assert dictionary["test_dictionary"] == {"a": 1, "b": 2}
    assert dictionary["test_variable_class"] == {'k_s': 1, 'Tg': 2, 'Rb': 3, 'flux': 0.06,
                                                 'volumetric_heat_capacity': 2400000.0,
                                                 'alpha': 4.1666666666666667e-07}
    assert dictionary["test_pygfunction"] == {'value': [{'H': 100.0, 'D': 4.0, 'r_b': 0.075, 'x': 0.0, 'y': 0.0,
                                                        'tilt': 0.0, 'orientation': 3.141592653589793},
                                                       {'H': 100.0, 'D': 4.0, 'r_b': 0.075,
                                                        'x': 6.0, 'y': 0.0, 'tilt': 0.0, 'orientation': 0.0}], 'type': 'pygfunction.Borehole'}


def test_with_slots():
    test_class = TestClassesWithSlots()
    dictionary = test_class._to_dict()
    assert dictionary["test_string"] == 'test'
    assert dictionary["test_int"] == 12
    assert dictionary["test_float"] == 12.5
    assert dictionary["test_bool"]
    assert dictionary["test_tuple"] == {'value': [12, 13, 14], 'type': 'tuple'}
    assert dictionary["test_list"] == [14, 13, 12]
    assert dictionary["test_set"] == {'value': [16, 12, 14], 'type': 'set'}
    assert dictionary["test_numpy"] == {'value': [15, 18, 16], 'type': 'np.ndarray'}
    assert dictionary["test_dictionary"] == {"a": 1, "b": 2}
    assert dictionary["test_variable_class"] == {'k_s': 1, 'Tg': 2, 'Rb': 3, 'flux': 0.06,
                                                 'volumetric_heat_capacity': 2400000.0,
                                                 'alpha': 4.1666666666666667e-07}
    assert dictionary["test_pygfunction"] == {'value': [{'H': 100.0, 'D': 4.0, 'r_b': 0.075, 'x': 0.0, 'y': 0.0,
                                                        'tilt': 0.0, 'orientation': 3.141592653589793},
                                                       {'H': 100.0, 'D': 4.0, 'r_b': 0.075,
                                                        'x': 6.0, 'y': 0.0, 'tilt': 0.0, 'orientation': 0.0}], 'type': 'pygfunction.Borehole'}

    test_class2 = TestClassesWithSlots()
    test_class2.clear()
    assert not test_class2.check_values()
    test_class2._from_dict(dictionary)
    dictionary = test_class2._to_dict()
    assert isinstance(test_class2.test_pygfunction[0], gt.boreholes.Borehole)
    assert isinstance(test_class2.test_tuple, tuple)
    assert isinstance(test_class2.test_list, list)
    assert isinstance(test_class2.test_set, set)
    assert isinstance(test_class2.test_numpy, np.ndarray)
    assert dictionary["test_string"] == 'test'
    assert dictionary["test_int"] == 12
    assert dictionary["test_float"] == 12.5
    assert dictionary["test_bool"]
    assert dictionary["test_tuple"] == {'value': [12, 13, 14], 'type': 'tuple'}
    assert dictionary["test_list"] == [14, 13, 12]
    assert dictionary["test_set"] == {'value': [16, 12, 14], 'type': 'set'}
    assert dictionary["test_numpy"] == {'value': [15, 18, 16], 'type': 'np.ndarray'}
    assert dictionary["test_dictionary"] == {"a": 1, "b": 2}
    assert dictionary["test_variable_class"] == {'k_s': 1, 'Tg': 2, 'Rb': 3, 'flux': 0.06,
                                                 'volumetric_heat_capacity': 2400000.0,
                                                 'alpha': 4.1666666666666667e-07}
    assert dictionary["test_pygfunction"] == {'value': [{'H': 100.0, 'D': 4.0, 'r_b': 0.075, 'x': 0.0, 'y': 0.0,
                                                        'tilt': 0.0, 'orientation': 3.141592653589793},
                                                       {'H': 100.0, 'D': 4.0, 'r_b': 0.075,
                                                        'x': 6.0, 'y': 0.0, 'tilt': 0.0, 'orientation': 0.0}], 'type': 'pygfunction.Borehole'}


def test_json_dump():
    test_class = TestClass()
    json.dump(test_class._to_dict(), open('test.json', 'w'))

test_with_slots()