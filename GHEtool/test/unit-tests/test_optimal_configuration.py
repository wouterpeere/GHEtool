import pytest

from GHEtool import *
from GHEtool.Validation.cases import load_case
from GHEtool.Methods.optimise_borefield_configuration import optimise_borefield_configuration, _check_identical_field
from GHEtool.VariableClasses.BaseClass import UnsolvableOptimalFieldError


def test_unsolvable():
    borefield = Borefield(ground_data=GroundConstantTemperature(3.5, 10),
                          load=MonthlyGeothermalLoadAbsolute(*load_case(1)))
    borefield.create_rectangular_borefield(10, 6, 6.5, 6.5, 100, 4, 0.075)
    borefield.calculation_setup(use_neural_network=True)

    with pytest.raises(UnsolvableOptimalFieldError):
        optimise_borefield_configuration(borefield, 8, 7, 5, 7, 0.5, 60, 150)


def test_unsolvable_nb_boreholes():
    borefield = Borefield(ground_data=GroundConstantTemperature(3.5, 10),
                          load=MonthlyGeothermalLoadAbsolute(*load_case(1)))
    borefield.create_rectangular_borefield(10, 6, 6.5, 6.5, 100, 4, 0.075)
    borefield.calculation_setup(use_neural_network=True)

    with pytest.raises(UnsolvableOptimalFieldError):
        optimise_borefield_configuration(borefield, 80, 70, 5, 7, 0.5, 60, 150, nb_max=10)


def test_equal_hmin_hmax():
    borefield = Borefield(ground_data=GroundConstantTemperature(3.5, 10),
                          load=MonthlyGeothermalLoadAbsolute(*load_case(1)))
    borefield.create_rectangular_borefield(10, 6, 6.5, 6.5, 100, 4, 0.075)
    borefield.calculation_setup(use_neural_network=True)

    optimise_borefield_configuration(borefield, 100, 100, 5, 7, 0.5, 150, 150, nb_max=50)


def test_check_identical_field():
    existing_fields = set()
    existing_fields.add((('b_1', 6), ('b_2', 5), ('n_1', 3), ('n_2', 2), ('shape', 3)))
    existing_fields.add((('b_1', 6), ('b_2', 5), ('n_1', 1), ('n_2', 2), ('shape', 3)))

    assert not _check_identical_field({'shape': 3, 'n_1': 3, 'n_2': 2, 'b_1': 6, 'b_2': 5}, existing_fields)
    assert not _check_identical_field({'shape': 3, 'n_1': 1, 'n_2': 2, 'b_1': 6, 'b_2': 5}, existing_fields)
    assert _check_identical_field({'shape': 3, 'n_1': 3, 'n_2': 1, 'b_1': 6, 'b_2': 5}, existing_fields)
    assert not _check_identical_field({'shape': 3, 'n_1': 2, 'n_2': 1, 'b_1': 5, 'b_2': 6}, existing_fields)
    assert not _check_identical_field({'shape': 3, 'n_1': 2, 'n_2': 3, 'b_1': 5, 'b_2': 6}, existing_fields)


def test_flow_field():
    borefield = Borefield(ground_data=GroundConstantTemperature(3.5, 10),
                          load=MonthlyGeothermalLoadAbsolute(*load_case(1)))
    borefield.create_rectangular_borefield(10, 6, 6.5, 6.5, 100, 4, 0.075)
    borefield.calculation_setup(use_neural_network=True)
    with pytest.raises(AttributeError):
        optimise_borefield_configuration(borefield, 100, 100, 5, 7, 0.5, 150, 150, nb_max=50, flow_field=1)
