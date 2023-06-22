import pytest
import numpy as np
from GHEtool import Borefield
from GHEtool.test.methods.method_data import list_of_test_objects


@pytest.mark.parametrize("model,result",
                         zip(list_of_test_objects.L2_sizing_input, list_of_test_objects.L2_sizing_output),
                         ids=list_of_test_objects.names)
def test_L2(model: Borefield, result):
    if not isinstance(result[0], (int, float, str)):
        with result[0]:
            assert model.size_L2(100)
    else:
        assert np.isclose(model.size_L2(100), result[0], atol=10e-2)
        assert model.limiting_quadrant == result[1]


@pytest.mark.parametrize("model,result",
                         zip(list_of_test_objects.L3_sizing_input, list_of_test_objects.L3_sizing_output),
                         ids=list_of_test_objects.names)
def test_L3(model: Borefield, result):
    if not isinstance(result[0], (int, float, str)):
        with result[0]:
            assert model.size_L3(100)
    else:
        assert np.isclose(model.size_L3(100), result[0], atol=10e-2)
        assert model.calculate_quadrant() == result[1]
