import numpy as np
import pygfunction as gt

from GHEtool import *
from GHEtool.VariableClasses.BaseClass import BaseClass


class TestClass(BaseClass):

    def __init__(self):
        self.test_string = "test"
        self.test_int = 12
        self.test_float = 12.5
        self.test_bool = True
        self.test_none = None
        self.test_tuple = (12, 13, 14)
        self.test_list = [14, 13, 12]
        self.test_numpy = np.array([15, 18, 16])
        self.test_set = {12, 14, 16}
        self.test_dictionary = {"a": 1, "b": 2}
        self.test_variable_class = GroundConstantTemperature(1, 2)
        self.test_pygfunction = gt.boreholes.rectangle_field(2, 1, 6, 6, 100, 4, 0.075)

    def clear(self):
        self.test_string = None
        self.test_int = None
        self.test_float = None
        self.test_tuple = None
        self.test_bool = None
        self.test_none = 0
        self.test_list = None
        self.test_numpy = None
        self.test_set = None
        self.test_dictionary = None
        self.test_variable_class = GroundConstantTemperature()
        self.test_pygfunction = None


class TestClassesWithSlots(BaseClass):
    __slots__ = 'test_string', 'test_int', 'test_float', 'test_tuple', 'test_list', 'test_numpy', "test_none", \
        'test_set', 'test_dictionary', 'test_variable_class', 'test_pygfunction', 'test_bool'

    def __init__(self):
        self.test_string = "test"
        self.test_int = 12
        self.test_float = 12.5
        self.test_bool = True
        self.test_none = None
        self.test_tuple = (12, 13, 14)
        self.test_list = [14, 13, 12]
        self.test_numpy = np.array([15, 18, 16])
        self.test_set = {12, 14, 16}
        self.test_dictionary = {"a": 1, "b": 2}
        self.test_variable_class = GroundConstantTemperature(1, 2)
        self.test_pygfunction = gt.boreholes.rectangle_field(2, 1, 6, 6, 100, 4, 0.075)

    def clear(self):
        self.test_string = None
        self.test_int = None
        self.test_float = None
        self.test_tuple = None
        self.test_bool = None
        self.test_none = 0
        self.test_list = None
        self.test_numpy = None
        self.test_set = None
        self.test_dictionary = None
        self.test_variable_class = GroundConstantTemperature()
        self.test_pygfunction = None


def test_without_slots():
    test_class2 = TestClass()
    test_class2.clear()
    assert not test_class2.check_values()


def test_with_slots():
    test_class2 = TestClassesWithSlots()
    test_class2.clear()
    assert not test_class2.check_values()
