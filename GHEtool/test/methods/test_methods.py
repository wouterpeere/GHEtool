import pytest
import numpy as np
from GHEtool import Borefield
from GHEtool.test.methods.method_data import list_of_test_objects


@pytest.mark.parametrize("model,result",
                         zip(list_of_test_objects.L2_sizing_input, list_of_test_objects.L2_sizing_output),
                         ids=list_of_test_objects.names_L2)
def test_L2(model: Borefield, result):
    if not isinstance(result[0], (int, float, str)):
        try:
            model.size_L2(100)
        except result[0]:
            assert True
    else:
        assert np.isclose(model.size_L2(100), result[0], atol=1e-2)
        assert model.limiting_quadrant == result[1]


@pytest.mark.parametrize("model,result",
                         zip(list_of_test_objects.L3_sizing_input, list_of_test_objects.L3_sizing_output),
                         ids=list_of_test_objects.names_L3)
def test_L3(model: Borefield, result):
    if not isinstance(result[0], (int, float, str)):
        try:
            model.size_L3(100)
        except result[0]:
            assert True
    else:
        assert np.isclose(model.size_L3(100), result[0], atol=1e-2)
        assert model.calculate_quadrant() == result[1]


@pytest.mark.parametrize("model,result",
                         zip(list_of_test_objects.L4_sizing_input, list_of_test_objects.L4_sizing_output),
                         ids=list_of_test_objects.names_L4)
def test_L4(model: Borefield, result):
    if not isinstance(result[0], (int, float, str)):
        try:
            model.size_L4(100)
        except result[0]:
            assert True
    else:
        assert np.isclose(model.size_L4(100), result[0], atol=1e-2)
        assert model.calculate_quadrant() == result[1]


@pytest.mark.parametrize("input,result",
                         zip(list_of_test_objects.optimise_load_profile_input,
                             list_of_test_objects.optimise_load_profile_output),
                         ids=list_of_test_objects.names_optimise_load_profile)
def test_optimise(input, result):
    model: Borefield = input[0]
    depth, SCOP, SEER = input[1:]
    model.optimise_load_profile(depth, SCOP, SEER)
    percentage_heating, percentage_cooling, peak_heating_geo, peak_cooling_geo, peak_heating_ext, peak_cooling_ext = \
        result
    # print(model._percentage_heating, model._percentage_cooling)
    # print(np.max(model.peak_heating), np.max(model.peak_cooling))
    # print(np.max(model.peak_heating_external), np.max(model.peak_cooling_external))
    assert np.isclose(model._percentage_heating, percentage_heating)
    assert np.isclose(model._percentage_cooling, percentage_cooling)
    assert np.isclose(np.max(model.peak_heating), peak_heating_geo)
    assert np.isclose(np.max(model.peak_cooling), peak_cooling_geo)
    assert np.isclose(np.max(model.peak_heating_external), peak_heating_ext)
    assert np.isclose(np.max(model.peak_cooling_external), peak_cooling_ext)