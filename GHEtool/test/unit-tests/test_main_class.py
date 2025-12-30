# noinspection PyPackageRequirements
import copy
import math

import matplotlib.pyplot as plt
import numpy as np
import pygfunction as gt
import pytest

from GHEtool import GroundConstantTemperature, GroundFluxTemperature, DoubleUTube, Borefield, \
    CalculationSetup, FOLDER, MultipleUTube, EERCombined, ConstantFlowRate, TemperatureDependentFluidData, \
    ConstantFluidData
from GHEtool.Validation.cases import load_case
from GHEtool.VariableClasses.LoadData import MonthlyGeothermalLoadAbsolute, HourlyGeothermalLoad, HourlyBuildingLoad, \
    HourlyBuildingLoadMultiYear, MonthlyBuildingLoadAbsolute
from GHEtool.VariableClasses.BaseClass import UnsolvableDueToTemperatureGradient
from GHEtool.Methods import *
from GHEtool import CustomGFunction

data = GroundConstantTemperature(3, 10)
ground_data_constant = data
data_ground_flux = GroundFluxTemperature(3, 10)
fluidData = ConstantFluidData(0.568, 998, 4180, 1e-3)
constantFlowData = ConstantFlowRate(mfr=0.2)
pipeData = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
flowData = ConstantFlowRate(vfr=0.2)

borefield_gt = gt.borefield.Borefield.rectangle_field(10, 12, 6, 6, 110, 4, 0.075)

# Monthly loading values
peakCooling = [0.0, 0, 34.0, 69.0, 133.0, 187.0, 213.0, 240.0, 160.0, 37.0, 0.0, 0.0]  # Peak cooling in kW
peakHeating = [160.0, 142, 102.0, 55.0, 0.0, 0.0, 0.0, 0.0, 40.4, 85.0, 119.0, 136.0]  # Peak heating in kW

# annual heating and cooling load
annualHeatingLoad = 300 * 10 ** 3  # kWh
annualCoolingLoad = 160 * 10 ** 3  # kWh

# percentage of annual load per month (15.5% for January ...)
monthlyLoadHeatingPercentage = [0.155, 0.148, 0.125, 0.099, 0.064, 0.0, 0.0, 0.0, 0.061, 0.087, 0.117, 0.144]
monthlyLoadCoolingPercentage = [0.025, 0.05, 0.05, 0.05, 0.075, 0.1, 0.2, 0.2, 0.1, 0.075, 0.05, 0.025]

# resulting load per month
monthlyLoadHeating = list(map(lambda x: x * annualHeatingLoad, monthlyLoadHeatingPercentage))  # kWh
monthlyLoadCooling = list(map(lambda x: x * annualCoolingLoad, monthlyLoadCoolingPercentage))  # kWh


def borefields_equal(borefield_one, borefield_two) -> bool:
    for i in range(len(borefield_one)):
        if borefield_one[i].__dict__ != borefield_two[i].__dict__:
            return False  # pragma: no cover
    return True


def test_set_investment_cost():
    borefield = Borefield()
    borefield.set_investment_cost()
    assert borefield.cost_investment == Borefield.DEFAULT_INVESTMENT
    borefield.set_investment_cost([0, 39])
    assert borefield.cost_investment == [0, 39]


def test_nb_of_boreholes():
    borefield = Borefield()
    assert borefield.number_of_boreholes == 0
    borefield = Borefield(borefield=copy.deepcopy(borefield_gt))
    borefield.ground_data = data_ground_flux
    assert borefield.number_of_boreholes == 120
    borefield.set_borefield(gt.borefield.Borefield.rectangle_field(5, 5, 6, 6, 110, 0.1, 0.07))
    assert np.isclose(borefield.avg_tilt, 0)
    assert np.isclose(borefield.H, 110)
    assert np.isclose(borefield.r_b, 0.07)
    assert np.isclose(borefield.D, 0.1)
    assert borefield.number_of_boreholes == 25
    borefield.gfunction(5000, 110)
    assert np.any(borefield.gfunction_calculation_object.borehole_length_array)
    borefield.borefield = gt.borefield.Borefield.rectangle_field(6, 5, 6, 6, 100, 1, 0.075)
    assert not np.any(borefield.gfunction_calculation_object.borehole_length_array)
    assert np.isclose(borefield.avg_tilt, 0)
    assert np.isclose(borefield.H, 100)
    assert np.isclose(borefield.r_b, 0.075)
    assert np.isclose(borefield.D, 1)
    borefield.gfunction(5000, 110)
    assert np.any(borefield.gfunction_calculation_object.borehole_length_array)
    assert np.isclose(borefield.avg_tilt, 0)
    assert borefield.number_of_boreholes == 30
    borefield.borefield = None
    assert not np.any(borefield.gfunction_calculation_object.borehole_length_array)
    assert borefield.gfunction_calculation_object
    assert borefield.number_of_boreholes == 0
    borefield.borefield = gt.borefield.Borefield.rectangle_field(6, 5, 6, 6, 100, 1, 0.075)
    borefield.gfunction(5000, 110)
    assert np.any(borefield.gfunction_calculation_object.borehole_length_array)
    assert np.isclose(borefield.avg_tilt, 0)
    borefield.set_borefield(None)
    assert not np.any(borefield.gfunction_calculation_object.borehole_length_array)
    assert borefield.number_of_boreholes == 0


def test_set_borefield():
    borefield = Borefield()
    borefield.set_borefield(gt.borefield.Borefield.from_boreholes([
        gt.boreholes.Borehole(100, 4, 0.075, 0, 0),
        gt.boreholes.Borehole(150, 4, 0.075, 10, 0)
    ]))
    assert borefield.H == 125


def test_tilt():
    borefield = Borefield()
    borefield.set_borefield(gt.borefield.Borefield.from_boreholes([
        gt.boreholes.Borehole(100, 4, 0.075, 0, 0),
        gt.boreholes.Borehole(150, 4, 0.075, 10, 0, tilt=math.pi / 9)
    ]))
    assert borefield.H == 125
    assert np.isclose(borefield.avg_tilt, math.pi / 18)
    assert np.isclose(borefield.depth, 4 + (100 + 150 * math.cos(math.pi / 9)) / 2)


def test_gfunction_with_irregular_borehole_depth():
    borefield = Borefield()
    borefield.ground_data = ground_data_constant
    borefield.set_borefield(gt.borefield.Borefield.from_boreholes([
        gt.boreholes.Borehole(150, 4, 0.075, 0, 0),
        gt.boreholes.Borehole(100, 4, 0.075, 10, 0)
    ]))
    borehole_irr = borefield.gfunction([3600, 3600 * 20, 3600 * 800])
    borefield.set_borefield(gt.borefield.Borefield.from_boreholes([
        gt.boreholes.Borehole(125, 4, 0.075, 0, 0),
        gt.boreholes.Borehole(125, 4, 0.075, 10, 0)
    ]))
    borehole_reg = borefield.gfunction([3600, 3600 * 20, 3600 * 800])

    # the gfunctions for those two classes should not be equal
    assert not np.array_equal(borehole_irr, borehole_reg)


def test_create_rectangular_field():
    borefield = Borefield()
    borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
    assert borefield.number_of_boreholes == 100
    borefields_equal(borefield.borefield, gt.borefield.Borefield.rectangle_field(10, 10, 6, 6, 110, 4, 0.075))
    assert borefield._borefield_description == {'B_1': 6, 'B_2': 6, 'N_1': 10, 'N_2': 10, 'type': 3}
    borefield.borefield = gt.borefield.Borefield.dense_rectangle_field(10, 10, 5, 5, 1, 0.075, False)
    assert borefield._borefield_description is None


def test_create_staggered_field():
    borefield = Borefield()
    borefield.create_staggered_shaped_borefield(10, 10, 6, 6, 110, 4, 0.075)
    assert borefield.number_of_boreholes == 95
    borefields_equal(borefield.borefield, gt.borefield.Borefield.staggered_rectangle_field(10, 10, 6, 6, 110, 4, 0.075,
                                                                                           include_last_borehole=False))


def test_create_circular_field():
    borefield = Borefield()
    borefield.create_circular_borefield(10, 10, 100, 1)
    assert borefield.number_of_boreholes == 10
    borefields_equal(borefield.borefield, gt.borefield.Borefield.circle_field(10, 10, 100, 1, 0.075))


def test_create_U_shaped_field():
    borefield = Borefield()
    borefield.create_U_shaped_borefield(10, 9, 6, 6, 110, 4, 0.075)
    assert borefield.number_of_boreholes == 9 * 2 + (10 - 2)
    borefields_equal(borefield.borefield, gt.borefield.Borefield.U_shaped_field(10, 10, 6, 6, 110, 4, 0.075))


def test_create_L_shaped_field():
    borefield = Borefield()
    borefield.create_L_shaped_borefield(10, 9, 6, 6, 110, 4, 0.075)
    assert borefield.number_of_boreholes == 10 + 8
    borefields_equal(borefield.borefield, gt.borefield.Borefield.L_shaped_field(10, 10, 6, 6, 110, 4, 0.075))


def test_create_box_shaped_field():
    borefield = Borefield()
    borefield.create_box_shaped_borefield(10, 8, 6, 6, 110, 4, 0.075)
    assert borefield.number_of_boreholes == 10 * 2 + (8 - 2) * 2
    borefields_equal(borefield.borefield, gt.borefield.Borefield.box_shaped_field(10, 10, 6, 6, 110, 4, 0.075))


def test_update_depth():
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    init_H = borefield.borefield[0].H

    borefield.H = init_H + 1
    borefield.H = 20
    for bor in borefield.borefield:
        assert bor.H == 20

    borefield.H = init_H + 2
    for bor in borefield.borefield:
        assert bor.H == init_H + 2

    borefield.H = init_H + 2
    for bor in borefield.borefield:
        assert bor.H == init_H + 2


def test_create_custom_dataset():
    borefield_test = Borefield()
    with pytest.raises(ValueError):
        borefield_test.create_custom_dataset([100, 1000], [50, 100])
    borefield_test.create_rectangular_borefield(10, 10, 6, 6, 100, 1, 0.075)
    with pytest.raises(AssertionError):
        borefield_test.create_custom_dataset([100, 1000], [50, 100])


def test_load_custom_gfunction():
    borefield = Borefield()
    borefield.ground_data = ground_data_constant
    borefield.borefield = copy.deepcopy(borefield_gt)
    borefield.create_custom_dataset()
    borefield.custom_gfunction.dump_custom_dataset("./", "test")
    dataset = copy.copy(borefield.custom_gfunction)
    borefield.borefield = None
    assert borefield.custom_gfunction is None
    borefield.custom_gfunction = dataset
    borefield.set_borefield(None)
    assert borefield.custom_gfunction is None
    borefield.load_custom_gfunction("./test.gvalues")
    assert borefield.custom_gfunction == dataset


def test_simulation_period():
    borefield = Borefield()
    assert borefield.simulation_period == 20
    assert len(borefield.load.time_L3) == 12 * 20
    borefield.simulation_period = 25
    assert borefield.simulation_period == 25
    assert len(borefield.load.time_L3) == 12 * 25
    borefield.load.simulation_period = 40
    assert borefield.simulation_period == 40
    assert len(borefield.load.time_L3) == 12 * 40


def test_set_Rb():
    borefield = Borefield()
    borefield.set_Rb(0.2)
    assert borefield.Rb == 0.2
    borefield.set_Rb(0.3)
    assert borefield.Rb == 0.3
    borefield.Rb = 0.4
    assert borefield.Rb == 0.4
    assert borefield.Rb == borefield.borehole._Rb


def test_ground_data_custom_gfunction():
    borefield = Borefield(borefield=copy.deepcopy(borefield_gt))
    assert borefield.ground_data == GroundConstantTemperature()
    borefield.ground_data = ground_data_constant
    assert borefield.custom_gfunction is None

    # create custom data set
    borefield.create_custom_dataset()
    borefield.gfunction([5000, 10000], 150)
    assert not borefield.custom_gfunction is None

    # test for property setter
    borefield.ground_data = ground_data_constant
    assert borefield.ground_data == ground_data_constant
    assert borefield._ground_data == ground_data_constant
    assert borefield.custom_gfunction is None

    # create custom data set
    borefield.create_custom_dataset()
    borefield.gfunction([5000, 10000], 150)
    assert not borefield.custom_gfunction is None

    # test for set function
    borefield.ground_data = data_ground_flux
    assert borefield.ground_data == data_ground_flux
    assert borefield._ground_data == data_ground_flux
    assert borefield.custom_gfunction is None


def test_ground_data_jit_gfunction():
    borefield = Borefield(borefield=copy.deepcopy(borefield_gt))
    assert borefield.ground_data == GroundConstantTemperature()
    borefield.ground_data = ground_data_constant

    # calculate gfunction
    borefield.gfunction([5000, 10000], 150)
    assert np.any(borefield.gfunction_calculation_object.borehole_length_array)

    # test for property setter
    borefield.ground_data = ground_data_constant
    assert borefield.ground_data == ground_data_constant
    assert borefield._ground_data == ground_data_constant
    assert not np.any(borefield.gfunction_calculation_object.borehole_length_array)

    # calculate gfunction
    borefield.gfunction([5000, 10000], 150)
    assert np.any(borefield.gfunction_calculation_object.borehole_length_array)

    # test for set function
    borefield.ground_data = data_ground_flux
    assert borefield.ground_data == data_ground_flux
    assert borefield._ground_data == data_ground_flux
    assert not np.any(borefield.gfunction_calculation_object.borehole_length_array)


def test_set_fluid_params():
    borefield = Borefield()
    assert borefield.borehole.fluid_data is None
    borefield.fluid_data = fluidData
    assert borefield.fluid_data == fluidData


def test_set_flow_params():
    borefield = Borefield()
    assert borefield.borehole.flow_data is None
    borefield.flow_data = flowData
    assert borefield.borehole.flow_data == flowData
    assert borefield.flow_data == flowData


def test_set_pipe_params():
    borefield = Borefield()
    assert borefield.borehole.pipe_data is None
    borefield.pipe_data = pipeData
    assert borefield.borehole.pipe_data == pipeData
    assert borefield.pipe_data == pipeData


def test_set_max_temp():
    borefield = Borefield()
    borefield.set_max_fluid_temperature(13)
    assert borefield.Tf_max == 13
    borefield.set_max_avg_fluid_temperature(15)
    assert borefield.Tf_max == 15
    borefield.set_max_fluid_temperature(14)
    assert borefield.Tf_max == 14
    with pytest.raises(ValueError):
        borefield.set_max_fluid_temperature(borefield.Tf_min - 1)


def test_set_min_temp():
    borefield = Borefield()
    borefield.set_min_fluid_temperature(3)
    assert borefield.Tf_min == 3
    borefield.set_min_avg_fluid_temperature(5)
    assert borefield.Tf_min == 5
    borefield.set_min_fluid_temperature(4)
    assert borefield.Tf_min == 4
    with pytest.raises(ValueError):
        borefield.set_min_fluid_temperature(borefield.Tf_max + 1)


def test_Tg():
    borefield = Borefield()
    borefield.ground_data = ground_data_constant
    assert borefield._Tg() == borefield.ground_data.calculate_Tg(borefield.H)
    assert borefield._Tg(20) == borefield.ground_data.calculate_Tg(20)
    borefield.ground_data = data_ground_flux
    assert borefield._Tg() == borefield.ground_data.calculate_Tg(borefield.H)
    assert borefield._Tg(20) == borefield.ground_data.calculate_Tg(20)


@pytest.mark.parametrize(
    "ground_data, constant_Rb, result",
    zip(
        [ground_data_constant, data_ground_flux, ground_data_constant, data_ground_flux],
        [True, True, False, False],
        [39.994203323480214, 38.45978496550447, 30.924434615896764, 30.047718917393134],
    ),
)
def test_Ahmadfard(ground_data, constant_Rb, result):
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    load = MonthlyGeothermalLoadAbsolute(*load_case(3))
    borefield.ground_data = ground_data
    borefield.fluid_data = fluidData
    borefield.flow_data = constantFlowData
    borefield.pipe_data = pipeData
    borefield.calculation_setup(use_constant_Rb=constant_Rb)
    th, qh, qm, qa = load._calculate_last_year_params(True)
    assert np.isclose(borefield._Ahmadfard(th, qh, qm, qa, 0), result)
    assert np.isclose(borefield.H, result)


@pytest.mark.parametrize(
    "ground_data, constant_Rb, result",
    zip(
        [ground_data_constant, data_ground_flux, ground_data_constant, data_ground_flux],
        [True, True, False, False],
        [48.76844845370183, 46.254155886276564, 38.53491016745154, 36.81621398703887],
    ),
)
def test_Carcel(ground_data, constant_Rb, result):
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    load = MonthlyGeothermalLoadAbsolute(*load_case(3))

    borefield.ground_data = ground_data
    borefield.fluid_data = fluidData
    borefield.flow_data = constantFlowData
    borefield.pipe_data = pipeData
    borefield.calculation_setup(use_constant_Rb=constant_Rb)
    th, _, tcm, qh, qpm, qm = load._calculate_first_year_params(True)
    assert np.isclose(borefield._Carcel(th, tcm, qh, qpm, qm, 0), result)
    assert np.isclose(borefield.H, result)


def test_set_sizing_setup():
    borefield = Borefield()
    sizing_setup_backup = copy.deepcopy(borefield._calculation_setup)
    borefield.calculation_setup()
    assert borefield._calculation_setup == sizing_setup_backup
    # set calculation_setup
    test = CalculationSetup(4, False, True, False)
    test2 = CalculationSetup(3, False, False, True)
    borefield.calculation_setup(use_constant_Rb=True, quadrant_sizing=4, L2_sizing=False, L3_sizing=True,
                                L4_sizing=False)
    assert borefield._calculation_setup == test
    borefield.calculation_setup(calculation_setup=test2)
    assert borefield._calculation_setup == test2

    borefield.calculation_setup(rtol=10)
    assert borefield._calculation_setup.rtol == 10
    borefield.calculation_setup(atol=10)
    assert borefield._calculation_setup.atol == 10
    assert borefield._calculation_setup.rtol == 10


def test_size():
    borefield = Borefield()
    with pytest.raises(ValueError):
        borefield.size()
    borefield.borefield = copy.deepcopy(borefield_gt)
    borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(3))

    borefield.ground_data = ground_data_constant
    sizing_setup_backup = copy.deepcopy(borefield._calculation_setup)
    borefield.size(L3_sizing=True)
    assert borefield._calculation_setup == sizing_setup_backup


def test_select_size():
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(3))

    # with constant Tg
    borefield.ground_data = ground_data_constant
    assert borefield._select_size(100, 20) == 100
    assert borefield._select_size(10, 20) == 20

    # with variable Tg
    borefield.ground_data = data_ground_flux
    assert borefield._select_size(100, 20) == 100
    assert borefield._select_size(10, 80) == 80
    borefield.set_max_fluid_temperature(14)
    with pytest.raises(UnsolvableDueToTemperatureGradient):
        borefield._select_size(10, 80)


def test_size_L2_value_errors():
    borefield = Borefield()
    with pytest.raises(ValueError):
        borefield.size_L2(100)
    load = MonthlyGeothermalLoadAbsolute(*load_case(2))
    borefield.load = load
    borefield.ground_data = ground_data_constant
    with pytest.raises(ValueError):
        borefield.size_L2(100, 5)


@pytest.mark.parametrize("quadrant, result", zip([1, 2, 3, 4], [74.55862437702756, 96.85342542746277, 27.2041541800546,
                                                                21.903857780936665]))
def test_size_L2(quadrant, result):
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(2))
    borefield.ground_data = ground_data_constant
    borefield.size_L2(100, quadrant_sizing=quadrant)

    assert np.isclose(result, borefield.size_L2(100, quadrant_sizing=quadrant))
    assert borefield.limiting_quadrant == quadrant
    assert np.isclose(result, borefield.H)


def test_size_L3_value_errors():
    borefield = Borefield()
    with pytest.raises(ValueError):
        borefield.size_L3(100)
    borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(2))
    borefield.ground_data = ground_data_constant
    with pytest.raises(ValueError):
        borefield.size_L3(100, 5)


@pytest.mark.parametrize("quadrant, result", zip([1, 2, 3, 4],
                                                 [56.372611810628065, 71.43023711680347, 27.162673692721025,
                                                  21.602240810876843]))
def test_size_L3(quadrant, result):
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    borefield.set_max_fluid_temperature(18)
    borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(2))
    borefield.ground_data = ground_data_constant

    assert np.isclose(result, borefield.size_L3(100, quadrant_sizing=quadrant))
    assert np.isclose(result, borefield.H)


def test_size_L4_value_errors():
    borefield = Borefield()
    with pytest.raises(ValueError):
        borefield.size_L4(100)
    borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(2))
    borefield.ground_data = ground_data_constant
    with pytest.raises(ValueError):
        borefield.size_L4(100, 5)
    with pytest.raises(ValueError):
        borefield.size_L4(100)


def test_size_L4():
    borefield = Borefield()
    borefield.ground_data = ground_data_constant
    load = HourlyGeothermalLoad()
    # quadrant 1
    borefield.borefield = copy.deepcopy(borefield_gt)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    borefield.load = load
    assert np.isclose(182.17317343989652, borefield.size_L4(100, quadrant_sizing=1))
    assert np.isclose(182.17317343989652, borefield.H)
    assert borefield.calculate_quadrant() == 1
    # quadrant 2
    borefield.borefield = copy.deepcopy(borefield_gt)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"), col_injection=0, col_extraction=1)
    borefield.load = load

    assert np.isclose(305.26723226385184, borefield.size_L4(100, quadrant_sizing=2))
    assert np.isclose(305.26723226385184, borefield.H)
    assert borefield.calculate_quadrant() == 2
    # quadrant 3
    borefield.borefield = copy.deepcopy(borefield_gt)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"), col_injection=0, col_extraction=1)
    borefield.load = load

    borefield.set_max_fluid_temperature(25)
    assert np.isclose(109.4742962707615, borefield.size_L4(100, quadrant_sizing=3))
    assert np.isclose(109.4742962707615, borefield.H)
    assert borefield.calculate_quadrant() == 3
    # quadrant 4
    borefield.borefield = copy.deepcopy(borefield_gt)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    borefield.load = load

    # to increase coverage
    borefield.calculation_setup(L4_sizing=True)
    assert np.isclose(174.2214456661528, borefield.size(100, quadrant_sizing=4))
    assert np.isclose(174.2214456661528, borefield.H)
    assert borefield.calculate_quadrant() == 4


def test_calculate_temperatures_eer_combined():
    eer_combined = EERCombined(20, 5, 17)
    borefield = Borefield()
    borefield.ground_data = ground_data_constant
    load = HourlyBuildingLoad(efficiency_cooling=eer_combined)

    borefield.borefield = copy.deepcopy(borefield_gt)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    borefield.load = load
    borefield.calculate_temperatures(hourly=True)

    active_cooling_array = borefield.load.eer.get_time_series_active_cooling(borefield.results.peak_injection,
                                                                             borefield.load.month_indices)
    assert np.allclose(borefield.load.hourly_cooling_load_simulation_period * active_cooling_array *
                       (1 + 1 / 5) + borefield.load.hourly_cooling_load_simulation_period * np.invert(
        active_cooling_array) *
                       (1 + 1 / 20),
                       borefield.load.hourly_injection_load_simulation_period)


def test_investment_cost():
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    borefield.H = 100
    cost = 10 * 12 * 100
    assert borefield.investment_cost == cost * borefield.cost_investment[0]
    borefield.set_investment_cost([38, 0])
    assert borefield.investment_cost == cost * 38


def test_reynolds_number():
    borefield = Borefield()
    borefield.pipe_data = pipeData
    borefield.fluid_data = fluidData
    borefield.flow_data = constantFlowData
    assert np.isclose(4244.131815783876, borefield.Re)


def test_last_year_params():
    load = MonthlyGeothermalLoadAbsolute(*load_case(2))
    th, qh, qm, qa = load._calculate_last_year_params(False)
    assert np.isclose(9132.420091324202, qa)
    assert np.isclose(65753.42465753425, qm)
    assert np.isclose(240000.0, qh)
    assert np.isclose(21600.0, th)
    th, qh, qm, qa = load._calculate_last_year_params(True)
    assert np.isclose(-9132.420091324202, qa)
    assert np.isclose(25753.424657534248, qm)
    assert np.isclose(160000.0, qh)
    assert np.isclose(21600.0, th)


def test_first_year_params():
    load = MonthlyGeothermalLoadAbsolute(*load_case(2))
    th, tpm, tcm, qh, qpm, qcm = load._calculate_first_year_params(False)
    assert np.isclose(65753.42465753425, qcm)
    assert np.isclose(6410.95890410959, qpm)
    assert np.isclose(21024000.0, tcm)
    assert np.isclose(18396000.0, tpm)
    assert np.isclose(240000.0, qh)
    assert np.isclose(21600.0, th)
    th, tpm, tcm, qh, qpm, qcm = load._calculate_first_year_params(True)
    assert np.isclose(25753.424657534248, qcm)
    assert np.isclose(0, qpm)
    assert np.isclose(2628000.0, tcm)
    assert np.isclose(0, tpm)
    assert np.isclose(160000.0, qh)
    assert np.isclose(21600.0, th)


def test_calculate_temperatures():
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    borefield.ground_data = ground_data_constant
    borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(2))

    borefield.calculate_temperatures(120)
    np.testing.assert_array_almost_equal(borefield.results.peak_extraction,
                                         np.array([
                                             7.72762934, 7.99146503, 8.51833967, 9.1509561, 9.8552787, 10.35493277,
                                             10.85933332, 10.99023511, 9.98375157, 9.25504159, 8.66647284, 8.29771455,
                                             7.91665803, 8.17800342, 8.70170202, 9.33072871, 10.03114914, 10.5277391,
                                             11.0286007, 11.15588842, 10.14604144, 9.41410275, 8.82400344, 8.45241599,
                                             8.06820009, 8.32841849, 8.84875588, 9.47501242, 10.17511856, 10.66895627,
                                             11.16793946, 11.29298095, 10.27931577, 9.54524349, 8.95252998, 8.57774404,
                                             8.1937121, 8.45376071, 8.97324652, 9.59889207, 10.29514246, 10.78586212,
                                             11.28414338, 11.40870247, 10.3944788, 9.65919691, 9.06287342, 8.68650234,
                                             8.30202959, 8.56162475, 9.0809234, 9.70411175, 10.39740363, 10.88747028,
                                             11.38536271, 11.50938828, 10.49543903, 9.75782827, 9.16004967, 8.78343508,
                                             8.39839472, 8.65659837, 9.17185807, 9.79012601, 10.48160262, 10.97114404,
                                             11.46961158, 11.59667566, 10.58444917, 9.84785261, 9.25064654, 8.87359141,
                                             8.48648536, 8.74025394, 9.25021913, 9.8657074, 10.55637015, 11.04626604,
                                             11.54703051, 11.67614232, 10.66484006, 9.9288079, 9.33147076, 8.95301947,
                                             8.56269321, 8.81203059, 9.31897773, 9.93357669, 10.62431486, 11.11560581,
                                             11.61858065, 11.74854509, 10.73779693, 10.00185568, 9.40361146, 9.02283284,
                                             8.62872694, 8.87490012, 9.38091117, 9.99538574, 10.68685342, 11.1804467,
                                             11.68421179, 11.81471642, 10.8042213, 10.06774287, 9.46785433, 9.08381829,
                                             8.68647695, 8.93169037, 9.43743157, 10.0523689, 10.74630288, 11.24107298,
                                             11.74562143, 11.87654742, 10.86557977, 10.12726795, 9.52355201, 9.13523399,
                                             8.73598286, 8.98063986, 9.48677597, 10.10303793, 10.79729468, 11.29206477,
                                             11.79661323, 11.92753922, 10.91657157, 10.17825975, 9.57454381, 9.18622578,
                                             8.78697465, 9.03163166, 9.53835349, 10.1560971, 10.85129753, 11.34666291,
                                             11.85119791, 11.9809148, 10.96702476, 10.22436363, 9.61735017, 9.22805838,
                                             8.82877404, 9.07436147, 9.58209642, 10.19984003, 10.89504046, 11.39040584,
                                             11.89494084, 12.02465773, 11.0107677, 10.26810656, 9.6610931, 9.27180131,
                                             8.87251697, 9.1193242, 9.62795252, 10.2462994, 10.94180665, 11.43669622,
                                             11.93961809, 12.06604757, 11.04869711, 10.304766, 9.69738516, 9.30849997,
                                             8.91036968, 9.15729976, 9.66592808, 10.28427496, 10.97978221, 11.47467178,
                                             11.97759365, 12.10402313, 11.08667267, 10.34274156, 9.73536072, 9.3469794,
                                             8.94976286, 9.19728055, 9.70626741, 10.32452901, 11.01914507, 11.51198131,
                                             12.01208298, 12.13659709, 11.11868228, 10.37480091, 9.76809148, 9.38025464,
                                             8.98303809, 9.23055579, 9.73954264, 10.35780424, 11.05242031, 11.54525655,
                                             12.04535822, 12.16987233, 11.15195751, 10.40808738, 9.80228547, 9.41501288,
                                             9.01818183, 9.26587882, 9.77447963, 10.39156292, 11.08385107, 11.57437959,
                                             12.07379672, 12.19811941, 11.18053668, 10.43748277, 9.83168085, 9.44440826,
                                             9.04757722, 9.29527421, 9.80387501, 10.4209583, 11.11324646, 11.60377497,
                                             12.1031921, 12.2275148, 11.21058262, 10.46842667, 9.86320837, 9.47627879,
                                             9.07928008, 9.32594275, 9.83225219, 10.44641374, 11.13694838, 11.62696168,
                                             12.12650419, 12.25159304, 11.23510843, 10.49295248, 9.88773418, 9.5008046
                                         ]))
    np.testing.assert_array_almost_equal(borefield.results.peak_injection,
                                         np.array([
                                             9.76307792, 9.94528491, 10.20779825, 10.71238908, 11.68713924, 12.59873554,
                                             13.28921831, 13.76520367, 12.45828104, 10.78945062, 10.35655154,
                                             10.03714501,
                                             9.95210661, 10.1318233, 10.39116059, 10.89216169, 11.86300968, 12.77154188,
                                             13.45848569, 13.93085698, 12.62057091, 10.94851178, 10.51408214,
                                             10.19184645,
                                             10.10364867, 10.28223837, 10.53821445, 11.0364454, 12.0069791, 12.91275905,
                                             13.59782445, 14.06794951, 12.75384524, 11.07965252, 10.64260868,
                                             10.3171745,
                                             10.22916068, 10.40758059, 10.66270509, 11.16032504, 12.127003, 13.02966489,
                                             13.71402837, 14.18367104, 12.86900827, 11.19360594, 10.75295212,
                                             10.4259328,
                                             10.33747817, 10.51544463, 10.77038198, 11.26554473, 12.22926417,
                                             13.13127305,
                                             13.8152477, 14.28435684, 12.9699685, 11.2922373, 10.85012837, 10.52286554,
                                             10.4338433, 10.61041825, 10.86131665, 11.35155899, 12.31346316,
                                             13.21494681,
                                             13.89949657, 14.37164422, 13.05897864, 11.38226164, 10.94072524,
                                             10.61302187,
                                             10.52193394, 10.69407382, 10.9396777, 11.42714038, 12.38823069,
                                             13.29006881,
                                             13.9769155, 14.45111088, 13.13936953, 11.46321693, 11.02154946,
                                             10.69244993,
                                             10.59814178, 10.76585047, 11.0084363, 11.49500967, 12.4561754, 13.35940858,
                                             14.04846564, 14.52351365, 13.2123264, 11.53626471, 11.09369016, 10.7622633,
                                             10.66417552, 10.82872, 11.07036974, 11.55681872, 12.51871396, 13.42424948,
                                             14.11409678, 14.58968498, 13.27875077, 11.6021519, 11.15793302,
                                             10.82324875,
                                             10.72192553, 10.88551025, 11.12689014, 11.61380188, 12.57816342,
                                             13.48487575,
                                             14.17550642, 14.65151598, 13.34010924, 11.66167698, 11.21363071,
                                             10.87466445,
                                             10.77143143, 10.93445974, 11.17623455, 11.66447091, 12.62915522,
                                             13.53586755,
                                             14.22649822, 14.70250778, 13.39110104, 11.71266878, 11.2646225,
                                             10.92565624,
                                             10.82242323, 10.98545154, 11.22781206, 11.71753008, 12.68315807,
                                             13.59046568,
                                             14.2810829, 14.75588336, 13.44155423, 11.75877265, 11.30742886,
                                             10.96748884,
                                             10.86422261, 11.02818135, 11.27155499, 11.76127301, 12.72690101,
                                             13.63420862,
                                             14.32482583, 14.79962629, 13.48529717, 11.80251559, 11.3511718,
                                             11.01123177,
                                             10.90796555, 11.07314408, 11.31741109, 11.80773238, 12.7736672, 13.680499,
                                             14.36950308, 14.84101614, 13.52322658, 11.83917503, 11.38746386,
                                             11.04793044,
                                             10.94581826, 11.11111964, 11.35538665, 11.84570794, 12.81164275,
                                             13.71847456,
                                             14.40747864, 14.87899169, 13.56120214, 11.87715059, 11.42543942,
                                             11.08640986,
                                             10.98521144, 11.15110043, 11.39572598, 11.88596199, 12.85100562,
                                             13.75578409,
                                             14.44196797, 14.91156566, 13.59321175, 11.90920994, 11.45817018,
                                             11.1196851,
                                             11.01848667, 11.18437566, 11.42900122, 11.91923722, 12.88428085,
                                             13.78905932,
                                             14.47524321, 14.94484089, 13.62648698, 11.94249641, 11.49236417,
                                             11.15444334,
                                             11.05363041, 11.2196987, 11.4639382, 11.9529959, 12.91571162, 13.81818236,
                                             14.50368171, 14.97308798, 13.65506615, 11.9718918, 11.52175955,
                                             11.18383872,
                                             11.0830258, 11.24909409, 11.49333358, 11.98239128, 12.945107, 13.84757774,
                                             14.53307709, 15.00248336, 13.68511209, 12.0028357, 11.55328707,
                                             11.21570925,
                                             11.11472866, 11.27976263, 11.52171076, 12.00784671, 12.96880892,
                                             13.87076446,
                                             14.55638918, 15.0265616, 13.7096379, 12.02736151, 11.57781288, 11.24023506
                                         ]))
    np.testing.assert_array_almost_equal(borefield.results.monthly_injection,
                                         np.array([9.7265228, 9.87217467, 9.91023486, 9.96749514, 10.24004053,
                                                   10.62890537, 11.40727853, 11.53818031, 10.77407145, 10.54689525,
                                                   10.2834413, 10.00058989, 9.91555149, 10.05871306, 10.09359721,
                                                   10.14726775, 10.41591098, 10.8017117, 11.5765459, 11.70383362,
                                                   10.93636131, 10.70595641, 10.44097189, 10.15529133, 10.06709355,
                                                   10.20912812, 10.24065107, 10.29155146, 10.55988039, 10.94292887,
                                                   11.71588467, 11.84092616, 11.06963565, 10.83709715, 10.56949843,
                                                   10.28061938, 10.19260556, 10.33447035, 10.36514171, 10.41543111,
                                                   10.6799043, 11.05983472, 11.83208858, 11.95664768, 11.18479868,
                                                   10.95105057, 10.67984187, 10.38937768, 10.30092305, 10.44233439,
                                                   10.47281859, 10.52065079, 10.78216546, 11.16144288, 11.93330791,
                                                   12.05733349, 11.28575891, 11.04968193, 10.77701813, 10.48631042,
                                                   10.39728818, 10.53730801, 10.56375326, 10.60666505, 10.86636446,
                                                   11.24511664, 12.01755679, 12.14462086, 11.37476905, 11.13970627,
                                                   10.867615, 10.57646675, 10.48537882, 10.62096358, 10.64211432,
                                                   10.68224644, 10.94113198, 11.32023864, 12.09497572, 12.22408753,
                                                   11.45515993, 11.22066156, 10.94843922, 10.65589481, 10.56158666,
                                                   10.69274023, 10.71087292, 10.75011573, 11.00907669, 11.38957841,
                                                   12.16652586, 12.2964903, 11.5281168, 11.29370934, 11.02057992,
                                                   10.72570818, 10.6276204, 10.75560975, 10.77280636, 10.81192478,
                                                   11.07161525, 11.4544193, 12.23215699, 12.36266163, 11.59454118,
                                                   11.35959653, 11.08482278, 10.78669363, 10.68537041, 10.81240001,
                                                   10.82932676, 10.86890794, 11.13106472, 11.51504558, 12.29356664,
                                                   12.42449263, 11.65589964, 11.41912161, 11.14052047, 10.83810933,
                                                   10.73487631, 10.8613495, 10.87867116, 10.91957697, 11.18205651,
                                                   11.56603738, 12.34455843, 12.47548442, 11.70689144, 11.47011341,
                                                   11.19151226, 10.88910112, 10.78586811, 10.91234129, 10.93024868,
                                                   10.97263614, 11.23605937, 11.62063551, 12.39914311, 12.52886,
                                                   11.75734464, 11.51621729, 11.23431862, 10.93093372, 10.82766749,
                                                   10.9550711, 10.97399161, 11.01637908, 11.2798023, 11.66437844,
                                                   12.44288605, 12.57260294, 11.80108757, 11.55996022, 11.27806156,
                                                   10.97467665, 10.87141043, 11.00003384, 11.01984771, 11.06283844,
                                                   11.32656849, 11.71066883, 12.4875633, 12.61399278, 11.83901699,
                                                   11.59661966, 11.31435362, 11.01137532, 10.90926314, 11.03800939,
                                                   11.05782327, 11.100814, 11.36454405, 11.74864438, 12.52553885,
                                                   12.65196834, 11.87699255, 11.63459522, 11.35232918, 11.04985474,
                                                   10.94865631, 11.07799019, 11.0981626, 11.14106805, 11.40390691,
                                                   11.78595391, 12.56002819, 12.6845423, 11.90900215, 11.66665457,
                                                   11.38505994, 11.08312998, 10.98193155, 11.11126542, 11.13143783,
                                                   11.17434329, 11.43718215, 11.81922915, 12.59330342, 12.71781753,
                                                   11.94227739, 11.69994104, 11.41925392, 11.11788822, 11.01707529,
                                                   11.14658846, 11.16637482, 11.20810196, 11.46861291, 11.84835219,
                                                   12.62174192, 12.74606462, 11.97085655, 11.72933643, 11.44864931,
                                                   11.1472836, 11.04647067, 11.17598384, 11.1957702, 11.23749734,
                                                   11.49800829, 11.87774757, 12.65113731, 12.77546, 12.00090249,
                                                   11.76028033, 11.48017683, 11.17915413, 11.07817353, 11.20665239,
                                                   11.22414738, 11.26295278, 11.52171021, 11.90093428, 12.67444939,
                                                   12.79953825, 12.0254283, 11.78480614, 11.50470264, 11.20367994]))
    np.testing.assert_array_almost_equal(borefield.results.monthly_extraction,
                                         np.array([9.37492462, 9.46486873, 9.54493806, 9.64968692, 9.9176661,
                                                   10.35493277, 10.85933332, 10.99023511, 10.38868332, 10.18251169,
                                                   9.93275637, 9.66908304, 9.56395331, 9.65140713, 9.72830041,
                                                   9.82945953, 10.09353655, 10.5277391, 11.0286007, 11.15588842,
                                                   10.55097318, 10.34157285, 10.09028696, 9.82378448, 9.71549538,
                                                   9.80182219, 9.87535427, 9.97374324, 10.23750597, 10.66895627,
                                                   11.16793946, 11.29298095, 10.68424752, 10.47271359, 10.2188135,
                                                   9.94911253, 9.84100739, 9.92716441, 9.99984491, 10.09762289,
                                                   10.35752987, 10.78586212, 11.28414338, 11.40870247, 10.79941055,
                                                   10.58666701, 10.32915694, 10.05787083, 9.94932487, 10.03502846,
                                                   10.10752179, 10.20284257, 10.45979104, 10.88747028, 11.38536271,
                                                   11.50938828, 10.90037078, 10.68529837, 10.4263332, 10.15480357,
                                                   10.04569001, 10.13000207, 10.19845646, 10.28885683, 10.54399003,
                                                   10.97114404, 11.46961158, 11.59667566, 10.98938092, 10.77532271,
                                                   10.51693007, 10.2449599, 10.13378064, 10.21365764, 10.27681752,
                                                   10.36443822, 10.61875755, 11.04626604, 11.54703051, 11.67614232,
                                                   11.0697718, 10.856278, 10.59775429, 10.32438796, 10.20998849,
                                                   10.28543429, 10.34557611, 10.43230751, 10.68670226, 11.11560581,
                                                   11.61858065, 11.74854509, 11.14272868, 10.92932578, 10.66989498,
                                                   10.39420133, 10.27602223, 10.34830382, 10.40750956, 10.49411656,
                                                   10.74924083, 11.1804467, 11.68421179, 11.81471642, 11.20915305,
                                                   10.99521297, 10.73413785, 10.45518678, 10.33377223, 10.40509407,
                                                   10.46402996, 10.55109972, 10.80869029, 11.24107298, 11.74562143,
                                                   11.87654742, 11.27051152, 11.05473805, 10.78983554, 10.50660248,
                                                   10.38327814, 10.45404356, 10.51337436, 10.60176875, 10.85968208,
                                                   11.29206477, 11.79661323, 11.92753922, 11.32150331, 11.10572985,
                                                   10.84082733, 10.55759427, 10.43426994, 10.50503536, 10.56495187,
                                                   10.65482792, 10.91368494, 11.34666291, 11.85119791, 11.9809148,
                                                   11.37195651, 11.15183373, 10.88363369, 10.59942687, 10.47606932,
                                                   10.54776517, 10.60869481, 10.69857086, 10.95742787, 11.39040584,
                                                   11.89494084, 12.02465773, 11.41569944, 11.19557666, 10.92737662,
                                                   10.6431698, 10.51981225, 10.5927279, 10.65455091, 10.74503022,
                                                   11.00419406, 11.43669622, 11.93961809, 12.06604757, 11.45362886,
                                                   11.2322361, 10.96366869, 10.67986847, 10.55766497, 10.63070346,
                                                   10.69252646, 10.78300578, 11.04216962, 11.47467178, 11.97759365,
                                                   12.10402313, 11.49160442, 11.27021166, 11.00164424, 10.71834789,
                                                   10.59705814, 10.67068425, 10.7328658, 10.82325983, 11.08153248,
                                                   11.51198131, 12.01208298, 12.13659709, 11.52361402, 11.30227101,
                                                   11.03437501, 10.75162313, 10.63033338, 10.70395949, 10.76614103,
                                                   10.85653507, 11.11480772, 11.54525655, 12.04535822, 12.16987233,
                                                   11.55688926, 11.33555748, 11.06856899, 10.78638137, 10.66547712,
                                                   10.73928253, 10.80107801, 10.89029374, 11.14623848, 11.57437959,
                                                   12.07379672, 12.19811941, 11.58546842, 11.36495287, 11.09796438,
                                                   10.81577675, 10.6948725, 10.76867791, 10.8304734, 10.91968913,
                                                   11.17563386, 11.60377497, 12.1031921, 12.2275148, 11.61551436,
                                                   11.39589677, 11.1294919, 10.84764728, 10.72657536, 10.79934645,
                                                   10.85885057, 10.94514456, 11.19933578, 11.62696168, 12.12650419,
                                                   12.25159304, 11.64004017, 11.42042258, 11.15401771, 10.87217309]))


def test_set_options_gfunction_calculation():
    borefield = Borefield()
    borefield.set_options_gfunction_calculation({"method": "equivalentt"})
    assert borefield.gfunction_calculation_object.options["method"] == "equivalentt"
    borefield.set_options_gfunction_calculation({"method": "equivalent"})


def test_gfunction():
    borefield = Borefield()
    borefield.ground_data = data_ground_flux
    borefield.create_rectangular_borefield(10, 10, 6, 6, 100, 1, 0.075)
    borefield.H = 100_000
    with pytest.raises(UnsolvableDueToTemperatureGradient):
        borefield.gfunction(56491)
    borefield.H = 102.3

    np.testing.assert_array_almost_equal(borefield.gfunction([6000, 60000, 600000]),
                                         np.array([0.63751082, 1.70657847, 2.84227252]))
    borefield.create_custom_dataset()
    np.testing.assert_array_almost_equal(borefield.gfunction([6000, 60000, 600000]),
                                         np.array([0.622017, 1.703272, 2.840246]))
    borefield.calculation_setup(use_precalculated_dataset=False)
    np.testing.assert_array_almost_equal(borefield.gfunction([6000, 60000, 600000]),
                                         np.array([0.63751082, 1.70657847, 2.84227252]))


def test_gfunction_with_irregular_depth():
    borefield = Borefield()
    borefield.ground_data = data_ground_flux
    temp = [
        gt.boreholes.Borehole(100, 4, 0.075, 0, 0),
        gt.boreholes.Borehole(150, 4, 0.075, 10, 0),
        gt.boreholes.Borehole(50, 4, 0.075, 100, 0)
    ]
    borefield.borefield = gt.borefield.Borefield.from_boreholes(temp)
    assert borefield.H == 100
    g_values = borefield.gfunction([6000, 60000, 600000])
    borefield.H = 100
    assert not np.array_equal(borefield.gfunction([6000, 60000, 600000]), g_values)

    borefield = Borefield()
    borefield.ground_data = data_ground_flux
    temp = [
        gt.boreholes.Borehole(100, 4, 0.075, 0, 0),
        gt.boreholes.Borehole(150, 4, 0.075, 10, 0),
        gt.boreholes.Borehole(50, 4, 0.075, 100, 0)
    ]
    borefield.borefield = gt.borefield.Borefield.from_boreholes(temp)
    assert borefield.H == 100
    temp = [
        gt.boreholes.Borehole(100, 4, 0.075, 0, 0),
        gt.boreholes.Borehole(100, 4, 0.075, 10, 0),
        gt.boreholes.Borehole(100, 4, 0.075, 100, 0)
    ]
    borefield.borefield = gt.borefield.Borefield.from_boreholes(temp)
    assert not np.array_equal(borefield.gfunction([6000, 60000, 600000]), g_values)


def test_load_duration(monkeypatch):
    borefield = Borefield()
    monkeypatch.setattr(plt, "show", lambda: None)
    borefield.ground_data = ground_data_constant
    borefield.borefield = copy.deepcopy(borefield_gt)
    load = HourlyBuildingLoad(efficiency_heating=10 ** 6, efficiency_cooling=10 * 66)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    borefield.load = load
    optimise_load_profile_power(borefield, load)
    optimise_load_profile_energy(borefield, load)


def test_optimise_load_profile_power(monkeypatch):
    borefield = Borefield()
    monkeypatch.setattr(plt, "show", lambda: None)
    borefield.ground_data = ground_data_constant
    borefield.borefield = copy.deepcopy(borefield_gt)
    load = HourlyBuildingLoad(efficiency_heating=10 ** 6, efficiency_cooling=10 * 66)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    load.simulation_period = 40
    secondary_borefield_load, external_load = optimise_load_profile_power(borefield, load)
    assert secondary_borefield_load.simulation_period == 40
    assert external_load.simulation_period == 40
    assert len(borefield.results.peak_extraction) == 0


def test_optimise_load_profile_power_multiyear(monkeypatch):
    # multiyear should also have a multiyear as output
    borefield = Borefield()
    monkeypatch.setattr(plt, "show", lambda: None)
    borefield.ground_data = ground_data_constant
    borefield.borefield = copy.deepcopy(borefield_gt)
    load = HourlyBuildingLoad(efficiency_heating=10 ** 6, efficiency_cooling=10 * 66)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    load_my = HourlyBuildingLoadMultiYear(load.hourly_heating_load_simulation_period,
                                          load.hourly_cooling_load_simulation_period)
    secundary_borefield_load, external_load = optimise_load_profile_power(borefield, load_my)
    assert borefield.load.simulation_period == 20
    assert secundary_borefield_load.simulation_period == 20
    assert external_load.simulation_period == 20
    assert len(borefield.results.peak_extraction) == 0


def test_optimise_load_profile_energy(monkeypatch):
    borefield = Borefield()
    monkeypatch.setattr(plt, "show", lambda: None)
    borefield.ground_data = ground_data_constant
    borefield.borefield = copy.deepcopy(borefield_gt)
    load = HourlyBuildingLoad(efficiency_heating=10 ** 6, efficiency_cooling=10 * 66)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    load.simulation_period = 40
    borefield_load, external_load = optimise_load_profile_energy(borefield, load)
    assert borefield_load.simulation_period == 40
    assert external_load.simulation_period == 40
    assert len(borefield.results.peak_extraction) == 0


def test_optimise_borefield_small_power(monkeypatch):
    borefield = Borefield()
    monkeypatch.setattr(plt, "show", lambda: None)
    borefield.ground_data = ground_data_constant
    borefield.create_rectangular_borefield(5, 1, 6, 6, 100)
    load = HourlyBuildingLoad(efficiency_heating=10 ** 6, efficiency_cooling=10 * 66)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    load.simulation_period = 40
    secundary_borefield_load, external_load = optimise_load_profile_power(borefield, load)
    assert secundary_borefield_load.simulation_period == 40
    assert external_load.simulation_period == 40


def test_optimise_borefield_small_energy(monkeypatch):
    borefield = Borefield()
    monkeypatch.setattr(plt, "show", lambda: None)
    borefield.ground_data = ground_data_constant
    borefield.create_rectangular_borefield(5, 1, 6, 6, 100)
    load = HourlyBuildingLoad(efficiency_heating=10 ** 6, efficiency_cooling=10 * 66)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    load.simulation_period = 40
    optimise_load_profile_energy(borefield, load)
    assert borefield.load.simulation_period == 20


def test_optimise_borefield_wrong_threshold_power(monkeypatch):
    borefield = Borefield()
    monkeypatch.setattr(plt, "show", lambda: None)
    borefield.ground_data = ground_data_constant
    borefield.create_rectangular_borefield(5, 1, 6, 6, 100)
    load = HourlyBuildingLoad(efficiency_heating=10 ** 6, efficiency_cooling=10 * 66)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    load.simulation_period = 40
    with pytest.raises(ValueError):
        optimise_load_profile_power(borefield, load, temperature_threshold=-0.5)


def test_optimise_borefield_wrong_threshold_energy(monkeypatch):
    borefield = Borefield()
    monkeypatch.setattr(plt, "show", lambda: None)
    borefield.ground_data = ground_data_constant
    borefield.create_rectangular_borefield(5, 1, 6, 6, 100)
    load = HourlyBuildingLoad(efficiency_heating=10 ** 6, efficiency_cooling=10 * 66)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    load.simulation_period = 40
    with pytest.raises(ValueError):
        optimise_load_profile_energy(borefield, load, temperature_threshold=-0.5)


def test_calculate_quadrants_without_data():
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    borefield.set_max_fluid_temperature(18)
    borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(2))
    borefield.ground_data = ground_data_constant
    borefield.calculate_quadrant()


def test_optimise_load_profile_power_without_data():
    borefield = Borefield()
    with pytest.raises(ValueError):
        optimise_load_profile_power(borefield, MonthlyGeothermalLoadAbsolute())


def test_optimise_load_profile_energy_without_data():
    borefield = Borefield()
    with pytest.raises(ValueError):
        optimise_load_profile_energy(borefield, MonthlyGeothermalLoadAbsolute())


def test_optimise_load_profile_balance_errors():
    borefield = Borefield()
    with pytest.raises(ValueError):
        optimise_load_profile_balance(borefield, MonthlyGeothermalLoadAbsolute())
    load = HourlyBuildingLoad(efficiency_heating=10 ** 6, efficiency_cooling=10 * 66)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    with pytest.raises(ValueError):
        optimise_load_profile_balance(borefield, load, temperature_threshold=-0.5)
    with pytest.raises(ValueError):
        optimise_load_profile_balance(borefield, load, imbalance_factor=-0.5)


def test_load_load():
    borefield1 = Borefield()
    borefield2 = Borefield()

    load = MonthlyGeothermalLoadAbsolute(*load_case(1))
    borefield2.load = load
    borefield1.set_load(load)
    assert borefield1.load is borefield2.load


def test_calculate_temperature_profile():
    borefield = Borefield()
    borefield.ground_data = ground_data_constant
    load = MonthlyGeothermalLoadAbsolute(*load_case(1))
    borefield.load = load
    with pytest.raises(ValueError):
        borefield.calculate_temperatures(hourly=True)


def test_optimise_load_profile_power_without_hourly_data():
    borefield = Borefield()
    borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(1))
    with pytest.raises(ValueError):
        optimise_load_profile_power(borefield, borefield.load)
    borefield.load = HourlyBuildingLoad()
    borefield.ground_data = ground_data_constant
    borefield.load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    borefield.create_rectangular_borefield(10, 10, 6, 6, 150)
    optimise_load_profile_power(borefield, borefield.load)


def test_optimise_load_profile_energy_without_hourly_data():
    borefield = Borefield()
    borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(1))
    with pytest.raises(ValueError):
        optimise_load_profile_energy(borefield, borefield.load)
    borefield.load = HourlyBuildingLoad()
    borefield.ground_data = ground_data_constant
    borefield.load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    borefield.create_rectangular_borefield(10, 10, 6, 6, 150)
    optimise_load_profile_energy(borefield, borefield.load)


@pytest.mark.parametrize(
    "H, result",
    zip(
        range(110, 130, 1),
        [
            122.99210426454648, 122.99135446500962, 122.99135409065917, 122.99135403971272,
            122.99135403719148, 122.9913540367823, 122.99135403674013, 122.99135403673134,
            122.99221686744185, 122.99217229220649, 122.99135553171544, 122.99220727438545,
            122.99477143007601, 122.9921794642058, 122.99220615327106, 122.99221262582992,
            122.99221900364599, 122.9922252887964, 122.99223148329897, 122.99223758911434,
        ],
    ),
)
def test_effect_H_init(H, result):
    borefield = Borefield()
    borefield.ground_data = GroundConstantTemperature(3, 11)
    borefield.create_rectangular_borefield(10, 5, 7, 7, 100, 0.75)
    load = MonthlyGeothermalLoadAbsolute(*load_case(1))
    borefield.load = load
    borefield.calculation_setup(H_init=H)
    assert np.isclose(borefield.size(), result)
    borefield = Borefield()
    borefield.ground_data = GroundConstantTemperature(3, 11)
    borefield.create_rectangular_borefield(10, 5, 7, 7, 100, 0.75)
    load = MonthlyGeothermalLoadAbsolute(*load_case(1))
    borefield.load = load
    assert np.isclose(borefield.size(H_init=H), result)


def test_depth_convergence():
    borefield = Borefield()
    borefield.calculation_setup(atol=1, rtol=0.01, max_nb_of_iterations=10)
    with pytest.raises(RuntimeError):
        borefield._check_convergence(10, 12, 10)

    assert borefield._check_convergence(10, 10, 1)
    assert not borefield._check_convergence(10, 10.5, 1)
    assert borefield._check_convergence(10, 10.001, 1)
    assert not borefield._check_convergence(10000, 10002, 1)


def test_calculate_next_depth_deep_sizing():
    borefield = Borefield()
    borefield.ground_data = GroundFluxTemperature(3, 10)
    borefield.create_rectangular_borefield(10, 5, 7, 7, 100, 0.75)
    load = MonthlyGeothermalLoadAbsolute(*load_case(1))
    borefield.load = load

    borefield.calculate_temperatures(75)
    assert np.isclose(borefield.calculate_next_depth_deep_sizing(75), 118.26269556337864)
    borefield.calculate_temperatures(118.26269556337864)
    assert np.isclose(borefield.calculate_next_depth_deep_sizing(118.26269556337864), 128.6225651998528)
    borefield.calculate_temperatures(128.6225651998528)
    assert np.isclose(borefield.calculate_next_depth_deep_sizing(128.6225651998528), 131.41962184720694)


@pytest.mark.parametrize("case, result",
                         zip((1, 2, 3, 4), [132.49024176019665, 0, 140.31290724434433, 132.49024176019665]))
def test_deep_sizing(case, result):
    borefield = Borefield()
    borefield.ground_data = GroundFluxTemperature(3, 10)
    borefield.create_rectangular_borefield(10, 5, 7, 7, 100, 0.75)
    load = MonthlyGeothermalLoadAbsolute(*load_case(case))
    borefield.load = load

    assert np.allclose(result, borefield._size_based_on_temperature_profile(10, deep_sizing=True)[0])

    borefield = Borefield()
    borefield.ground_data = GroundFluxTemperature(3, 10)
    borefield.create_rectangular_borefield(10, 5, 7, 7, 100, 0.75)
    load = MonthlyGeothermalLoadAbsolute(*load_case(case))
    borefield.load = load

    # methods should more or less lead to the same results, 1% diff taken as a reference
    assert np.allclose(result, borefield._size_based_on_temperature_profile(10, deep_sizing=False)[0], rtol=0.01)


def test_depreciation_warning():
    with pytest.raises(ValueError):
        Borefield(baseload_heating=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])


def test_optimise_load_borefield():
    load = HourlyBuildingLoad()
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
    load.simulation_period = 10
    borefield = Borefield(load=load)
    borefield.set_min_fluid_temperature(2)
    borefield.set_max_fluid_temperature(17)
    borefield.borefield = gt.borefield.Borefield.rectangle_field(20, 4, 6, 6, 150, 1, 0.07)
    borefield.Rb = 0.1699
    ground_data = GroundFluxTemperature(2, 9.6, flux=0.07)
    borefield.ground_data = ground_data
    borefield_load, external_load = optimise_load_profile_energy(borefield, load)
    assert np.isclose(borefield_load.imbalance, -229270.593357212)
    borefield.load = borefield_load
    borefield.calculate_temperatures(hourly=False)
    assert np.isclose(np.max(borefield.results.peak_injection), 17.066534473125756)
    assert np.isclose(np.min(borefield.results.peak_extraction), 1.9451431947563664)
    assert np.isclose(borefield.load.max_peak_cooling, 329.9393053)
    assert np.isclose(np.sum(borefield.load.hourly_heating_load), 593960.7811708137)
    load.peak_extraction_duration = 10
    borefield_load_, external_load = optimise_load_profile_energy(borefield, load)
    assert not borefield_load == borefield_load_
    assert np.isclose(borefield_load_.peak_extraction_duration, 3600 * 10)


def test_repr_():
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(3))
    borefield.ground_data = ground_data_constant

    assert {'Average borehole depth [m]': 114.0,
            'Average borehole length [m]': 110.0,
            'Average buried depth [m]': 4.0,
            'Borehole data': {'Rb': 0.12},
            'Borehole diameter [mm]': 149.99999999999997,
            'Ground data': {'Conductivity [W/(m·K)]': 3,
                            'Ground temperature at infinity [°C]': 10,
                            'Volumetric heat capacity [MJ/(m³·K)]': 2.4,
                            'type': 'Constant ground temperature'},
            'Load data': {'First month of simulation [-]': 1,
                          'Peak extraction duration [hour]': 6.0,
                          'Peak injection duration [hour]': 6.0,
                          'Simulation period [year]': 20,
                          'load': {1: {'Baseload extraction [kWh]': 24800.0,
                                       'Baseload injection [kWh]': 6000.0,
                                       'Peak extraction [kW]': 300.0,
                                       'Peak injection [kW]': 8.219178082191782},
                                   2: {'Baseload extraction [kWh]': 23680.0,
                                       'Baseload injection [kWh]': 12000.0,
                                       'Peak extraction [kW]': 266.25,
                                       'Peak injection [kW]': 16.438356164383563},
                                   3: {'Baseload extraction [kWh]': 20000.0,
                                       'Baseload injection [kWh]': 12000.0,
                                       'Peak extraction [kW]': 191.25,
                                       'Peak injection [kW]': 16.438356164383563},
                                   4: {'Baseload extraction [kWh]': 15840.0,
                                       'Baseload injection [kWh]': 12000.0,
                                       'Peak extraction [kW]': 103.125,
                                       'Peak injection [kW]': 16.438356164383563},
                                   5: {'Baseload extraction [kWh]': 10240.0,
                                       'Baseload injection [kWh]': 18000.0,
                                       'Peak extraction [kW]': 14.027397260273972,
                                       'Peak injection [kW]': 24.65753424657534},
                                   6: {'Baseload extraction [kWh]': 0.0,
                                       'Baseload injection [kWh]': 24000.0,
                                       'Peak extraction [kW]': 0.0,
                                       'Peak injection [kW]': 32.87671232876713},
                                   7: {'Baseload extraction [kWh]': 0.0,
                                       'Baseload injection [kWh]': 48000.0,
                                       'Peak extraction [kW]': 0.0,
                                       'Peak injection [kW]': 65.75342465753425},
                                   8: {'Baseload extraction [kWh]': 0.0,
                                       'Baseload injection [kWh]': 48000.0,
                                       'Peak extraction [kW]': 0.0,
                                       'Peak injection [kW]': 65.75342465753425},
                                   9: {'Baseload extraction [kWh]': 9760.0,
                                       'Baseload injection [kWh]': 24000.0,
                                       'Peak extraction [kW]': 75.75,
                                       'Peak injection [kW]': 32.87671232876713},
                                   10: {'Baseload extraction [kWh]': 13919.999999999998,
                                        'Baseload injection [kWh]': 18000.0,
                                        'Peak extraction [kW]': 159.375,
                                        'Peak injection [kW]': 24.65753424657534},
                                   11: {'Baseload extraction [kWh]': 18720.000000000004,
                                        'Baseload injection [kWh]': 12000.0,
                                        'Peak extraction [kW]': 223.125,
                                        'Peak injection [kW]': 16.438356164383563},
                                   12: {'Baseload extraction [kWh]': 23040.0,
                                        'Baseload injection [kWh]': 6000.0,
                                        'Peak extraction [kW]': 255.0,
                                        'Peak injection [kW]': 8.219178082191782}},
                          'type': 'Monthly geothermal load'},
            'Maximum average fluid temperature [°C]': 16.0,
            'Minimum average fluid temperature [°C]': 0.0,
            'Number of boreholes [-]': 120} == borefield.__export__()


def test_with_titled_borefield():
    # define params
    ground_data = GroundFluxTemperature(1.9, 10)
    pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    fluid_data = TemperatureDependentFluidData('MPG', 30).create_constant(2)
    load_data = MonthlyBuildingLoadAbsolute(
        np.array([.176, .174, .141, .1, .045, 0, 0, 0, 0.012, 0.065, 0.123, 0.164]) * 8 * 1350,
        np.array([0, 0, 0, 0, .112, .205, .27, .264, .149, 0, 0, 0]) * 4 * 700,
        np.array([1, .991, .802, .566, .264, 0, 0, 0, .0606, .368, .698, .934]) * 8,
        np.array([0, 0, 0, 0, .415, .756, 1, .976, .549, 0, 0, 0]) * 4
    )

    # define borefield
    borefield_tilted = gt.borefield.Borefield.from_boreholes(
        [gt.boreholes.Borehole(150, 0.75, 0.07, -3, 0, math.pi / 7, orientation=math.pi),
         gt.boreholes.Borehole(150, 0.75, 0.07, 3, 0, math.pi / 7, orientation=0)])

    # initiate GHEtool object with tilted borefield
    borefield = Borefield(borefield=borefield_tilted, load=load_data)
    borefield.ground_data = ground_data
    borefield.pipe_data = pipe_data
    borefield.fluid_data = fluid_data
    borefield.flow_data = ConstantFlowRate(mfr=0.2)
    borefield.set_max_fluid_temperature(17)

    assert np.isclose(borefield.depth, 150 * math.cos(math.pi / 7) + 0.75)
    assert np.isclose(borefield.ground_data.calculate_Tg(borefield.depth, borefield.D), 12.157557845032045)

    assert np.isclose(borefield.size_L3(), 111.5821049845363)


def test_Rb_and_Re_with_temperture_dep_data():
    ground_data = GroundFluxTemperature(1.9, 10)
    pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    flow_data = ConstantFlowRate(vfr=0.2, series_factor=2)
    fluid_data = TemperatureDependentFluidData('MPG', 30)
    load_data = MonthlyBuildingLoadAbsolute(
        np.array([.176, .174, .141, .1, .045, 0, 0, 0, 0.012, 0.065, 0.123, 0.164]) * 8 * 1350,
        np.array([0, 0, 0, 0, .112, .205, .27, .264, .149, 0, 0, 0]) * 4 * 700,
        np.array([1, .991, .802, .566, .264, 0, 0, 0, .0606, .368, .698, .934]) * 8,
        np.array([0, 0, 0, 0, .415, .756, 1, .976, .549, 0, 0, 0]) * 4
    )

    borefield = Borefield(ground_data=ground_data, pipe_data=pipe_data, fluid_data=fluid_data, flow_data=flow_data,
                          load=load_data)

    borefield.create_rectangular_borefield(4, 1, 7, 7, 100, 1, 0.075)
    assert np.isclose(borefield.Re, 709.7715066160362)
    assert np.isclose(borefield.Rb, 0.15719115050343702)

    borefield.calculate_temperatures()
    assert np.isclose(borefield.Re, 949.0513333574957)
    assert np.isclose(borefield.Rb, 0.15660083491337237)

    borefield = Borefield(ground_data=ground_data, pipe_data=pipe_data, fluid_data=fluid_data, flow_data=flow_data,
                          load=load_data)
    borefield.borehole.flow_data = ConstantFlowRate(vfr=0.8, flow_per_borehole=False)
    borefield.create_rectangular_borefield(4, 1, 7, 7, 100, 1, 0.075)
    assert np.isclose(borefield.Re, 709.7715066160362)
    assert np.isclose(borefield.Rb, 0.15719115050343702)

    borefield.calculate_temperatures()
    assert np.isclose(borefield.Re, 949.0513333574957)
    assert np.isclose(borefield.Rb, 0.15660083491337237)

    borefield = Borefield(ground_data=ground_data, pipe_data=pipe_data, fluid_data=fluid_data, flow_data=flow_data,
                          load=load_data)
    borefield.borehole.flow_data = ConstantFlowRate(vfr=0.4, flow_per_borehole=False, series_factor=2)
    borefield.create_rectangular_borefield(4, 1, 7, 7, 100, 1, 0.075)
    assert np.isclose(borefield.Re, 709.7715066160362)
    assert np.isclose(borefield.Rb, 0.15719115050343702)

    borefield.calculate_temperatures()
    assert np.isclose(borefield.Re, 949.0513333574957)
    assert np.isclose(borefield.Rb, 0.15660083491337237)


def test_inlet_outlet_temperatures():
    borefield = Borefield()
    with pytest.raises(TypeError):
        borefield.calculate_borefield_inlet_outlet_temperature(10, 5)
    borefield.create_rectangular_borefield(1, 1, 6, 6, 100)
    borefield.borehole.pipe_data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 2)
    borefield.borehole.fluid_data = ConstantFluidData(0.5, 1200, 4000, 0.001)
    borefield.borehole.flow_data = ConstantFlowRate(mfr=1)
    borefield.borehole.use_constant_Rb = False

    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(10, 0), (1.25, -1.25))
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(np.array([5, 10]), 0),
                       ((0.625, 1.25), (-0.625, -1.25)))
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(10, np.array([0, 1])),
                       ((1.25, 2.25), (-1.25, -0.25)))
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(np.array([5, 10]), np.array([0, 1])),
                       ((0.625, 2.25), (-0.625, -0.25)))
    borefield.borehole.flow_data = ConstantFlowRate(mfr=2, series_factor=2)
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(10, 0), (1.25, -1.25))
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(np.array([5, 10]), 0),
                       ((0.625, 1.25), (-0.625, -1.25)))
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(10, np.array([0, 1])),
                       ((1.25, 2.25), (-1.25, -0.25)))
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(np.array([5, 10]), np.array([0, 1])),
                       ((0.625, 2.25), (-0.625, -0.25)))

    borefield.borehole.flow_data = ConstantFlowRate(mfr=1, flow_per_borehole=False)
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(10, 0), (1.25, -1.25))
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(np.array([5, 10]), 0),
                       ((0.625, 1.25), (-0.625, -1.25)))
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(10, np.array([0, 1])),
                       ((1.25, 2.25), (-1.25, -0.25)))
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(np.array([5, 10]), np.array([0, 1])),
                       ((0.625, 2.25), (-0.625, -0.25)))
    borefield.create_rectangular_borefield(4, 1, 6, 6, 100)
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(10, 0), (1.25, -1.25))
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(np.array([5, 10]), 0),
                       ((0.625, 1.25), (-0.625, -1.25)))
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(10, np.array([0, 1])),
                       ((1.25, 2.25), (-1.25, -0.25)))
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(np.array([5, 10]), np.array([0, 1])),
                       ((0.625, 2.25), (-0.625, -0.25)))
    borefield.borehole.flow_data = ConstantFlowRate(mfr=1, flow_per_borehole=False, series_factor=2)
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(10, 0), (1.25, -1.25))
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(np.array([5, 10]), 0),
                       ((0.625, 1.25), (-0.625, -1.25)))
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(10, np.array([0, 1])),
                       ((1.25, 2.25), (-1.25, -0.25)))
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(np.array([5, 10]), np.array([0, 1])),
                       ((0.625, 2.25), (-0.625, -0.25)))

    borefield.create_rectangular_borefield(1, 1, 6, 6, 100)
    borefield.borehole.flow_data = ConstantFlowRate(vfr=1)
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(np.array([5, 10]), np.array([0, 1])),
                       ((0.52083333, 2.04166667), (-0.52083333, -0.04166667)))  # equal since rho is equal
    borefield.borehole.fluid_data = TemperatureDependentFluidData('MEG', 25)
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(np.array([5, 10]), np.array([0, 1])),
                       ((0.64067241, 2.28081611), (-0.64067241, -0.28081611)))
    borefield.create_rectangular_borefield(2, 1, 6, 6, 100)
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(np.array([5, 10]), np.array([0, 1])),
                       ((0.3203362, 1.64040806), (-0.3203362, 0.35959194)))
    borefield.borehole.flow_data = ConstantFlowRate(vfr=1, flow_per_borehole=False)
    borefield.borehole.fluid_data = ConstantFluidData(0.5, 1200, 4000, 0.001)
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(np.array([5, 10]), np.array([0, 1])),
                       ((0.52083333, 2.04166667), (-0.52083333, -0.04166667)))  # equal since rho is equal
    borefield.borehole.fluid_data = TemperatureDependentFluidData('MEG', 25)
    assert np.allclose(borefield.calculate_borefield_inlet_outlet_temperature(np.array([5, 10]), np.array([0, 1])),
                       ((0.64067241, 2.28081611), (-0.64067241, -0.28081611)))


def test_size_inlet_outlet_l2():
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    load = MonthlyGeothermalLoadAbsolute(*load_case(3))
    borefield.ground_data = GroundConstantTemperature(2, 10)
    borefield.fluid_data = ConstantFluidData(0.5, 1200, 4000, 0.001)
    borefield.flow_data = ConstantFlowRate(mfr=1)
    borefield.pipe_data = pipeData
    borefield.calculation_setup(use_constant_Rb=False, interpolate_gfunctions=False, atol=0.0005)

    # extraction
    th, _, tcm, qh, qpm, qm = load._calculate_first_year_params(True)
    borefield.calculation_setup(size_based_on='inlet')
    size_inlet = borefield._Carcel(th, tcm, qh, qpm, qm, 0)
    borefield.calculation_setup(size_based_on='outlet')
    size_outlet = borefield._Carcel(th, tcm, qh, qpm, qm, 0)
    borefield.calculation_setup(size_based_on='average')
    delta_T = qh / 1000 / (borefield.fluid_data.cp() / 1000 * borefield.flow_data.mfr() * borefield.number_of_boreholes)
    assert np.isclose(size_inlet, borefield._Carcel(th, tcm, qh, qpm, qm, delta_T / 2))
    assert np.isclose(size_outlet, borefield._Carcel(th, tcm, qh, qpm, qm, -delta_T / 2))

    # injection
    th, _, tcm, qh, qpm, qm = load._calculate_first_year_params(False)
    borefield.calculation_setup(size_based_on='inlet')
    size_inlet = borefield._Carcel(th, tcm, qh, qpm, qm, 0)
    borefield.calculation_setup(size_based_on='outlet')
    size_outlet = borefield._Carcel(th, tcm, qh, qpm, qm, 0)
    borefield.calculation_setup(size_based_on='average')
    delta_T = qh / 1000 / (borefield.fluid_data.cp() / 1000 * borefield.flow_data.mfr() * borefield.number_of_boreholes)
    assert np.isclose(size_inlet, borefield._Carcel(th, tcm, qh, qpm, qm, delta_T / 2))
    assert np.isclose(size_outlet, borefield._Carcel(th, tcm, qh, qpm, qm, -delta_T / 2))

    # extraction
    th, qh, qm, qa = load._calculate_last_year_params(True)
    borefield.calculation_setup(size_based_on='inlet')
    size_inlet = borefield._Ahmadfard(th, qh, qm, qa, 0)
    borefield.calculation_setup(size_based_on='outlet')
    size_outlet = borefield._Ahmadfard(th, qh, qm, qa, 0)
    borefield.calculation_setup(size_based_on='average')
    delta_T = qh / 1000 / (borefield.fluid_data.cp() / 1000 * borefield.flow_data.mfr() * borefield.number_of_boreholes)
    assert np.isclose(size_inlet, borefield._Ahmadfard(th, qh, qm, qa, delta_T / 2))
    assert np.isclose(size_outlet, borefield._Ahmadfard(th, qh, qm, qa, -delta_T / 2))

    # injection
    th, qh, qm, qa = load._calculate_last_year_params(False)
    borefield.calculation_setup(size_based_on='inlet')
    size_inlet = borefield._Ahmadfard(th, qh, qm, qa, 0)
    borefield.calculation_setup(size_based_on='outlet')
    size_outlet = borefield._Ahmadfard(th, qh, qm, qa, 0)
    borefield.calculation_setup(size_based_on='average')
    delta_T = qh / 1000 / (borefield.fluid_data.cp() / 1000 * borefield.flow_data.mfr() * borefield.number_of_boreholes)
    assert np.isclose(size_inlet, borefield._Ahmadfard(th, qh, qm, qa, delta_T / 2))
    assert np.isclose(size_outlet, borefield._Ahmadfard(th, qh, qm, qa, -delta_T / 2))


def test_plot_inlet_outlet(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    borefield = Borefield()
    borefield.borefield = copy.deepcopy(borefield_gt)
    load = MonthlyGeothermalLoadAbsolute(*load_case(3))
    borefield.ground_data = GroundConstantTemperature(2, 10)
    borefield.fluid_data = ConstantFluidData(0.5, 1200, 4000, 0.001)
    borefield.flow_data = ConstantFlowRate(mfr=1)
    borefield.pipe_data = pipeData
    borefield.load = load
    borefield.calculation_setup(use_constant_Rb=False, interpolate_gfunctions=False, atol=0.0005)
    borefield.print_temperature_profile(type='inlet')
    borefield.print_temperature_profile(type='outlet')

    borefield.load = HourlyGeothermalLoad(np.full(8760, 1), np.full(8760, 2))
    borefield.print_temperature_profile(type='inlet', plot_hourly=True)
    borefield.print_temperature_profile(type='outlet', plot_hourly=True)
