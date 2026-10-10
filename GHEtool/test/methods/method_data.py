"""
This document contains all the method data used in the test_methods document.
"""
import copy

import numpy as np
import pygfunction as gt

from GHEtool.test.methods.TestMethodClass import *
from GHEtool import *
from GHEtool.Validation.cases import load_case
from GHEtool.VariableClasses.BaseClass import UnsolvableDueToTemperatureGradient, MaximumNumberOfIterations

list_of_test_objects = TestMethodClass()

# Case 1 from main_functionalities
data = GroundConstantTemperature(3, 10)
peak_injection = np.array([0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.])
peak_extraction = np.array([160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.])
annual_extraction_load = 300 * 10 ** 3
annual_injection_load = 160 * 10 ** 3
monthly_load_extraction_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
monthly_load_injection_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
monthly_load_extraction = annual_extraction_load * monthly_load_extraction_percentage
monthly_load_injection = annual_injection_load * monthly_load_injection_percentage
load = MonthlyGeothermalLoadAbsolute(monthly_load_extraction, monthly_load_injection, peak_extraction, peak_injection)
borefield = Borefield(load=load)
borefield.Rb = 0.2
borefield.ground_data = data
borefield.create_rectangular_borefield(10, 12, 6, 6, 100, 4, 0.075)
borefield.set_max_fluid_temperature(16)
borefield.set_min_fluid_temperature(0)

list_of_test_objects.add(SizingObject(borefield, L2_output=92.07, L3_output=91.99, quadrant=1,
                                      name='Main functionalities (1)'))

fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
flow_data = ConstantFlowRate(mfr=0.2)
pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
borefield.fluid_data = fluid_data
borefield.flow_data = flow_data
borefield.pipe_data = pipe_data
borefield.calculation_setup(use_constant_Rb=False)

list_of_test_objects.add(SizingObject(borefield, L2_output=52.7, L3_output=52.73, quadrant=1,
                                      name='Main functionalities (2)'))

borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
list_of_test_objects.add(SizingObject(borefield, L2_output=69.412, L3_output=69.37579, quadrant=1,
                                      name='Main functionalities (2), MPG, variable'))
borefield.calculation_setup(approximate_req_depth=True)
list_of_test_objects.add(SizingObject(borefield, L2_output=69.412, L3_output=69.98618, quadrant=1,
                                      name='Main functionalities (2), MPG, variable, approx'))
borefield.calculation_setup(approximate_req_depth=False)
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25).create_constant(0)
list_of_test_objects.add(SizingObject(borefield, L2_output=70.0197, L3_output=69.98384673547854, quadrant=1,
                                      name='Main functionalities (2), MPG, fixed'))
borefield.fluid_data = fluid_data
borefield.calculation_setup(atol=False)
list_of_test_objects.add(SizingObject(borefield, L2_output=52.716, L3_output=52.741, quadrant=1,
                                      name='Main functionalities (2), no atol'))

borefield_gt = gt.borefield.Borefield.rectangle_field(10, 12, 6, 6, 110, 1, 0.075)
borefield = Borefield()
borefield.ground_data = data
borefield.Rb = 0.12
borefield.set_borefield(borefield_gt)
hourly_load = HourlyGeothermalLoad()
hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile.csv"), header=True,
                                separator=";", col_extraction=0, col_injection=1)
borefield.load = hourly_load

list_of_test_objects.add(SizingObject(borefield, L2_output=182.73, L3_output=182.656, L4_output=182.337, quadrant=1,
                                      name='Hourly profile (1)'))
borefield.pipe_data = pipe_data
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
list_of_test_objects.add(SizingObject(borefield, L2_output=182.73155, L3_output=182.655, L4_output=182.337, quadrant=1,
                                      name='Hourly profile (1), MPG, variable'))
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25).create_constant(0)
list_of_test_objects.add(SizingObject(borefield, L2_output=182.73155, L3_output=182.655, L4_output=182.337, quadrant=1,
                                      name='Hourly profile (1), MPG, constant'))
borefield.Rb = 0.12

peak_injection = np.array([0., 0, 3.4, 6.9, 13., 18., 21., 50., 16., 3.7, 0., 0.])  # Peak injection in kW
peak_extraction = np.array([60., 42., 10., 5., 0., 0., 0., 0., 4.4, 8.5, 19., 36.])  # Peak extraction in kW
annual_extraction_load = 30 * 10 ** 3  # kWh
annual_injection_load = 16 * 10 ** 3  # kWh
monthly_load_extraction_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
monthly_load_injection_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
monthly_load_extraction = annual_extraction_load * monthly_load_extraction_percentage  # kWh
monthly_load_injection = annual_injection_load * monthly_load_injection_percentage  # kWh
load = MonthlyGeothermalLoadAbsolute(monthly_load_extraction, monthly_load_injection, peak_extraction, peak_injection)
borefield = Borefield(load=load)
borefield.ground_data = data
borefield.Rb = 0.2
borefield.set_max_fluid_temperature(16)  # maximum temperature
borefield.set_min_fluid_temperature(0)  # minimum temperature
custom_field = gt.borefield.Borefield.L_shaped_field(N_1=4, N_2=5, B_1=5., B_2=5., H=100., D=4, r_b=0.05)
borefield.set_borefield(custom_field)

list_of_test_objects.add(SizingObject(borefield, L2_output=305.176, L3_output=306.898, quadrant=1,
                                      name='Custom config (1)'))

borefield_gt = gt.borefield.Borefield.rectangle_field(11, 11, 6, 6, 110, 1, 0.075)
peak_injection = np.array([0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.])  # Peak injection in kW
peak_extraction = np.array([160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.])  # Peak extraction in kW
annual_extraction_load = 150 * 10 ** 3  # kWh
annual_injection_load = 400 * 10 ** 3  # kWh
monthly_load_extraction_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
monthly_load_injection_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
monthly_load_extraction = annual_extraction_load * monthly_load_extraction_percentage  # kWh
monthly_load_injection = annual_injection_load * monthly_load_injection_percentage  # kWh
load = MonthlyGeothermalLoadAbsolute(monthly_load_extraction, monthly_load_injection, peak_extraction, peak_injection)
borefield = Borefield(load=load)
borefield.ground_data = data
borefield.set_borefield(borefield_gt)
borefield.Rb = 0.2
borefield.set_max_fluid_temperature(16)  # maximum temperature
borefield.set_min_fluid_temperature(0)  # minimum temperature

list_of_test_objects.add(SizingObject(borefield, L2_output=190.223, L3_output=195.8952, quadrant=2,
                                      name='Effect of borehole configuration (1)'))

borefield_gt = gt.borefield.Borefield.rectangle_field(6, 20, 6, 6, 110, 1, 0.075)
borefield.set_borefield(borefield_gt)

list_of_test_objects.add(SizingObject(borefield, L2_output=186.5208, L3_output=191.165, quadrant=2,
                                      name='Effect of borehole configuration (2)'))

data = GroundConstantTemperature(3.5, 10)
borefield_gt = gt.borefield.Borefield.rectangle_field(10, 12, 6.5, 6.5, 110, 4, 0.075)
correct_answers_L2 = (56.75, 117.223, 66.94, 91.266)
correct_answers_L3 = (56.771, 118.7118, 66.8693, 91.45876)
for i in (1, 2, 3, 4):
    load = MonthlyGeothermalLoadAbsolute(*load_case(i))
    borefield = Borefield(load=load)
    borefield.ground_data = data
    borefield.set_borefield(borefield_gt)
    borefield.Rb = 0.2
    borefield.set_max_fluid_temperature(16)
    borefield.set_min_fluid_temperature(0)
    list_of_test_objects.add(SizingObject(borefield, L2_output=correct_answers_L2[i - 1],
                                          L3_output=correct_answers_L3[i - 1], quadrant=i, name=f'BS2021 case {i}'))

correct_answers_L2 = (56.749, 117.223, 66.941, 91.266)
correct_answers_L3 = (56.770, 118.7118, 66.8693, 91.45876)
customField = gt.borefield.Borefield.rectangle_field(N_1=12, N_2=10, B_1=6.5, B_2=6.5, H=110., D=4, r_b=0.075)
for i in (1, 2, 3, 4):
    load = MonthlyGeothermalLoadAbsolute(*load_case(i))
    borefield = Borefield(load=load)
    borefield.ground_data = data
    borefield.set_borefield(customField)
    borefield.Rb = 0.2

    borefield.set_max_fluid_temperature(16)  # maximum temperature
    borefield.set_min_fluid_temperature(0)  # minimum temperature
    list_of_test_objects.add(SizingObject(borefield, L2_output=correct_answers_L2[i - 1],
                                          L3_output=correct_answers_L3[i - 1], quadrant=i,
                                          name=f'Custom field case {i}'))

data = GroundConstantTemperature(3, 10)
borefield = Borefield()
borefield.ground_data = data
borefield.Rb = 0.12
borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 1, 0.075)
hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile.csv"), header=True,
                                separator=";",
                                col_extraction=0, col_injection=1)
borefield.load = hourly_load
borefield.simulation_period = 100
list_of_test_objects.add(SizingObject(borefield, L2_output=285.476, L3_output=288.7084, L4_output=266.7272, quadrant=4,
                                      name=f'Sizing method comparison (Validation)'))

ground_data = GroundFluxTemperature(3, 10)
fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
flow_data = ConstantFlowRate(mfr=0.2)
pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
borefield = Borefield()
borefield.create_rectangular_borefield(5, 4, 6, 6, 110, 4, 0.075)
borefield.ground_data = ground_data
borefield.fluid_data = fluid_data
borefield.flow_data = flow_data
borefield.pipe_data = pipe_data
borefield.calculation_setup(use_constant_Rb=False)
borefield.set_max_fluid_temperature(17)
borefield.set_min_fluid_temperature(3)
hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/auditorium.csv"), header=True, separator=";",
                                col_injection=0, col_extraction=1)
borefield.load = hourly_load
list_of_test_objects.add(SizingObject(borefield, L2_output=142.001, L3_output=141.453, L4_output=103.761, quadrant=1,
                                      name='BS2023 Auditorium'))
borefield.set_max_fluid_temperature(19)
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
list_of_test_objects.add(
    SizingObject(borefield, L2_output=119.5189, L3_output=119.3097, L4_output=101.33915035063208, quadrant=1,
                 name='BS2023 Auditorium (MPG, Variable limit)'))
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
borefield.flow_data = VariableHourlyFlowRate(mfr=np.full(8760, 0.2))
list_of_test_objects.add(
    SizingObject(borefield, L4_output=101.33915035063208, quadrant=1,
                 name='BS2023 Auditorium (MPG, Variable limit, variable flow)'))
borefield.flow_data = ConstantFlowRate(mfr=0.2)
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25).create_constant(3)
list_of_test_objects.add(SizingObject(borefield, L2_output=121.0716, L3_output=120.8516, L4_output=102.7196, quadrant=1,
                                      name='BS2023 Auditorium (MPG, fixed limit)'))
borefield.calculation_setup(size_based_on='inlet')
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
borefield.set_max_fluid_temperature(23)
list_of_test_objects.add(
    SizingObject(borefield, L2_output=99.7214185133763, L3_output=99.59088033375507, L4_output=85.73751704134587,
                 quadrant=1,
                 name='BS2023 Auditorium (MPG, Variable limit, inlet)'))
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25).create_constant(3)
list_of_test_objects.add(
    SizingObject(borefield, L2_output=100.847412852, L3_output=100.70122075570458, L4_output=86.80658085033203,
                 quadrant=1,
                 name='BS2023 Auditorium (MPG, fixed limit, inlet)'))
borefield.calculation_setup(size_based_on='outlet')
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
list_of_test_objects.add(
    SizingObject(borefield, L2_output=64.38776970267729, L3_output=65.28538350504957, L4_output=60.942615648726196,
                 quadrant=4,
                 name='BS2023 Auditorium (MPG, Variable limit, outlet)'))
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25).create_constant(3)
list_of_test_objects.add(
    SizingObject(borefield, L2_output=64.19954433467, L3_output=65.28912237173243, L4_output=60.94524740941217,
                 quadrant=4,
                 name='BS2023 Auditorium (MPG, fixed limit, outlet)'))
borefield.calculation_setup(size_based_on='average')
borefield.fluid_data = fluid_data
borefield.set_max_fluid_temperature(17)
list_of_test_objects.add(SizingObject(borefield, L2_output=142.001, L3_output=141.453, L4_output=103.761, quadrant=1,
                                      name='BS2023 Auditorium (Variable limit)'))
borefield.calculation_setup(max_nb_of_iterations=2)
list_of_test_objects.add(SizingObject(borefield, error_L2=MaximumNumberOfIterations, error_L3=MaximumNumberOfIterations,
                                      error_L4=MaximumNumberOfIterations, quadrant=1,
                                      name='BS2023 Auditorium (max nb of iter)'))
borefield.calculation_setup(atol=False, max_nb_of_iterations=40)
list_of_test_objects.add(SizingObject(borefield, L2_output=141.286, L3_output=140.5628, L4_output=103.451, quadrant=1,
                                      name='BS2023 Auditorium (no atol)'))
borefield.calculation_setup(force_deep_sizing=True)
list_of_test_objects.add(SizingObject(borefield, L2_output=141.286, L3_output=140.4335, L4_output=103.4728, quadrant=1,
                                      name='BS2023 Auditorium (no atol, deep)'))
borefield.calculation_setup(force_deep_sizing=False)
borefield = Borefield()
borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
borefield.ground_data = ground_data
borefield.fluid_data = fluid_data
borefield.pipe_data = pipe_data
borefield.flow_data = flow_data
borefield.calculation_setup(use_constant_Rb=False)
borefield.set_max_fluid_temperature(17)
borefield.set_min_fluid_temperature(3)
hourly_load.simulation_period = 20
hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/office.csv"), header=True, separator=";",
                                col_injection=0, col_extraction=1)
borefield.load = hourly_load
list_of_test_objects.add(SizingObject(borefield, L2_output=113.955, L3_output=115.9884, L4_output=109.617, quadrant=2,
                                      name='BS2023 Office'))
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
list_of_test_objects.add(
    SizingObject(borefield, L2_output=169.373, L3_output=172.4350131073142, L4_output=160.68693020401176, quadrant=2,
                 name='BS2023 Office, (MPG, variable)'))
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25).create_constant(3)
list_of_test_objects.add(
    SizingObject(borefield, L2_output=172.41551490145127, L3_output=175.59628514322574, L4_output=163.5176, quadrant=2,
                 name='BS2023 Office, (MPG, fixed)'))
borefield.set_max_fluid_temperature(20)
borefield.calculation_setup(size_based_on='inlet')
list_of_test_objects.add(
    SizingObject(borefield, L2_output=137.801376, L3_output=139.60742073304235, L4_output=131.326824817385, quadrant=2,
                 name='BS2023 Office, (MPG, variable, inlet)'))
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25).create_constant(3)
list_of_test_objects.add(
    SizingObject(borefield, L2_output=137.8013763, L3_output=139.60742073304235, L4_output=131.326824817385,
                 quadrant=2,
                 name='BS2023 Office, (MPG, fixed, inlet)'))
borefield.set_max_fluid_temperature(17)
borefield.calculation_setup(size_based_on='outlet')
list_of_test_objects.add(
    SizingObject(borefield, L2_output=96.20402464, L3_output=97.21734710484408, L4_output=94.278108727, quadrant=2,
                 name='BS2023 Office, (MPG, variable, outlet)'))
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25).create_constant(3)
list_of_test_objects.add(
    SizingObject(borefield, L2_output=96.204024648, L3_output=97.21734710484408, L4_output=94.27810872711586,
                 quadrant=2,
                 name='BS2023 Office, (MPG, fixed, outlet)'))
borefield.calculation_setup(size_based_on='average')
borefield.fluid_data = fluid_data
borefield.calculation_setup(max_nb_of_iterations=5)
list_of_test_objects.add(SizingObject(borefield, error_L2=MaximumNumberOfIterations, error_L3=MaximumNumberOfIterations,
                                      error_L4=MaximumNumberOfIterations, quadrant=2,
                                      name='BS2023 Office (max nb of iter)'))
borefield.calculation_setup(deep_sizing=True)
list_of_test_objects.add(SizingObject(borefield, error_L2=MaximumNumberOfIterations, error_L3=MaximumNumberOfIterations,
                                      error_L4=MaximumNumberOfIterations, quadrant=2,
                                      name='BS2023 Office (max nb of iter, deep sizing)'))
borefield.calculation_setup(atol=False, max_nb_of_iterations=40)
list_of_test_objects.add(
    SizingObject(borefield, L2_output=113.739, L3_output=115.61944351365554, L4_output=109.2783, quadrant=2,
                 name='BS2023 Office (no atol)'))
borefield.calculation_setup(force_deep_sizing=True)
list_of_test_objects.add(
    SizingObject(borefield, L2_output=113.739, L3_output=115.62659508492692, L4_output=109.28426, quadrant=2,
                 name='BS2023 Office (no atol, deep)'))
borefield.calculation_setup(force_deep_sizing=False)

borefield.ground_data.Tg = 12
list_of_test_objects.add(
    SizingObject(borefield, error_L2=UnsolvableDueToTemperatureGradient, error_L3=UnsolvableDueToTemperatureGradient,
                 error_L4=UnsolvableDueToTemperatureGradient, quadrant=2,
                 name='BS2023 Office (unsolvable)'))
borefield.ground_data.Tg = 10

borefield = Borefield()
borefield.create_rectangular_borefield(15, 20, 6, 6, 110, 4, 0.075)
borefield.ground_data = ground_data
borefield.fluid_data = fluid_data
borefield.pipe_data = pipe_data
borefield.flow_data = flow_data
borefield.calculation_setup(use_constant_Rb=False)
borefield.set_max_fluid_temperature(17)
borefield.set_min_fluid_temperature(3)
hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/swimming_pool.csv"), header=True,
                                separator=";",
                                col_injection=0, col_extraction=1)
borefield.load = hourly_load
borefield2 = copy.deepcopy(borefield)
borefield2.flow_data = ConstantFlowRate(mfr=0.2 * 15 * 20, flow_per_borehole=False)
list_of_test_objects.add(SizingObject(borefield, L2_output=303.172, L3_output=308.303, L4_output=305.8658, quadrant=4,
                                      name='BS2023 Swimming pool'))
list_of_test_objects.add(SizingObject(borefield2, L2_output=303.172, L3_output=308.303, L4_output=305.8658, quadrant=4,
                                      name='BS2023 Swimming pool, borefield flow'))
borefield2.flow_data = ConstantFlowRate(mfr=0.2 * 15 * 10, flow_per_borehole=False, series_factor=2)
list_of_test_objects.add(SizingObject(borefield2, L2_output=303.172, L3_output=308.303, L4_output=305.8658, quadrant=4,
                                      name='BS2023 Swimming pool, borefield flow, series factor'))
borefield2.flow_data = ConstantFlowRate(mfr=0.2 * 15 * 20, flow_per_borehole=False)
borefield.calculation_setup(size_based_on='inlet')
borefield2.calculation_setup(size_based_on='inlet')
list_of_test_objects.add(
    SizingObject(borefield, L2_output=337.18203201720564, L3_output=342.0561260799836, L4_output=335.1396044,
                 quadrant=4, name='BS2023 Swimming pool, inlet'))
list_of_test_objects.add(
    SizingObject(borefield2, L2_output=337.18203201720564, L3_output=342.0561260799836, L4_output=335.1396044,
                 quadrant=4, name='BS2023 Swimming pool, inlet, borefield flow'))
borefield.calculation_setup(size_based_on='outlet')
list_of_test_objects.add(
    SizingObject(borefield, L2_output=272.6762852815378, L3_output=279.1327314039608, L4_output=280.309456, quadrant=4,
                 name='BS2023 Swimming pool, outlet'))
borefield2.calculation_setup(size_based_on='outlet')
list_of_test_objects.add(
    SizingObject(borefield2, L2_output=272.6762852815378, L3_output=279.1327314039608, L4_output=280.309456, quadrant=4,
                 name='BS2023 Swimming pool, outlet, borefield flow'))
borefield2.flow_data = ConstantFlowRate(mfr=0.2 * 15 * 10, flow_per_borehole=False, series_factor=2)
list_of_test_objects.add(
    SizingObject(borefield2, L2_output=247.11273341108404, L3_output=253.0698059707121, L4_output=256.82506752144457,
                 quadrant=4,
                 name='BS2023 Swimming pool, outlet, borefield flow, series factor'))
borefield.calculation_setup(size_based_on='average')
borefield.calculation_setup(atol=False, max_nb_of_iterations=40)
list_of_test_objects.add(SizingObject(borefield, L2_output=303.162, L3_output=308.4918, L4_output=306.0602, quadrant=4,
                                      name='BS2023 Swimming pool (no atol)'))
borefield.calculation_setup(force_deep_sizing=True)
# we expect the same values as hereabove, since quadrant 4 is limiting
list_of_test_objects.add(SizingObject(borefield, L2_output=303.162, L3_output=308.4918, L4_output=306.0602, quadrant=4,
                                      name='BS2023 Swimming pool (no atol, deep)'))
borefield.calculation_setup(force_deep_sizing=False)

ground_data_IKC = GroundFluxTemperature(2.3, 10.5, flux=2.85)
fluid_data_IKC = ConstantFluidData(0.5, 1021.7, 3919, 0.0033)
flow_data_IKC = ConstantFlowRate(mfr=0.2)
pipe_data_IKC = SingleUTube(2.3, 0.016, 0.02, 0.42, 0.04)
monthly_injection = np.array([0, 0, 740, 1850, 3700, 7400, 7400, 7400, 5550, 2220, 740, 0]) * (1 + 1 / 4.86)
monthly_extraction = np.array([20064, 17784, 16644, 13680, 0, 0, 0, 0, 0, 12540, 15618, 17670]) * (1 - 1 / 4.49)
peak_injection = np.array([61] * 12) * (1 + 1 / 4.86)
peak_extraction = np.array([57] * 12) * (1 - 1 / 4.49)
load = MonthlyGeothermalLoadAbsolute(monthly_extraction, monthly_injection, peak_extraction, peak_injection, 25)
borefield = Borefield(load=load)
borefield.create_rectangular_borefield(4, 5, 8, 8, 110, 0.8, 0.07)
borefield.ground_data = ground_data_IKC
borefield.fluid_data = fluid_data_IKC
borefield.flow_data = flow_data_IKC
borefield.pipe_data = pipe_data_IKC
borefield.calculation_setup(use_constant_Rb=False)
borefield.load.peak_duration = 10
borefield.set_max_fluid_temperature(25)
borefield.set_min_fluid_temperature(0)
list_of_test_objects.add(
    SizingObject(borefield, error_L2=UnsolvableDueToTemperatureGradient, error_L3=UnsolvableDueToTemperatureGradient,
                 name='Real case 1 (Error)'))
borefield.calculation_setup(max_nb_of_iterations=20)
list_of_test_objects.add(SizingObject(borefield, error_L2=RuntimeError, error_L3=UnsolvableDueToTemperatureGradient,
                                      name='Real case 1 (Error, max nb of iter)'))

ground_data_IKC = GroundFluxTemperature(2.3, 10.5, flux=2.3 * 2.85 / 100)
borefield.ground_data = ground_data_IKC
borefield.calculation_setup(max_nb_of_iterations=40)
list_of_test_objects.add(
    SizingObject(borefield, L2_output=74.312, L3_output=74.687, quadrant=4, name='Real case 1 (Correct)'))
borefield.calculation_setup(atol=False)
list_of_test_objects.add(
    SizingObject(borefield, L2_output=74.312, L3_output=74.701, quadrant=4, name='Real case 1 (Correct) (no atol)'))
borefield.calculation_setup(atol=0.05)
borefield.ground_data = ground_data_IKC
borefield.create_rectangular_borefield(2, 10, 8, 8, 60, 0.8, 0.07)
list_of_test_objects.add(SizingObject(borefield, L2_output=71.50, L3_output=71.8671, quadrant=4,
                                      name='Real case 2 (Correct)'))

peakCooling = [0] * 12
peakHeating = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]  # Peak extraction in kW
annualHeatingLoad = 300 * 10 ** 3  # kWh
monthlyLoadHeatingPercentage = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144]
monthlyLoadHeating = list(map(lambda x: x * annualHeatingLoad, monthlyLoadHeatingPercentage))  # kWh
monthlyLoadCooling = [0] * 12  # kWh
load = MonthlyGeothermalLoadAbsolute(monthlyLoadHeating, monthlyLoadCooling, peakHeating, peakCooling)
borefield = Borefield(load=load)
borefield.ground_data = data
borefield.create_rectangular_borefield(10, 12, 6, 6, 110, 4, 0.075)
borefield.set_max_fluid_temperature(16)
borefield.set_min_fluid_temperature(0)
list_of_test_objects.add(SizingObject(borefield, L2_output=81.205, L3_output=82.0381, quadrant=4,
                                      name='No injection L2/L3'))

peakCooling = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]  # Peak injection in kW
peakHeating = [0] * 12
annualCoolingLoad = 160 * 10 ** 3  # kWh
monthlyLoadCoolingPercentage = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]
monthlyLoadHeating = [0] * 12  # kWh
monthlyLoadCooling = list(map(lambda x: x * annualCoolingLoad, monthlyLoadCoolingPercentage))  # kWh
borefield = Borefield(
    load=MonthlyGeothermalLoadAbsolute(monthlyLoadHeating, monthlyLoadCooling, peakHeating, peakCooling))
borefield.ground_data = data
borefield.create_rectangular_borefield(10, 12, 6, 6, 110, 4, 0.075)
borefield.set_max_fluid_temperature(16)  # maximum temperature
borefield.set_min_fluid_temperature(0)  # minimum temperature
list_of_test_objects.add(SizingObject(borefield, L2_output=120.913, L3_output=123.3795, quadrant=2,
                                      name='No extraction L2/L3'))
borefield = Borefield()
borefield.ground_data = data
borefield.create_rectangular_borefield(10, 12, 6, 6, 110, 4, 0.075)
hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile.csv"))
borefield.load = hourly_load
borefield.load.hourly_injection_load = np.zeros(8760)
list_of_test_objects.add(SizingObject(borefield, L4_output=244.03137515188732, quadrant=4, name='No injection L4'))

hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile.csv"))
borefield.load = hourly_load
borefield.load.hourly_extraction_load = np.zeros(8760)
list_of_test_objects.add(SizingObject(borefield, L4_output=305.55338863384287, quadrant=2, name='No extraction L4'))

borefield = Borefield(load=MonthlyGeothermalLoadAbsolute(*load_case(2)))
borefield.ground_data = GroundFluxTemperature(3, 12)
borefield.create_rectangular_borefield(10, 12, 6, 6, 110, 4, 0.075)
borefield.set_Rb(0.2)
list_of_test_objects.add(
    SizingObject(borefield, error_L2=MaximumNumberOfIterations, error_L3=UnsolvableDueToTemperatureGradient,
                 quadrant=2, name='Cannot size'))
list_of_test_objects.add(SizingObject(borefield, error_L4=ValueError, quadrant=2, name='Cannot size L4'))

data = GroundConstantTemperature(3, 10)
borefield_gt = gt.borefield.Borefield.rectangle_field(10, 12, 6, 6, 110, 4, 0.075)
borefield = Borefield()
borefield.set_max_fluid_temperature(16)
borefield.set_min_fluid_temperature(0)
borefield.ground_data = data
borefield.set_Rb(0.2)
borefield.set_borefield(borefield_gt)
hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile.csv"))
borefield.load = hourly_load
temp = hourly_load.hourly_extraction_load
temp[0] = 100_000
borefield._borefield_load.hourly_extraction_load = temp
list_of_test_objects.add(
    SizingObject(borefield, L4_output=18760.64149089075, quadrant=4, name='Hourly profile, quadrant 4'))

hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile.csv"), col_injection=0,
                                col_extraction=1)
borefield.load = hourly_load
list_of_test_objects.add(
    SizingObject(borefield, L4_output=368.4794931300781, quadrant=2, name='Hourly profile reversed'))

temp = hourly_load.hourly_extraction_load
temp[0] = 100_000
borefield._borefield_load.hourly_extraction_load = temp
list_of_test_objects.add(
    SizingObject(borefield, L4_output=18602.210559679363, quadrant=3, name='Hourly profile, quadrant 3'))
hourly_load = HourlyBuildingLoad(efficiency_heating=10 ** 6, efficiency_cooling=10 ** 6)
hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile.csv"))
# set borefield depth to 150
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 87.40169379352756, 97.01606695298591,
                                                   305.11363277342565, 384.30906362851204,
                                                   230.92219811263652, 292.1075911801673,
                                                   name='Optimise load profile 1 (power)', power=1, hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 69.92875049500091, 87.84392629398803,
                                                   210.2407498208503, 246.69466980177307,
                                                   325.7951759381897, 429.72184739265003,
                                                   name='Optimise load profile 2 (power)', power=1, hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 50, 45.05159291166561, 63.84284656488144,
                                                   118.75160373942786, 117.95035244169365,
                                                   417.2844135088497, 558.4660360085409,
                                                   name='Optimise load profile 3 (power)', power=1, hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 87.4462324917588, 96.41100142865851,
                                                   305.4256058396145, 368.6450842954758,
                                                   230.6102247344743, 307.7715548492398,
                                                   name='Optimise load profile 1 (power, hourly)', power=1,
                                                   hourly=True))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 69.5291344428321, 86.87171070152701,
                                                   208.4600166152545, 238.3334848681924,
                                                   327.5759109245205, 438.08302396505417,
                                                   name='Optimise load profile 2 (power, hourly)', power=1,
                                                   hourly=True))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 50, 44.64342391291525, 63.24059679183192,
                                                   117.41457119133149, 115.95658459670314,
                                                   418.62144739397996, 560.4598018597655,
                                                   name='Optimise load profile 3 (power, hourly)', power=1,
                                                   hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 40.34662410772084, 95.92777544019569,
                                                   103.33961398049986, 357.1818703484314,
                                                   432.6964186797829, 319.23475733308175,
                                                   name='Optimise load profile 1 (balance)', power=3, hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 36.071187149488715, 85.76253446878265,
                                                   89.5783872904925, 229.40986139420548,
                                                   446.4576591310307, 447.0066385154265,
                                                   name='Optimise load profile 2 (balance)', power=3, hourly=False))

list_of_test_objects.add(
    OptimiseLoadProfileObject(borefield, hourly_load, 50, 25.727672470628615, 61.16988575728409,
                              58.81915615875205, 109.38667345029486,
                              477.21692102203303, 567.0297064362692,
                              name='Optimise load profile 3 (balance)', power=3, hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 40.114924501143015, 95.37688851171224,
                                                   102.58063934909933, 344.9700246379995,
                                                   433.4553940701588, 331.44659083168017,
                                                   name='Optimise load profile 1 (balance, hourly)', power=3,
                                                   hourly=True))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 35.77066502371268, 85.04801572938858,
                                                   88.63486696221385, 223.96201156696952,
                                                   447.4011804028306, 452.45448289481806,
                                                   name='Optimise load profile 2 (balance, hourly)', power=3,
                                                   hourly=True))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 50, 25.583203966066996, 60.82639872286041,
                                                   58.42998287268812, 108.33038018094643,
                                                   477.60609469727063, 568.0859986493253,
                                                   name='Optimise load profile 3 (balance, hourly)', power=3,
                                                   hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 94.71874758593957, 99.61418184090991,
                                                   536.035599963864, 673.684458993794, 209.51411978433754,
                                                   298.19863625473664,
                                                   name='Optimise load profile 1 (energy)', power=2))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 79.26537043636431, 96.80038419642045,
                                                   531.7630737363945, 468.0016563011883, 300.20920660323685,
                                                   423.969460923839,
                                                   name='Optimise load profile 2 (energy)', power=2))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 50, 52.517079533661416, 77.60187603103539,
                                                   268.8156054361622, 239.89969037483152, 390.3299545839425,
                                                   551.8504717910687,
                                                   name='Optimise load profile 3 (energy)', power=2))
temp_borehole = copy.deepcopy(borefield.borehole)
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
borefield.flow_data = ConstantFlowRate(vfr=0.3)
borefield.pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

borefield.borehole.use_constant_Rb = False

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 97.5918078816849, 99.97708241629543,
                                                   536.035599963864, 676.4169469162705, 173.10714970652015,
                                                   149.7220503430118,
                                                   name='Optimise load profile 1 (energy, var temp)', power=2))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 84.72690125386208, 99.67067780119245,
                                                   536.035599963864, 665.7761682755024, 272.83557499555667,
                                                   312.6283879506591,
                                                   name='Optimise load profile 2 (energy, var temp)', power=2))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 50, 60.04290903722156, 90.24461282113019,
                                                   363.6612104245367, 341.30984770950636, 363.5175103633432,
                                                   495.0006934523831,
                                                   name='Optimise load profile 3 (energy, var temp)', power=2))
borefield.USE_SPEED_UP_IN_SIZING = False
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 50, 60.04290903722156, 90.24461282113019,
                                                   363.6612104245367, 341.30984770950636, 363.5175103633432,
                                                   495.0006934523831,
                                                   name='Optimise load profile 3 (energy, var temp, no speed up)',
                                                   power=2))
borefield.USE_SPEED_UP_IN_SIZING = True
borefield.borehole = temp_borehole
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 67.621, 81.579,
                                                   200, 200, 336.036, 476.416,
                                                   name='Optimise load profile 1 (power, limit)', power=1,
                                                   hourly=False,
                                                   max_peak_heating=200, max_peak_cooling=200))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 67.621, 81.579,
                                                   200, 200, 336.036, 476.416,
                                                   name='Optimise load profile 1 (energy, limit)', power=2,
                                                   max_peak_heating=200, max_peak_cooling=200))
temp_borehole = copy.deepcopy(borefield.borehole)
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
borefield.flow_data = ConstantFlowRate(vfr=0.3)
borefield.pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
borefield.borehole.use_constant_Rb = False
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 67.621, 81.579,
                                                   200, 200, 336.036, 476.416,
                                                   name='Optimise load profile 1 (energy, limit, var temp)', power=2,
                                                   max_peak_heating=200, max_peak_cooling=200))
borefield.borehole = temp_borehole
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 9.958586636669834, 23.677447214261154,
                                                   20.842994441927324, 30.00003,
                                                   515.1931207150575, 646.4162705,
                                                   name='Optimise load profile 1 (balance, limit)', power=3,
                                                   hourly=False,
                                                   max_peak_heating=30, max_peak_cooling=30))
borefield.set_min_fluid_temperature(-5)
borefield.set_max_fluid_temperature(25)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 100, 100,
                                                   536.036, 676.417, 0, 0, name='Optimise load profile 100% (power)',
                                                   power=1, hourly=False))

list_of_test_objects.add(
    OptimiseLoadProfileObject(borefield, hourly_load, 150, 81.451, 95.049,
                              536.036 / 2, 676.417 / 2, 536.036 / 2, 676.417 / 2,
                              name='Optimise load profile 50% (power)',
                              power=1, hourly=False, max_peak_heating=536.036 / 2,
                              max_peak_cooling=676.417 / 2))
borefield.set_max_fluid_temperature(17)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 41.2696055085359, 98.12224782818228,
                                                   106.36300913778896, 422.1337620430212,
                                                   429.67302049909557, 254.2829305903187,
                                                   name='Optimise load profile 100% (balance)',
                                                   power=3, hourly=False))

list_of_test_objects.add(
    OptimiseLoadProfileObject(borefield, hourly_load, 150, 39.977067414497135, 95.04912072585488,
                              102.1290631333759, 338.20883820849997,
                              433.9069707374589, 338.2077705,
                              name='Optimise load profile 50% (balance)',
                              power=3, hourly=False, max_peak_heating=536.036 / 2,
                              max_peak_cooling=676.417 / 2))
borefield.set_max_fluid_temperature(25)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 100, 100,
                                                   536.036, 676.417, 0, 0,
                                                   name='Optimise load profile 100% (power, hourly)', power=1,
                                                   hourly=True))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 100, 100,
                                                   536.036, 676.417, 0, 0, name='Optimise load profile 100% (energy)',
                                                   power=2))

borefield.set_max_fluid_temperature(17)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 41.153796387565265, 97.84690108985943,
                                                   105.98365508449672, 410.8679947655677,
                                                   430.0523749317423, 265.5486866020162,
                                                   name='Optimise load profile 100% (balance, hourly)', power=3,
                                                   hourly=True))
borefield.set_max_fluid_temperature(25)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 81.451, 95.049,
                                                   536.036 / 2, 676.417 / 2, 536.036 / 2, 676.417 / 2,
                                                   name='Optimise load profile 50% (energy)',
                                                   power=2, max_peak_heating=536.036 / 2,
                                                   max_peak_cooling=676.417 / 2))

borefield = Borefield()
borefield.ground_data = data
borefield.set_Rb(0.2)
borefield.set_borefield(borefield_gt)
borefield.set_max_fluid_temperature(16)
borefield.set_min_fluid_temperature(0)
hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile.csv"), col_heating=1,
                                col_cooling=0)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.9738328260207, 66.33060176158988,
                                                   641.5806215052567, 194.66773405200593,
                                                   34.835007413480184, 341.36859661553353,
                                                   name='Optimise load profile 1, reversed (power)', power=1,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.97104380163456, 66.31564963906172,
                                                   639.0914749083714, 194.60626036942426,
                                                   37.324156499514515, 341.43007023664154,
                                                   name='Optimise load profile 1, reversed (power, hourly)', power=1,
                                                   hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.94743987959366, 42.03710175401808,
                                                   623.4262132112449, 108.8773018559599,
                                                   52.98943386191843, 427.15894302123314,
                                                   name='Optimise load profile 1, reversed (balance)', power=3,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.9516913262364, 42.038889878809854,
                                                   625.7028101449715, 108.88315919896134,
                                                   50.71283465159263, 427.15308568408904,
                                                   name='Optimise load profile 1, reversed (balance, hourly)', power=3,
                                                   hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.99940708216474, 73.57736516569348,
                                                   676.4155940837295, 483.8312541717402, 27.132862523716426,
                                                   329.33896937575713,
                                                   name='Optimise load profile 1, reversed (energy)', power=2))
temp_borehole = copy.deepcopy(borefield.borehole)
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
borefield.flow_data = ConstantFlowRate(vfr=0.3)
borefield.pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

borefield.borehole.use_constant_Rb = False

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 100, 80.34618612539653,
                                                   676.4155940837295, 536.036672036136, 0, 302.95742307616104,
                                                   name='Optimise load profile 1, reversed (energy, var temp)',
                                                   power=2))
borefield.borehole = temp_borehole
borefield.set_max_fluid_temperature(20)
borefield.set_min_fluid_temperature(4)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 96.93431051990653, 87.42894360094394,
                                                   382.0695108564542, 305.3051157324942,
                                                   294.34637757365283, 230.73132557231628,
                                                   name='Optimise load profile 2, reversed (power)', power=1,
                                                   hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 87.8792595562795, 69.89338154626415,
                                                   247.0098757984736, 210.08356205083408,
                                                   429.4061476914036, 325.9527840325179,
                                                   name='Optimise load profile 3, reversed (power)', power=1,
                                                   hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 96.30671722709224, 87.4326630254479,
                                                   366.1056203901484, 305.3311686400503,
                                                   310.3102840038651, 230.70527269081305,
                                                   name='Optimise load profile 2, reversed (power, hourly)', power=1,
                                                   hourly=True))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 86.79925366431937, 69.46560300637913,
                                                   237.7323914134255, 208.17732988122862,
                                                   438.68364135394535, 327.85901429589313,
                                                   name='Optimise load profile 3, reversed (power, hourly)', power=1,
                                                   hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 95.92780986016768, 40.34647719831484,
                                                   357.1819436549771, 103.33933943022109,
                                                   319.2339696627221, 432.69689990901503,
                                                   name='Optimise load profile 2, reversed (balance)', power=3,
                                                   hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 85.76259821569249, 36.071069676474174,
                                                   229.40989729493236, 89.57819305514214,
                                                   447.00614379494095, 446.4580325229614,
                                                   name='Optimise load profile 3, reversed (balance)', power=3,
                                                   hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 95.37692398776166, 40.11477896271139,
                                                   344.97010070607297, 102.5803677717572,
                                                   331.44582482348136, 433.45587080850805,
                                                   name='Optimise load profile 2, reversed (balance, hourly)', power=3,
                                                   hourly=True))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 85.04807784638385, 35.77054806725507,
                                                   223.9620230754433, 88.6346779140164,
                                                   452.45402346230964, 447.4015467205729,
                                                   name='Optimise load profile 3, reversed (balance, hourly)', power=3,
                                                   hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.61419014079208, 94.71863227032236,
                                                   673.6857354975243, 536.036672036136, 298.19769219583554,
                                                   209.51544203461776,
                                                   name='Optimise load profile 2, reversed (energy)', power=2))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 96.80042094108062, 79.26522526772645,
                                                   468.0007202988117, 531.7641372636054, 423.96883812064647,
                                                   300.2099900773207,
                                                   name='Optimise load profile 3, reversed (energy)', power=2))
temp_borehole = copy.deepcopy(borefield.borehole)
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
borefield.flow_data = ConstantFlowRate(vfr=0.3)
borefield.pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

borefield.borehole.use_constant_Rb = False

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.89659107091336, 99.22439328287719,
                                                   676.4155940837295, 536.036672036136, 223.1749427285772,
                                                   127.66202276900788,
                                                   name='Optimise load profile 2, reversed (energy, var temp)',
                                                   power=2))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 99.0944012608283, 88.79523111739012,
                                                   612.45587754351, 536.036672036136, 367.12472876854804,
                                                   247.40527747959175,
                                                   name='Optimise load profile 3, reversed (energy, var temp)',
                                                   power=2))
borefield.borehole = temp_borehole
borefield = Borefield()
borefield.create_rectangular_borefield(3, 6, 6, 6, 146, 4)
borefield.set_min_fluid_temperature(3)
borefield.set_max_fluid_temperature(16)
borefield.load.peak_duration = 6
load = HourlyBuildingLoad(efficiency_heating=4, efficiency_cooling=25)
load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/problem_data.csv"), col_heating=0,
                         col_cooling=1, header=True, decimal_seperator=',')
load.simulation_period = 40
borefield.load = load

borefield.ground_data = GroundTemperatureGradient(1.9, 10, gradient=2)
borefield.fluid_data = ConstantFluidData(0.475, 1033, 3930, 0.001)
borefield.flow_data = ConstantFlowRate(mfr=0.1)
borefield.pipe_data = SingleUTube(1.5, 0.016, 0.02, 0.42, 0.04)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 81.95005802079557, 86.9370565131668,
                                                   22.455055991481615, 38.143544140022456,
                                                   55.07480115469119, 59.723824559978404,
                                                   name='Optimise load profile (stuck in loop) (power)', power=1,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 80.86242505959412, 84.43394210953802,
                                                   21.907719129593865, 35.57989215451865,
                                                   55.80458363720819, 62.188874546039756,
                                                   name='Optimise load profile (stuck in loop) (power, hourly)',
                                                   power=1, hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 29.82548099571232, 82.38510944782531,
                                                   5.817779445788956, 33.71141407098653,
                                                   77.25783654894806, 63.985488087897565,
                                                   name='Optimise load profile (stuck in loop) (balance)', power=3,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 29.019818960300714, 80.15967828127062,
                                                   5.627769698923158, 31.86298372368094,
                                                   77.51118287810246, 65.76282496030679,
                                                   name='Optimise load profile (stuck in loop) (balance, hourly)',
                                                   power=3, hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 90.0735675672204, 98.42105305544519,
                                                   58.265826982499995, 80.73466864976513, 56.1379457303727,
                                                   62.33784403553506,
                                                   name='Optimise load profile (stuck in loop) (energy)', power=2))

ground_data = GroundFluxTemperature(3, 10)
fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
flow_data = ConstantFlowRate(mfr=0.2)
pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
borefield = Borefield()
borefield.create_rectangular_borefield(5, 4, 6, 6, 110, 4, 0.075)
borefield.ground_data = ground_data
borefield.fluid_data = fluid_data
borefield.flow_data = flow_data
borefield.pipe_data = pipe_data
borefield.calculation_setup(use_constant_Rb=False)
borefield.set_max_fluid_temperature(17)
borefield.set_min_fluid_temperature(3)
hourly_load_building = HourlyBuildingLoad()
hourly_load_building.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/auditorium.csv"), header=True,
                                         separator=";", col_cooling=0, col_heating=1)
hourly_load_building.hourly_cooling_load = hourly_load_building.hourly_cooling_load * 20 / 21
hourly_load_building.hourly_heating_load = hourly_load_building.hourly_heating_load * 5 / 4
borefield.load = hourly_load_building
list_of_test_objects.add(SizingObject(borefield, L2_output=141.453, L3_output=141.453, L4_output=103.761, quadrant=1,
                                      name='BS2023 Auditorium (1)'))
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
borefield.flow_data = ConstantDeltaTFlowRate(extraction=4, injection=4)
list_of_test_objects.add(
    SizingObject(borefield, L3_output=183.65974457051686, L4_output=147.42590911709823, quadrant=1,
                 name='BS2023 Auditorium, (var temp and flow)'))

borefield.calculation_setup(size_based_on='outlet')
borefield.flow_data = ConstantDeltaTFlowRate(extraction=4, injection=4)
list_of_test_objects.add(
    SizingObject(borefield, L3_output=96.13895180044284, L4_output=81.15952849537456, quadrant=1,
                 name='BS2023 Auditorium, (var temp and flow, outlet)'))
borefield.calculation_setup(size_based_on='average')
borefield.flow_data = ConstantDeltaTFlowRate(extraction=4, injection=4)
hourly_load_building.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/office.csv"), header=True,
                                         separator=";", col_cooling=0, col_heating=1)
borefield.load = hourly_load_building
borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
list_of_test_objects.add(
    SizingObject(borefield, L3_output=209.74036374350868, L4_output=196.39841813729225,
                 quadrant=2, name='BS2023 Office, (var temp and flow)'))

borefield.calculation_setup(size_based_on='outlet')
borefield.flow_data = ConstantDeltaTFlowRate(extraction=4, injection=4)
list_of_test_objects.add(SizingObject(borefield, L3_output=116.91234896711268, L4_output=113.00677754806857, quadrant=2,
                                      name='BS2023 Office, (var temp and flow, outlet)'))

borefield.calculation_setup(size_based_on='average')
borefield.flow_data = ConstantDeltaTFlowRate(extraction=4, injection=4)
hourly_load_building.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/swimming_pool.csv"), header=True,
                                         separator=";", col_cooling=0, col_heating=1)
borefield.load = hourly_load_building
borefield.create_rectangular_borefield(20, 20, 6, 6, 110, 4, 0.075)
list_of_test_objects.add(
    SizingObject(borefield, L3_output=233.14207706044144, L4_output=232.57331611644975, quadrant=4,
                 name='BS2023 Swimming pool, (var temp and flow)'))
borefield.calculation_setup(size_based_on='outlet')
borefield.flow_data = ConstantDeltaTFlowRate(extraction=4, injection=4)
list_of_test_objects.add(
    SizingObject(borefield, L3_output=181.937647491016, L4_output=181.35558993185205, quadrant=4,
                 name='BS2023 Swimming pool, (var temp and flow, outlet)'))
borefield = Borefield()
borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
borefield.ground_data = ground_data
borefield.fluid_data = fluid_data
borefield.flow_data = flow_data
borefield.pipe_data = pipe_data
borefield.calculation_setup(use_constant_Rb=False)
borefield.set_max_fluid_temperature(17)
borefield.set_min_fluid_temperature(3)
hourly_load_building.simulation_period = 20
hourly_load_building.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/office.csv"), header=True,
                                         separator=";", col_cooling=0, col_heating=1)
hourly_load_building.hourly_cooling_load = hourly_load_building.hourly_cooling_load * 20 / 21
hourly_load_building.hourly_heating_load = hourly_load_building.hourly_heating_load * 5 / 4
borefield.load = hourly_load_building
list_of_test_objects.add(
    SizingObject(borefield, L2_output=115.98849525499037, L3_output=115.98849525499037, L4_output=109.47590077900136,
                 quadrant=2,
                 name='BS2023 Office (1)'))

borefield = Borefield()
borefield.create_rectangular_borefield(15, 20, 6, 6, 110, 4, 0.075)
borefield.ground_data = ground_data
borefield.fluid_data = fluid_data
borefield.pipe_data = pipe_data
borefield.flow_data = flow_data
borefield.calculation_setup(use_constant_Rb=False)
borefield.set_max_fluid_temperature(17)
borefield.set_min_fluid_temperature(3)
hourly_load_building.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/swimming_pool.csv"), header=True,
                                         separator=";", col_cooling=0, col_heating=1)
hourly_load_building.hourly_cooling_load = hourly_load_building.hourly_cooling_load * 20 / 21
hourly_load_building.hourly_heating_load = hourly_load_building.hourly_heating_load * 5 / 4
borefield.load = hourly_load_building
list_of_test_objects.add(SizingObject(borefield, L2_output=308.303, L3_output=308.303, L4_output=305.8658, quadrant=4,
                                      name='BS2023 Swimming pool (1)'))

eer_combined = EERCombined(20, 5, 10)
borefield = Borefield()
borefield.create_rectangular_borefield(3, 6, 6, 6, 146, 4)
borefield.set_min_fluid_temperature(3)
borefield.set_max_fluid_temperature(16)
borefield.load.peak_duration = 6
load = HourlyBuildingLoad(efficiency_heating=4, efficiency_cooling=eer_combined)
# column order is inverted
load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile.csv"), col_heating=1, col_cooling=0)
load.simulation_period = 40
borefield.load = load

borefield.ground_data = GroundTemperatureGradient(1.9, 10, gradient=2)
borefield.fluid_data = ConstantFluidData(0.475, 1033, 3930, 0.001)
borefield.flow_data = ConstantFlowRate(mfr=0.1)
borefield.pipe_data = SingleUTube(1.5, 0.016, 0.02, 0.42, 0.04)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 45.97027470740345, 10.948246469552123,
                                                   52.81300331246172, 27.782453402164943,
                                                   605.998932750051, 512.884091498196,
                                                   name='Optimise load profile (eer combined) (power)', power=1,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 53.28456608002084, 13.765776909145428,
                                                   128.589968025, 87.797931432, 601.7667152391606,
                                                   505.7854874461028,
                                                   name='Optimise load profile (eer combined) (energy)', power=2,
                                                   hourly=False))
temp_borehole = copy.deepcopy(borefield.borehole)
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
borefield.flow_data = ConstantFlowRate(vfr=0.3)
borefield.pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

borefield.borehole.use_constant_Rb = False
borefield.load.simulation_period = 20
borefield.create_rectangular_borefield(12, 10, 6, 6, 146, 4)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 100, 45.8928906040306,
                                                   507.312202875, 537.3063482445762, 0,
                                                   419.99201166026506,
                                                   name='Optimise load profile (eer combined) (energy, var temp)',
                                                   power=2, hourly=False))
borefield.load.simulation_period = 40
borefield.borehole = temp_borehole
borefield.create_rectangular_borefield(6, 6, 6, 6, 146, 4)
list_of_test_objects.add(
    OptimiseLoadProfileObject(borefield, load, 146, 73.09826888017955, 19.215602145531243,
                              115.45661216620069, 50.92927436155475,
                              522.4741209450658, 493.59507403203776,
                              name='Optimise load profile (eer combined) (balance)', power=3,
                              hourly=True))
data = GroundFluxTemperature(1.8, 9.7, flux=0.08)
borefield = Borefield()
borefield.ground_data = data
borefield.Rb = 0.131
borefield.create_rectangular_borefield(3, 5, 6, 6, 100, 1, 0.07)
load = HourlyBuildingLoad(efficiency_heating=4.5, efficiency_cooling=20)
load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/auditorium.csv"), header=True, separator=";",
                         col_cooling=0, col_heating=1)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 100, 100.0, 95.38314800513896,
                                                   25.31511111111111, 53.00085, 0.0, 64.12244064037692,
                                                   name='Optimise load profile (auditorium) (energy)', power=2,
                                                   hourly=False))
temp_borehole = copy.deepcopy(borefield.borehole)
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
borefield.flow_data = ConstantFlowRate(vfr=0.3)
borefield.pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

borefield.borehole.use_constant_Rb = False

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 100, 100.0, 96.8077143579668,
                                                   25.31511111111111, 62.948073105081136, 0.0, 60.134611891055705,
                                                   name='Optimise load profile (auditorium) (energy, var temp)',
                                                   power=2,
                                                   hourly=False))
borefield.borehole = temp_borehole

borefield = Borefield()
data = GroundConstantTemperature(3, 10)
borefield.ground_data = data
borefield.set_Rb(0.2)
borefield.set_borefield(borefield_gt)
borefield.set_max_fluid_temperature(16)
borefield.set_min_fluid_temperature(0)
hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile.csv"), col_heating=1,
                                col_cooling=0)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.9738328260207, 66.33060176158988,
                                                   641.5806215052567, 194.66773405200593,
                                                   34.835007413480184, 341.36859661553353,
                                                   name='Optimise load profile 1, reversed (power, dhw not preferential)',
                                                   power=1,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.97104380163456, 66.31564963906172,
                                                   639.0914749083714, 194.60626036942426,
                                                   37.324156499514515, 341.43007023664154,
                                                   name='Optimise load profile 1, reversed (power, hourly, dhw not preferential)',
                                                   power=1,
                                                   hourly=True, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.94743987959366, 42.03710175401808,
                                                   623.4262132112449, 108.8773018559599,
                                                   52.98943386191843, 427.15894302123314,
                                                   name='Optimise load profile 1, reversed (balance, dhw not preferential)',
                                                   power=3,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.9516913262364, 42.038889878809854,
                                                   625.7028101449715, 108.88315919896134,
                                                   50.71283465159263, 427.15308568408904,
                                                   name='Optimise load profile 1, reversed (balance, hourly, dhw not preferential)',
                                                   power=3,
                                                   hourly=True, dhw_preferential=False))
hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile.csv"), col_heating=1,
                                col_cooling=0, col_dhw=1)
hourly_load.set_hourly_heating_load(np.zeros(8760))
hourly_load.cop_dhw = 10 ** 6
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.9738328260207, 66.33060176158988,
                                                   641.5806215052567, 194.66773405200593,
                                                   0.0, 341.36859661553353,
                                                   name='Optimise load profile 1, reversed (power, dhw load)',
                                                   power=1,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.97104380163456, 66.31564963906172,
                                                   639.0914749083714, 194.60626036942426,
                                                   0.0, 341.43007023664154,
                                                   name='Optimise load profile 1, reversed (power, hourly, dhw load)',
                                                   power=1,
                                                   hourly=True, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 81.57865616524568, 61.9785805665559,
                                                   199.9998, 177.1502599018092,
                                                   0.0, 358.8860532482736,
                                                   name='Optimise load profile 1, reversed (power, hourly, dhw load, 200)',
                                                   power=1,
                                                   hourly=True, dhw_preferential=False, max_peak_dhw=200))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 81.57865616524568, 61.9785805665559,
                                                   199.9998, 177.1502599018092,
                                                   0.0, 358.8860532482736,
                                                   name='Optimise load profile 1, reversed (power, hourly, dhw load, 200 pref)',
                                                   power=1,
                                                   hourly=True, dhw_preferential=True, max_peak_dhw=200))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.9738328260207, 66.33060176158988,
                                                   641.5806215052567, 194.66773405200593,
                                                   0.0, 341.36859661553353,
                                                   name='Optimise load profile 1, reversed (power, dhw load, preferential)',
                                                   power=1,
                                                   hourly=False, dhw_preferential=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.97104380163456, 66.31564963906172,
                                                   639.0914749083714, 194.60626036942426,
                                                   0.0, 341.43007023664154,
                                                   name='Optimise load profile 1, reversed (power, hourly, dhw load, preferential)',
                                                   power=1,
                                                   hourly=True, dhw_preferential=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.94743987959366, 42.03710175401808,
                                                   623.4262132112449, 108.8773018559599,
                                                   0.0, 427.15894302123314,
                                                   name='Optimise load profile 1, reversed (balance, dhw load)',
                                                   power=3,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.9516913262364, 42.038889878809854,
                                                   625.7028101449715, 108.88315919896134,
                                                   0.0, 427.15308568408904,
                                                   name='Optimise load profile 1, reversed (balance, hourly, dhw load)',
                                                   power=3,
                                                   hourly=True, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.94743987959366, 42.03710175401808,
                                                   623.4262132112449, 108.8773018559599,
                                                   0.0, 427.15894302123314,
                                                   name='Optimise load profile 1, reversed (balance, dhw load, preferential)',
                                                   power=3,
                                                   hourly=False, dhw_preferential=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.9516913262364, 42.038889878809854,
                                                   625.7028101449715, 108.88315919896134,
                                                   0.0, 427.15308568408904,
                                                   name='Optimise load profile 1, reversed (balance, hourly, dhw load, preferential)',
                                                   power=3,
                                                   hourly=True, dhw_preferential=True))

hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile.csv"), col_heating=1,
                                col_cooling=0, col_dhw=1)
hourly_load.cop_dhw = 10 ** 6
hourly_load.exclude_DHW_from_peak = True
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 50.040245342020604, 66.35516046254362,
                                                   641.4307656206506, 194.76870391659895,
                                                   35.08486344794221, 341.2676268519102,
                                                   name='Optimise load profile 1, reversed (power, dhw load, include DHW)',
                                                   power=1,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 94.42148162273423, 88.83148512706724,
                                                   741.8669931056082, 483.8312541717402, 92.0353046461911,
                                                   219.1734997081336,
                                                   name='Optimise load profile 1, reversed (energy, dhw load, include DHW)',
                                                   power=2, hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 94.42148162273423, 88.83148512706724,
                                                   741.8669931056082, 483.8312541717402, 92.0353046461911,
                                                   219.1734997081336,
                                                   name='Optimise load profile 1, reversed (energy, dhw load, include DHW, pref)',
                                                   power=2, hourly=False, dhw_preferential=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 94.42148162273423, 88.83148512706724,
                                                   741.8669931056082, 483.8312541717402, 92.0353046461911,
                                                   219.1734997081336,
                                                   name='Optimise load profile 1, reversed (energy, dhw load, include DHW, None)',
                                                   power=2, hourly=False, dhw_preferential=None))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 50.027279543433636, 42.08215524434656,
                                                   623.6233464420164, 109.02488313634873,
                                                   52.892300434013464, 427.0113618884254,
                                                   name='Optimise load profile 1, reversed (balance, dhw load, include DHW)',
                                                   power=3,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 50.02795062684239, 42.08271974908172,
                                                   624.3420601218551, 109.02673227902318,
                                                   52.1735860354604, 427.0095127476001,
                                                   name='Optimise load profile 1, reversed (balance, dhw load, include DHW, 200)',
                                                   power=3, max_peak_dhw=200,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 90.70619335327937, 76.30061328844434,
                                                   784.4119587444213, 239.87452906422376,
                                                   92.00352734283547, 296.16184681006547,
                                                   name='Optimise load profile 1, reversed (balance, dhw load, include DHW, 200 pref)',
                                                   power=3, max_peak_dhw=200,
                                                   hourly=False, dhw_preferential=True))
hourly_load.exclude_DHW_from_peak = False

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 50.040303937795414, 66.35550812309596,
                                                   641.5353566555302, 194.77013327717313,
                                                   34.98027230847151, 341.2661974927654,
                                                   name='Optimise load profile 1, reversed (power, dhw load, exclude DHW)',
                                                   power=1,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 94.42148162273423, 88.83148512706724,
                                                   741.8669931056082, 483.8312541717402, 92.0353046461911,
                                                   219.1734997081336,
                                                   name='Optimise load profile 1, reversed (energy, dhw load, exclude DHW)',
                                                   power=2,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 50.028488794150114, 42.083172446897734,
                                                   624.9184239554257, 109.02821517685932,
                                                   51.59722162552532, 427.0080298512469,
                                                   name='Optimise load profile 1, reversed (balance, dhw load, exclude DHW)',
                                                   power=3,
                                                   hourly=False, dhw_preferential=False))
borefield = Borefield()
eer_combined = EERCombined(20, 5, 10)
borefield.create_rectangular_borefield(10, 10, 6, 6, 146, 4)
borefield.set_min_fluid_temperature(0)
borefield.set_max_fluid_temperature(18)
borefield.load.peak_duration = 6
load = HourlyBuildingLoad(efficiency_heating=4, efficiency_cooling=eer_combined)
# column order is inverted
load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile.csv"), col_heating=1, col_cooling=0)
load.simulation_period = 40
load.add_dhw(50000)
borefield.load = load
borefield.ground_data = GroundTemperatureGradient(1.9, 10, gradient=2)
borefield.fluid_data = ConstantFluidData(0.475, 1033, 3930, 0.001)
borefield.flow_data = ConstantFlowRate(mfr=0.1)
borefield.pipe_data = SingleUTube(1.5, 0.016, 0.02, 0.42, 0.04)

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 100.0, 31.196180796771927,
                                                   511.59302479280825, 89.2894868557026,
                                                   0.0, 461.6282302869146,
                                                   name='Optimise balance with EER',
                                                   power=3, hourly=True, dhw_preferential=None))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 100.0, 31.196180796771927,
                                                   511.59302479280825, 89.2894868557026,
                                                   0.0, 461.6282302869146,
                                                   name='Optimise balance with EER and dhw preferential',
                                                   power=3, hourly=True, dhw_preferential=True))
load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile.csv"), col_dhw=0, col_cooling=1)
load.hourly_heating_load = np.zeros(8760)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 54.22428484677548, 82.152561940423,
                                                   111.87401156930925, 244.49877564991002,
                                                   0.0, 472.6672907917416,
                                                   name='Optimise balance with EER and dhw preferential and dhw',
                                                   power=3, hourly=True, dhw_preferential=True))

borefield.fluid_data = TemperatureDependentFluidData('MEG', 25)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 84.76210781224593, 72.97600227796836,
                                                   551.4363042257639, 339.4569351303427, 277.10846990785245,
                                                   300.1085391993554,
                                                   name='Optimise load profile 1, reversed (energy, dhw load, '
                                                        'include DHW, variable fluid)',
                                                   power=2, hourly=False, dhw_preferential=False))

borefield = Borefield()
borefield.create_rectangular_borefield(3, 6, 6, 6, 146, 4)
borefield.set_min_fluid_temperature(2)
borefield.set_max_fluid_temperature(17)
borefield.load.peak_duration = 6
load = HourlyBuildingLoad(efficiency_heating=4, efficiency_cooling=20)
load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile.csv"), col_heating=0, col_cooling=1)
load.simulation_period = 20
borefield.load = load

borefield.ground_data = GroundTemperatureGradient(1.9, 10, gradient=2)
borefield.fluid_data = ConstantFluidData(0.475, 1033, 3930, 0.001)
borefield.flow_data = ConstantFlowRate(mfr=0.15)
borefield.pipe_data = SingleUTube(1.5, 0.016, 0.02, 0.42, 0.04)
borefield.borehole.use_constant_rb = False
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 27.938780438710197, 30.998415511007117,
                                                   48.65682409699774, 43.64658715227783,
                                                   471.1603705373364, 634.8480922597354,
                                                   name='Optimise load profile (power, average)', power=1,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 34.191772874135694, 42.63245808591089,
                                                   140.17664334661987, 167.889049335, 444.38799494827526,
                                                   633.0972769002127,
                                                   name='Optimise load profile (energy, average)', power=2,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 17.291547535608334, 29.365937284994338,
                                                   28.46395908280642, 40.81208282207222,
                                                   498.08419055625814, 637.5476201932645,
                                                   name='Optimise load profile (balance, average)', power=3,
                                                   hourly=False))
borefield.calculation_setup(size_based_on='inlet')
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 22.59005996704104, 23.917315694042944,
                                                   38.031125073220366, 31.87512416851255,
                                                   485.32796923570623, 646.0590093871309,
                                                   name='Optimise load profile (power, inlet)', power=1, hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 27.169457431246215, 32.71578516121564,
                                                   97.23498547259602, 122.8919262307197, 470.75440920872757,
                                                   644.7091554483359,
                                                   name='Optimise load profile (energy, inlet)', power=2, hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 13.426067500342553, 22.80125913468676,
                                                   21.699887700348004, 30.13963225549167,
                                                   507.10295239953604, 647.7118588281031,
                                                   name='Optimise load profile (balance, inlet)', power=3,
                                                   hourly=False))
borefield.calculation_setup(size_based_on='outlet')
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 36.88590380548247, 44.01413295010364,
                                                   69.12606088665581, 69.5250106117684,
                                                   443.8680548177923, 610.2019746792682,
                                                   name='Optimise load profile (power, outlet)', power=1, hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 47.2078669546172, 61.240833259624935,
                                                   398.82270412500003, 250.92255027000002, 389.921515765419,
                                                   612.23469802635,
                                                   name='Optimise load profile (energy, outlet)', power=2,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 24.31717431802821, 41.297438213726004,
                                                   41.316087256919936, 63.64580590229524,
                                                   480.9480196574401, 615.8012172597188,
                                                   name='Optimise load profile (balance, outlet)', power=3,
                                                   hourly=False))
borefield.flow_data = ConstantFlowRate(mfr=0.15 * 18, flow_per_borehole=False)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 36.88590380548247, 44.01413295010364,
                                                   69.12606088665581, 69.5250106117684,
                                                   443.8680548177923, 610.2019746792682,
                                                   name='Optimise load profile (power, outlet, flow borefield)',
                                                   power=1, hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 47.2078669546172, 61.240833259624935,
                                                   398.82270412500003, 250.92255027000002, 389.921515765419,
                                                   612.23469802635,
                                                   name='Optimise load profile (energy, outlet, flow borefield)',
                                                   power=2,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 24.31717431802821, 41.297438213726004,
                                                   41.316087256919936, 63.64580590229524,
                                                   480.9480196574401, 615.8012172597188,
                                                   name='Optimise load profile (balance, outlet, flow borefield)',
                                                   power=3,
                                                   hourly=False))
borefield.calculation_setup(size_based_on='average')
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
borefield.flow_data = ConstantDeltaTFlowRate()
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 24.272093992731474, 25.665183415227265,
                                                   41.228317479808794, 34.65327438808342,
                                                   481.06504602692166, 643.4131520351586,
                                                   name='Optimise load profile (power, average, var flow)', power=1,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 32.01879872296366, 43.00279892704973,
                                                   180.32708178246241, 180.025955235, 459.5327837794823,
                                                   631.2794676440247,
                                                   name='Optimise load profile (energy, average, var flow)', power=2,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 14.311499683828508, 24.30497335788279,
                                                   23.24927521206315, 32.48426943252152,
                                                   505.03710238391585, 645.4788710404557,
                                                   name='Optimise load profile (balance, average, var flow)', power=3,
                                                   hourly=False))
borefield.calculation_setup(size_based_on='inlet')
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 17.656953153513026, 15.542378896163148,
                                                   29.103369883149284, 19.476834767228606,
                                                   497.2316428224677, 657.8669040550203,
                                                   name='Optimise load profile (power, inlet, var flow)', power=1,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 27.559448916839845, 36.10225507929293,
                                                   139.14743198167048, 150.3403161252108, 468.9909539436819,
                                                   639.5980379181033,
                                                   name='Optimise load profile (energy, inlet, var flow)', power=2,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 8.060842850093813, 13.689590542002469,
                                                   12.311464480950189, 16.9322340336763,
                                                   519.6208500253998, 660.2903333250702,
                                                   name='Optimise load profile (balance, inlet, var flow)', power=3,
                                                   hourly=False))
ground = GroundFluxTemperature(2.4, 10, flux=0.06, volumetric_heat_capacity=2.5 * 10 ** 6)
load = MonthlyBuildingLoadAbsolute(
    np.array([0.176, 0.174, 0.141, 0.1, 0.045, 0, 0, 0, 0.012, 0.065, 0.123, 0.164]) * 4680,
    np.array([0, 0, 0, 0, 0.112, 0.205, 0.27, 0.264, 0.149, 0, 0, 0]) * 1350,
    np.full(12, 3),
    np.full(12, 1.8),
    dhw=1950,
    efficiency_dhw=3,
)
fluid = TemperatureDependentFluidData('MEG', 28, False)
pipe = SingleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
flow = ConstantFlowRate(vfr=0.2)

borefield = Borefield(ground_data=ground, load=load, flow_data=flow, fluid_data=fluid, pipe_data=pipe)
borefield.create_rectangular_borefield(1, 1, 6, 6, 100, 1, 0.07)
borefield.set_min_fluid_temperature(0)
borefield.set_max_fluid_temperature(18)

list_of_test_objects.add(SizingObject(borefield, L3_output=86.23481223412898, name='Issue 435'))
