import pytest
import numpy as np
from GHEtool import Borefield
from GHEtool.test.methods.method_data import list_of_test_objects
from GHEtool.Methods import *


@pytest.mark.parametrize("model,result",
                         zip(list_of_test_objects.L2_sizing_input, list_of_test_objects.L2_sizing_output),
                         ids=list_of_test_objects.names_L2)
def test_L2(model: Borefield, result):
    if not isinstance(result[0], (int, float, str)):
        with pytest.raises(result[0]):
            model.size_L2(100)
    else:
        assert np.isclose(model.size_L2(100), result[0], atol=1e-2)
        assert model.limiting_quadrant == result[1]


@pytest.mark.parametrize("model,result",
                         zip(list_of_test_objects.L3_sizing_input, list_of_test_objects.L3_sizing_output),
                         ids=list_of_test_objects.names_L3)
def test_L3(model: Borefield, result):
    if not isinstance(result[0], (int, float, str)):
        with pytest.raises(result[0]):
            model.size_L3(100)
    else:
        assert np.isclose(model.size_L3(100), result[0], atol=1e-2)
        assert model.calculate_quadrant() == result[1]


@pytest.mark.parametrize("model,result",
                         zip(list_of_test_objects.L4_sizing_input, list_of_test_objects.L4_sizing_output),
                         ids=list_of_test_objects.names_L4)
def test_L4(model: Borefield, result):
    if not isinstance(result[0], (int, float, str)):
        with pytest.raises(result[0]):
            model.size_L4(100)
    else:
        assert np.isclose(model.size_L4(100), result[0], atol=1e-2)
        assert model.calculate_quadrant() == result[1]


@pytest.mark.parametrize("input,result",
                         zip(list_of_test_objects.optimise_load_profile_input,
                             list_of_test_objects.optimise_load_profile_output),
                         ids=list_of_test_objects.names_optimise_load_profile)
def test_optimise(input, result):
    model: Borefield = input[0]
    load, depth, power, hourly, max_peak_extraction, max_peak_injection, dhw_preferential = input[1:]
    model.H = depth
    if power == 1:
        return
        borefield_load, external_load = optimise_load_profile_power(model, load,
                                                                    use_hourly_resolution=hourly,
                                                                    max_peak_heating=max_peak_extraction,
                                                                    max_peak_cooling=max_peak_injection,
                                                                    dhw_preferential=dhw_preferential)
    elif power == 2:
        return
        borefield_load, external_load = optimise_load_profile_energy(model, load,
                                                                     max_peak_heating=max_peak_extraction,
                                                                     max_peak_cooling=max_peak_injection)

    elif power == 3:
        borefield_load, external_load = optimise_load_profile_balance(model, load,
                                                                      use_hourly_resolution=hourly,
                                                                      max_peak_heating=max_peak_extraction,
                                                                      max_peak_cooling=max_peak_injection,
                                                                      dhw_preferential=dhw_preferential)
        print("imbalance", borefield_load.imbalance,
              borefield_load.imbalance / np.maximum(borefield_load.yearly_average_extraction_load,
                                                    borefield_load.yearly_average_injection_load))
        model.load = borefield_load
        model.calculate_temperatures(hourly=True)
        print(borefield_load.results.min_temperature, borefield_load.results.max_temperature)
    percentage_extraction, percentage_injection, peak_extraction_geo, peak_injection_geo, peak_extraction_ext, peak_injection_ext = \
        result
    _percentage_extraction = (np.sum(borefield_load.hourly_heating_load_simulation_period) + np.sum(
        borefield_load.hourly_dhw_load_simulation_period)) / \
                             (np.sum(load.hourly_heating_load_simulation_period) + np.sum(
                                 load.hourly_dhw_load_simulation_period)) * 100
    _percentage_injection = np.sum(borefield_load.hourly_cooling_load_simulation_period) / \
                            np.sum(load.hourly_cooling_load_simulation_period) * 100
    print(_percentage_extraction)
    print(_percentage_injection)
    print(borefield_load.max_peak_extraction)
    print(borefield_load.max_peak_injection)
    print(external_load.max_peak_heating)
    print(external_load.max_peak_cooling)
    model.load = borefield_load
    model.calculate_temperatures(hourly=True)

    assert np.isclose(_percentage_extraction, percentage_extraction)
    assert np.isclose(_percentage_injection, percentage_injection)
    assert np.isclose(borefield_load.max_peak_extraction, peak_extraction_geo)
    assert np.isclose(borefield_load.max_peak_injection, peak_injection_geo)
    assert np.isclose(external_load.max_peak_heating, peak_extraction_ext)
    assert np.isclose(external_load.max_peak_cooling, peak_injection_ext)
