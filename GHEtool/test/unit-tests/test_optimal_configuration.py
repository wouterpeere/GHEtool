import pytest

from GHEtool import *
from GHEtool.Validation.cases import load_case
from GHEtool.Methods.optimise_borefield_configuration import optimise_borefield_configuration
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
