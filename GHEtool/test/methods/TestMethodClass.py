"""
This document contains the TestMethodClass used for testing the GHEtool methods.
"""
from GHEtool import Borefield
from typing import List
import copy

import numpy as np


class SizingObject:

    def __init__(self, borefield, L2_output=None, L3_output=None, L4_output=None,
                 quadrant: int = None, error_L2=None, error_L3=None, error_L4=None, name: str = ""):
        self.borefield: Borefield = copy.deepcopy(borefield)
        self.L2_output = L2_output
        self.L3_output = L3_output
        self.L4_output = L4_output
        self.quadrant = quadrant
        self.error_L2 = error_L2
        self.error_L3 = error_L3
        self.error_L4 = error_L4
        self.name = name


class OptimiseLoadProfileObject:

    def __init__(self, borefield: Borefield, load, depth: float, SCOP: float, SEER: float, percentage_extraction: float,
                 percentage_injection: float, peak_extraction_geo: float, peak_injection_geo: float,
                 peak_extraction_ext: float,
                 peak_injection_ext: float, name: str = "", power: bool = True, hourly: bool = True,
                 max_peak_extraction: float = None,
                 max_peak_injection: float = None):
        self.borefield = copy.deepcopy(borefield)
        self.load = copy.deepcopy(load)
        self.depth = depth
        self.SCOP = SCOP
        self.SEER = SEER
        self.percentage_extraction = percentage_extraction
        self.percentage_injection = percentage_injection
        self.peak_extraction_geo = peak_extraction_geo
        self.peak_injection_geo = peak_injection_geo
        self.peak_extraction_ext = peak_extraction_ext
        self.peak_injection_ext = peak_injection_ext
        self.name = name
        self.power = power
        self.hourly = hourly
        self.max_peak_extraction = max_peak_extraction
        self.max_peak_injection = max_peak_injection

    def test(self):  # pragma: no cover
        self.borefield.optimise_load_profile(self.load, self.depth, self.SCOP, self.SEER)
        assert np.isclose(self.borefield._percentage_extraction, self.percentage_extraction)
        assert np.isclose(self.borefield._percentage_injection, self.percentage_injection)
        assert np.isclose(self.borefield.load.max_peak_extraction, self.peak_extraction_geo)
        assert np.isclose(self.borefield.load.max_peak_injection, self.peak_injection_geo)
        assert np.isclose(self.borefield._external_load.max_peak_extraction, self.peak_extraction_ext)
        assert np.isclose(self.borefield._external_load.max_peak_injection, self.peak_injection_ext)


class TestMethodClass():

    def __init__(self):
        self.list_of_test_objects: List[SizingObject | OptimiseLoadProfileObject] = []

    def add(self, object: SizingObject | OptimiseLoadProfileObject) -> None:
        self.list_of_test_objects.append(object)

    @property
    def names_L2(self) -> list:
        list_of_names = []
        for _, i in enumerate(self.list_of_test_objects):
            if not isinstance(i, SizingObject):
                continue
            if i.L2_output is None and i.error_L2 is None:
                continue
            if i.name != '':
                list_of_names.append(i.name)
                continue
            list_of_names.append(f'case {_}')  # pragma: no cover
        return list_of_names

    @property
    def names_L3(self) -> list:
        list_of_names = []
        for _, i in enumerate(self.list_of_test_objects):
            if not isinstance(i, SizingObject):
                continue
            if i.L3_output is None and i.error_L3 is None:
                continue
            if i.name != '':
                list_of_names.append(i.name)
                continue
            list_of_names.append(f'case {_}')  # pragma: no cover
        return list_of_names

    @property
    def names_L4(self) -> list:
        list_of_names = []
        for _, i in enumerate(self.list_of_test_objects):
            if not isinstance(i, SizingObject):
                continue
            if i.L4_output is None and i.error_L4 is None:
                continue
            if i.name != '':
                list_of_names.append(i.name)
                continue
            list_of_names.append(f'case {_}')  # pragma: no cover
        return list_of_names

    @property
    def names_optimise_load_profile(self) -> list:
        list_of_names = []
        for _, i in enumerate(self.list_of_test_objects):
            if isinstance(i, SizingObject):
                continue
            if i.name != '':
                list_of_names.append(i.name)
                continue
            list_of_names.append(f'case {_}')  # pragma: no cover
        return list_of_names

    @property
    def L2_sizing_input(self) -> list:
        temp = []
        for _, i in enumerate(self.list_of_test_objects):
            if not isinstance(i, SizingObject):
                continue
            if i.L2_output is not None or i.error_L2 is not None:
                temp.append(copy.deepcopy(i.borefield))
        return temp

    @property
    def L2_sizing_output(self) -> list:
        temp = []
        for _, i in enumerate(self.list_of_test_objects):
            if not isinstance(i, SizingObject):
                continue
            if i.L2_output is not None or i.error_L2 is not None:
                temp.append((i.L2_output if i.L2_output is not None else i.error_L2, i.quadrant))
        return temp

    @property
    def L3_sizing_input(self) -> list:
        temp = []
        for _, i in enumerate(self.list_of_test_objects):
            if not isinstance(i, SizingObject):
                continue
            if i.L3_output is not None or i.error_L3 is not None:
                temp.append(copy.deepcopy(i.borefield))
        return temp

    @property
    def L3_sizing_output(self) -> list:
        temp = []
        for _, i in enumerate(self.list_of_test_objects):
            if not isinstance(i, SizingObject):
                continue
            if i.L3_output is not None or i.error_L3 is not None:
                temp.append((i.L3_output if i.L3_output is not None else i.error_L3, i.quadrant))
        return temp

    @property
    def L4_sizing_input(self) -> list:
        temp = []
        for _, i in enumerate(self.list_of_test_objects):
            if not isinstance(i, SizingObject):
                continue
            if i.L4_output is not None or i.error_L4 is not None:
                temp.append(copy.deepcopy(i.borefield))
        return temp

    @property
    def L4_sizing_output(self) -> list:
        temp = []
        for _, i in enumerate(self.list_of_test_objects):
            if not isinstance(i, SizingObject):
                continue
            if i.L4_output is not None or i.error_L4 is not None:
                temp.append((i.L4_output if i.L4_output is not None else i.error_L4, i.quadrant))
        return temp

    @property
    def optimise_load_profile_input(self) -> list:
        temp = []
        for _, i in enumerate(self.list_of_test_objects):
            if isinstance(i, SizingObject):
                continue
            temp.append((copy.deepcopy(i.borefield), copy.deepcopy(i.load), i.depth, i.SCOP, i.SEER, i.power, i.hourly,
                         i.max_peak_extraction, i.max_peak_injection))
        return temp

    @property
    def optimise_load_profile_output(self) -> list:
        temp = []
        for _, i in enumerate(self.list_of_test_objects):
            if isinstance(i, SizingObject):
                continue
            temp.append((i.percentage_extraction, i.percentage_injection, i.peak_extraction_geo, i.peak_injection_geo,
                         i.peak_extraction_ext, i.peak_injection_ext))
        return temp
