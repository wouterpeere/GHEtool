"""
This document contains the TestMethodClass used for testing the GHEtool methods.
"""
from GHEtool import Borefield
from typing import List
import copy


class TestObject:

    def __init__(self, borefield, L2_output=None, L3_output=None, L4_output=None,
                 quadrant: int = None, error=None, name: str = ""):
        self.borefield: Borefield = copy.deepcopy(borefield)
        self.L2_output = L2_output
        self.L3_output = L3_output
        self.L4_output = L4_output
        self.quadrant = quadrant
        self.error = error
        self.name = name


class TestMethodClass():

    def __init__(self):
        self.list_of_test_objects: List[TestObject] = []

    def add(self, object: TestObject) -> None:
        self.list_of_test_objects.append(object)

    @property
    def names(self) -> list:
        return [i.name if i.name != '' else f'case {_}' for _, i in enumerate(self.list_of_test_objects)]

    @property
    def L2_sizing_input(self) -> list:
        return [i.borefield for _, i in enumerate(self.list_of_test_objects)
                if i.L2_output is not None or i.error is not None]

    @property
    def L2_sizing_output(self) -> list:
        return [(i.L2_output if i.L2_output is not None else i.error, i.quadrant)
                for _, i in enumerate(self.list_of_test_objects)
                if i.L2_output is not None or i.error is not None]

    @property
    def L3_sizing_input(self) -> list:
        return [i.borefield for _, i in enumerate(self.list_of_test_objects)
                if i.L3_output is not None or i.error is not None]

    @property
    def L3_sizing_output(self) -> list:
        return [(i.L3_output if i.L3_output is not None else i.error, i.quadrant)
                for _, i in enumerate(self.list_of_test_objects)
                if i.L3_output is not None or i.error is not None]

    @property
    def L4_sizing(self) -> list:
        pass
