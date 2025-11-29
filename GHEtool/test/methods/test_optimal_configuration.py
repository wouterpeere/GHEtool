import pytest

from GHEtool import *
from GHEtool.Validation.cases import load_case
from GHEtool.Methods.optimise_borefield_configuration import optimise_borefield_configuration_config_all_in_once
from GHEtool.VariableClasses.BaseClass import UnsolvableOptimalFieldError


def test_unsolvable():
    borefield = Borefield(ground_data=GroundConstantTemperature(3.5, 10),
                          load=MonthlyGeothermalLoadAbsolute(*load_case(1)))
    borefield.create_rectangular_borefield(10, 6, 6.5, 6.5, 100, 4, 0.075)
    borefield.calculation_setup(use_neural_network=True)

    with pytest.raises(UnsolvableOptimalFieldError):
        optimise_borefield_configuration_config_all_in_once(borefield, 8, 7, 5, 7, 0.5, 60, 150)
