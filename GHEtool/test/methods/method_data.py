"""
This document contains all the method data used in the test_methods document.
"""
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
borefield.set_max_avg_fluid_temperature(16)
borefield.set_min_avg_fluid_temperature(0)

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
borefield.set_max_avg_fluid_temperature(16)  # maximum temperature
borefield.set_min_avg_fluid_temperature(0)  # minimum temperature
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
borefield.set_max_avg_fluid_temperature(16)  # maximum temperature
borefield.set_min_avg_fluid_temperature(0)  # minimum temperature

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
    borefield.set_max_avg_fluid_temperature(16)
    borefield.set_min_avg_fluid_temperature(0)
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

    borefield.set_max_avg_fluid_temperature(16)  # maximum temperature
    borefield.set_min_avg_fluid_temperature(0)  # minimum temperature
    list_of_test_objects.add(SizingObject(borefield, L2_output=correct_answers_L2[i - 1],
                                          L3_output=correct_answers_L3[i - 1], quadrant=i,
                                          name=f'Custom field case {i}'))

data = GroundConstantTemperature(3, 10)
borefield = Borefield()
borefield.ground_data = data
borefield.Rb = 0.12
borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 1, 0.075)
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"), header=True,
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
borefield.set_max_avg_fluid_temperature(17)
borefield.set_min_avg_fluid_temperature(3)
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True, separator=";",
                                col_injection=0, col_extraction=1)
borefield.load = hourly_load
list_of_test_objects.add(SizingObject(borefield, L2_output=142.001, L3_output=141.453, L4_output=103.761, quadrant=1,
                                      name='BS2023 Auditorium'))
borefield.set_max_avg_fluid_temperature(19)
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
list_of_test_objects.add(SizingObject(borefield, L2_output=119.5189, L3_output=119.3097, L4_output=101.353, quadrant=1,
                                      name='BS2023 Auditorium (MPG, Variable limit)'))
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25).create_constant(3)
list_of_test_objects.add(SizingObject(borefield, L2_output=121.0716, L3_output=120.8516, L4_output=102.7196, quadrant=1,
                                      name='BS2023 Auditorium (MPG, fixed limit)'))
borefield.fluid_data = fluid_data
borefield.set_max_avg_fluid_temperature(17)
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
borefield.set_max_avg_fluid_temperature(17)
borefield.set_min_avg_fluid_temperature(3)
hourly_load.simulation_period = 20
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\office.csv"), header=True, separator=";",
                                col_injection=0, col_extraction=1)
borefield.load = hourly_load
list_of_test_objects.add(SizingObject(borefield, L2_output=113.955, L3_output=115.9884, L4_output=109.617, quadrant=2,
                                      name='BS2023 Office'))
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
list_of_test_objects.add(
    SizingObject(borefield, L2_output=169.373, L3_output=172.4350131073142, L4_output=160.90935, quadrant=2,
                 name='BS2023 Office, (MPG, variable)'))
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25).create_constant(3)
list_of_test_objects.add(
    SizingObject(borefield, L2_output=172.41551490145127, L3_output=175.60818720662357, L4_output=163.5176, quadrant=2,
                 name='BS2023 Office, (MPG, fixed)'))
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
borefield.set_max_avg_fluid_temperature(17)
borefield.set_min_avg_fluid_temperature(3)
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\swimming_pool.csv"), header=True,
                                separator=";",
                                col_injection=0, col_extraction=1)
borefield.load = hourly_load
list_of_test_objects.add(SizingObject(borefield, L2_output=303.172, L3_output=308.303, L4_output=305.8658, quadrant=4,
                                      name='BS2023 Swimming pool'))
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
borefield.set_max_avg_fluid_temperature(25)
borefield.set_min_avg_fluid_temperature(0)
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
borefield.set_max_avg_fluid_temperature(16)
borefield.set_min_avg_fluid_temperature(0)
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
borefield.set_max_avg_fluid_temperature(16)  # maximum temperature
borefield.set_min_avg_fluid_temperature(0)  # minimum temperature
list_of_test_objects.add(SizingObject(borefield, L2_output=120.913, L3_output=123.3795, quadrant=2,
                                      name='No extraction L2/L3'))
borefield = Borefield()
borefield.ground_data = data
borefield.create_rectangular_borefield(10, 12, 6, 6, 110, 4, 0.075)
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"))
borefield.load = hourly_load
borefield.load.hourly_injection_load = np.zeros(8760)
list_of_test_objects.add(SizingObject(borefield, L4_output=244.03137515188732, quadrant=4, name='No injection L4'))

hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"))
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
borefield.set_max_avg_fluid_temperature(16)
borefield.set_min_avg_fluid_temperature(0)
borefield.ground_data = data
borefield.set_Rb(0.2)
borefield.set_borefield(borefield_gt)
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"))
borefield.load = hourly_load
temp = hourly_load.hourly_extraction_load
temp[0] = 100_000
borefield._borefield_load.hourly_extraction_load = temp
list_of_test_objects.add(
    SizingObject(borefield, L4_output=18760.64149089075, quadrant=4, name='Hourly profile, quadrant 4'))

hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"), col_injection=0,
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
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"))
# set borefield depth to 150
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 87.506, 97.012,
                                                   305.842, 384.199888, 230.19356748567617, 292.2167663088656,
                                                   name='Optimise load profile 1 (power)', power=1, hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 70.054, 87.899,
                                                   210.800, 247.181790, 325.2359184159649, 429.23472764038456,
                                                   name='Optimise load profile 2 (power)', power=1, hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 50, 44.791, 63.79798,
                                                   117.89775525978715, 117.80039058481954, 418.138, 558.6159977154532,
                                                   name='Optimise load profile 3 (power)', power=1, hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 87.506, 96.404,
                                                   305.842, 368.463, 230.193, 307.954,
                                                   name='Optimise load profile 1 (power, hourly)', power=1,
                                                   hourly=True))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 69.662, 87.022,
                                                   209.053, 239.590, 326.983, 436.827,
                                                   name='Optimise load profile 2 (power, hourly)', power=1,
                                                   hourly=True))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 50, 44.635, 63.467,
                                                   117.388, 116.699, 418.648, 559.718,
                                                   name='Optimise load profile 3 (power, hourly)', power=1,
                                                   hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 40.231, 96.043,
                                                   102.962, 359.83364, 433.0742169029619, 316.5829889272631,
                                                   name='Optimise load profile 1 (balance)', power=3, hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 36.114, 85.953,
                                                   89.715, 230.8905106236524, 446.322, 445.522,
                                                   name='Optimise load profile 2 (balance)', power=3, hourly=False))

list_of_test_objects.add(
    OptimiseLoadProfileObject(borefield, hourly_load, 50, 25.768695010600833, 61.30370860870371, 58.929663820834676,
                              109.80038258481954, 477.10641324944265, 566.6159977154532,
                              name='Optimise load profile 3 (balance)', power=3, hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 39.917, 95.431,
                                                   101.932, 346.137, 434.104, 330.280,
                                                   name='Optimise load profile 1 (balance, hourly)', power=3,
                                                   hourly=True))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 35.594, 85.107,
                                                   88.0811, 224.402, 447.954, 452.015,
                                                   name='Optimise load profile 2 (balance, hourly)', power=3,
                                                   hourly=True))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 50, 25.456, 60.946,
                                                   58.0879, 108.699, 477.948, 567.718,
                                                   name='Optimise load profile 3 (balance, hourly)', power=3,
                                                   hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 93.2198, 99.574,
                                                   536.0356, 663.3017, 233.541, 287.717,
                                                   name='Optimise load profile 1 (energy)', power=2))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 77.5255, 96.316,
                                                   385.309, 417.43548, 316.3463, 420.1286,
                                                   name='Optimise load profile 2 (energy)', power=2))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 50, 50.7546, 75.436,
                                                   181.2417, 209.5633, 402.086, 553.3226,
                                                   name='Optimise load profile 3 (energy)', power=2))
temp_borehole = copy.deepcopy(borefield.borehole)
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
borefield.flow_data = ConstantFlowRate(vfr=0.3)
borefield.pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

borefield.borehole.use_constant_Rb = False

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 96.14933062, 99.97627,
                                                   536.035599, 676.416946, 203.989357, 131.74828,
                                                   name='Optimise load profile 1 (energy, var temp)', power=2))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 82.967736, 99.6004,
                                                   483.7593, 641.32582, 296.03371, 297.143273,
                                                   name='Optimise load profile 2 (energy, var temp)', power=2))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 50, 58.0151808, 88.56452,
                                                   220.095094, 329.93963, 380.234193, 491.59407,
                                                   name='Optimise load profile 3 (energy, var temp)', power=2))
borefield.USE_SPEED_UP_IN_SIZING = False
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 50, 58.0151808, 88.56452,
                                                   220.095094, 329.93963, 380.234193, 491.59407,
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
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 9.8902, 23.6774,
                                                   20.6834, 30, 515.352, 646.416,
                                                   name='Optimise load profile 1 (balance, limit)', power=3,
                                                   hourly=False,
                                                   max_peak_heating=30, max_peak_cooling=30))
borefield.set_min_avg_fluid_temperature(-5)
borefield.set_max_avg_fluid_temperature(25)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 100, 100,
                                                   536.036, 676.417, 0, 0, name='Optimise load profile 100% (power)',
                                                   power=1, hourly=False))

list_of_test_objects.add(
    OptimiseLoadProfileObject(borefield, hourly_load, 150, 81.451, 95.049,
                              536.036 / 2, 676.417 / 2, 536.036 / 2, 676.417 / 2,
                              name='Optimise load profile 50% (power)',
                              power=1, hourly=False, max_peak_heating=536.036 / 2,
                              max_peak_cooling=676.417 / 2))
borefield.set_max_avg_fluid_temperature(17)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 41.245, 98.215,
                                                   106.282, 426.45554769525677, 429.75396962980585, 249.96114925986444,
                                                   name='Optimise load profile 100% (balance)',
                                                   power=3, hourly=False))

list_of_test_objects.add(
    OptimiseLoadProfileObject(borefield, hourly_load, 150, 39.9766, 95.049,
                              102.127, 338.209, 433.909, 338.208,
                              name='Optimise load profile 50% (balance)',
                              power=3, hourly=False, max_peak_heating=536.036 / 2,
                              max_peak_cooling=676.417 / 2))
borefield.set_max_avg_fluid_temperature(25)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 100, 100,
                                                   536.036, 676.417, 0, 0,
                                                   name='Optimise load profile 100% (power, hourly)', power=1,
                                                   hourly=True))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 100, 100,
                                                   536.036, 676.417, 0, 0, name='Optimise load profile 100% (energy)',
                                                   power=2))

borefield.set_max_avg_fluid_temperature(17)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 40.9204, 97.914,
                                                   105.219, 413.455, 430.817, 262.961,
                                                   name='Optimise load profile 100% (balance, hourly)', power=3,
                                                   hourly=True))
borefield.set_max_avg_fluid_temperature(25)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 81.451, 95.049,
                                                   536.036 / 2, 676.417 / 2, 536.036 / 2, 676.417 / 2,
                                                   name='Optimise load profile 50% (energy)',
                                                   power=2, max_peak_heating=536.036 / 2,
                                                   max_peak_cooling=676.417 / 2))

borefield = Borefield()
borefield.ground_data = data
borefield.set_Rb(0.2)
borefield.set_borefield(borefield_gt)
borefield.set_max_avg_fluid_temperature(16)
borefield.set_min_avg_fluid_temperature(0)
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"), col_heating=1,
                                col_cooling=0)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.976, 66.492,
                                                   643.137, 195.331, 33.28226963696875, 340.705,
                                                   name='Optimise load profile 1, reversed (power)', power=1,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.971, 66.424,
                                                   639.283, 195.053, 37.132, 340.983,
                                                   name='Optimise load profile 1, reversed (power, hourly)', power=1,
                                                   hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.956, 41.9184,
                                                   628.137, 108.489, 48.28226963696875, 427.547637708311,
                                                   name='Optimise load profile 1, reversed (balance)', power=3,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.949, 41.871,
                                                   624.266, 108.333, 52.149, 427.703,
                                                   name='Optimise load profile 1, reversed (balance, hourly)', power=3,
                                                   hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.999, 72.193,
                                                   676.415, 345.694, 23.00968, 342.182,
                                                   name='Optimise load profile 1, reversed (energy)', power=2))
temp_borehole = copy.deepcopy(borefield.borehole)
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
borefield.flow_data = ConstantFlowRate(vfr=0.3)
borefield.pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

borefield.borehole.use_constant_Rb = False

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 100, 78.77365,
                                                   676.4155, 482.4967, 0, 323.34919,
                                                   name='Optimise load profile 1, reversed (energy, var temp)',
                                                   power=2))
borefield.borehole = temp_borehole
borefield.set_max_avg_fluid_temperature(20)
borefield.set_min_avg_fluid_temperature(4)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 97.012, 87.506,
                                                   384.20003438433275, 305.8416132537297, 292.21585191524866,
                                                   230.19482858757777,
                                                   name='Optimise load profile 2, reversed (power)', power=1,
                                                   hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 87.899, 70.054,
                                                   247.1818850288293, 210.79978273642746, 429.23413828903847,
                                                   325.23656406314456,
                                                   name='Optimise load profile 3, reversed (power)', power=1,
                                                   hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 96.404, 87.506,
                                                   368.463, 305.842, 307.953, 230.195,
                                                   name='Optimise load profile 2, reversed (power, hourly)', power=1,
                                                   hourly=True))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 87.022, 69.662,
                                                   239.590, 209.053, 436.826, 326.984,
                                                   name='Optimise load profile 3, reversed (power, hourly)', power=1,
                                                   hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 96.043, 40.231,
                                                   359.83382713922595, 102.96159611581379, 316.58208352658704,
                                                   433.0746428456794,
                                                   name='Optimise load profile 2, reversed (balance)', power=3,
                                                   hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 85.953, 36.114,
                                                   230.89063822391384, 89.71430554509783, 445.52540138521704,
                                                   446.321920169118,
                                                   name='Optimise load profile 3, reversed (balance)', power=3,
                                                   hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 95.431, 39.917,
                                                   346.137, 101.932, 330.280, 434.105,
                                                   name='Optimise load profile 2, reversed (balance, hourly)', power=3,
                                                   hourly=True))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 85.107, 35.5938,
                                                   224.402, 88.081, 452.014, 447.956,
                                                   name='Optimise load profile 3, reversed (balance, hourly)', power=3,
                                                   hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.5744, 93.2196,
                                                   663.3017, 536.037, 287.716, 233.54241,
                                                   name='Optimise load profile 2, reversed (energy)', power=2))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 96.316, 77.5254,
                                                   417.4359, 385.3091, 420.12788, 316.34701,
                                                   name='Optimise load profile 3, reversed (energy)', power=2))
temp_borehole = copy.deepcopy(borefield.borehole)
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
borefield.flow_data = ConstantFlowRate(vfr=0.3)
borefield.pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

borefield.borehole.use_constant_Rb = False

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.891275, 98.0621883,
                                                   676.415594, 536.03667, 208.37122, 169.963718,
                                                   name='Optimise load profile 2, reversed (energy, var temp)',
                                                   power=2))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 98.93888, 86.940635,
                                                   577.63369, 536.03667, 357.7105, 279.10843,
                                                   name='Optimise load profile 3, reversed (energy, var temp)',
                                                   power=2))
borefield.borehole = temp_borehole
borefield = Borefield()
borefield.create_rectangular_borefield(3, 6, 6, 6, 146, 4)
borefield.set_min_avg_fluid_temperature(3)
borefield.set_max_avg_fluid_temperature(16)
borefield.load.peak_duration = 6
load = HourlyBuildingLoad(efficiency_heating=4, efficiency_cooling=25)
load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\problem_data.csv"), col_heating=0,
                         col_cooling=1, header=True, decimal_seperator=',')
load.simulation_period = 40
borefield.load = load

borefield.ground_data = GroundTemperatureGradient(1.9, 10, gradient=2)
borefield.fluid_data = ConstantFluidData(0.475, 1033, 3930, 0.001)
borefield.flow_data = ConstantFlowRate(mfr=0.1)
borefield.pipe_data = SingleUTube(1.5, 0.016, 0.02, 0.42, 0.04)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 81.74619424986747, 86.4450620561209,
                                                   22.3508, 37.60682541280639, 55.21378992502661, 60.239900259224626,
                                                   name='Optimise load profile (stuck in loop) (power)', power=1,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 80.572, 83.887,
                                                   21.7649, 35.0615, 55.995, 62.6873,
                                                   name='Optimise load profile (stuck in loop) (power, hourly)',
                                                   power=1, hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 29.86737590252756, 82.77895335975978,
                                                   5.827673593321711, 34.051663566739, 77.24464435223773,
                                                   63.6583251112125,
                                                   name='Optimise load profile (stuck in loop) (balance)', power=3,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 28.7926, 79.804,
                                                   5.5742, 31.582, 77.583, 66.033,
                                                   name='Optimise load profile (stuck in loop) (balance, hourly)',
                                                   power=3, hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 89.7131, 98.2914,
                                                   57.1473, 74.1744, 54.511, 57.455,
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
borefield.set_max_avg_fluid_temperature(17)
borefield.set_min_avg_fluid_temperature(3)
hourly_load_building = HourlyBuildingLoad()
hourly_load_building.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True,
                                         separator=";", col_cooling=0, col_heating=1)
hourly_load_building.hourly_cooling_load = hourly_load_building.hourly_cooling_load * 20 / 21
hourly_load_building.hourly_heating_load = hourly_load_building.hourly_heating_load * 5 / 4
borefield.load = hourly_load_building
list_of_test_objects.add(SizingObject(borefield, L2_output=141.453, L3_output=141.453, L4_output=103.761, quadrant=1,
                                      name='BS2023 Auditorium'))

borefield = Borefield()
borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
borefield.ground_data = ground_data
borefield.fluid_data = fluid_data
borefield.flow_data = flow_data
borefield.pipe_data = pipe_data
borefield.calculation_setup(use_constant_Rb=False)
borefield.set_max_avg_fluid_temperature(17)
borefield.set_min_avg_fluid_temperature(3)
hourly_load_building.simulation_period = 20
hourly_load_building.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\office.csv"), header=True,
                                         separator=";", col_cooling=0, col_heating=1)
hourly_load_building.hourly_cooling_load = hourly_load_building.hourly_cooling_load * 20 / 21
hourly_load_building.hourly_heating_load = hourly_load_building.hourly_heating_load * 5 / 4
borefield.load = hourly_load_building
list_of_test_objects.add(
    SizingObject(borefield, L2_output=115.98849525499037, L3_output=115.98849525499037, L4_output=109.61700586805655,
                 quadrant=2,
                 name='BS2023 Office'))

borefield = Borefield()
borefield.create_rectangular_borefield(15, 20, 6, 6, 110, 4, 0.075)
borefield.ground_data = ground_data
borefield.fluid_data = fluid_data
borefield.pipe_data = pipe_data
borefield.flow_data = flow_data
borefield.calculation_setup(use_constant_Rb=False)
borefield.set_max_avg_fluid_temperature(17)
borefield.set_min_avg_fluid_temperature(3)
hourly_load_building.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\swimming_pool.csv"), header=True,
                                         separator=";", col_cooling=0, col_heating=1)
hourly_load_building.hourly_cooling_load = hourly_load_building.hourly_cooling_load * 20 / 21
hourly_load_building.hourly_heating_load = hourly_load_building.hourly_heating_load * 5 / 4
borefield.load = hourly_load_building
list_of_test_objects.add(SizingObject(borefield, L2_output=308.303, L3_output=308.303, L4_output=305.8658, quadrant=4,
                                      name='BS2023 Swimming pool'))

eer_combined = EERCombined(20, 5, 10)
borefield = Borefield()
borefield.create_rectangular_borefield(3, 6, 6, 6, 146, 4)
borefield.set_min_avg_fluid_temperature(3)
borefield.set_max_avg_fluid_temperature(16)
borefield.load.peak_duration = 6
load = HourlyBuildingLoad(efficiency_heating=4, efficiency_cooling=eer_combined)
# column order is inverted
load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"), col_heating=1, col_cooling=0)
load.simulation_period = 40
borefield.load = load

borefield.ground_data = GroundTemperatureGradient(1.9, 10, gradient=2)
borefield.fluid_data = ConstantFluidData(0.475, 1033, 3930, 0.001)
borefield.flow_data = ConstantFlowRate(mfr=0.1)
borefield.pipe_data = SingleUTube(1.5, 0.016, 0.02, 0.42, 0.04)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 45.978137699335, 10.93,
                                                   52.82586122830533, 27.731458, 605.9817888622596,
                                                   512.9266,
                                                   name='Optimise load profile (eer combined) (power)', power=1,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 50.20552887448856, 12.775993964027224,
                                                   96.0348641865927, 66.16134683885466, 602.987477171566,
                                                   509.995718403938,
                                                   name='Optimise load profile (eer combined) (energy)', power=2,
                                                   hourly=False))
temp_borehole = copy.deepcopy(borefield.borehole)
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
borefield.flow_data = ConstantFlowRate(vfr=0.3)
borefield.pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

borefield.borehole.use_constant_Rb = False

# list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 56.08842937920029, 14.933843858740387,
#                                                    120.94477115082148, 87.752679252, 589.5522141862185,
#                                                    504.2618778131993,
#                                                    name='Optimise load profile (eer combined) (energy, var temp)',
#                                                    power=2, hourly=False))
borefield.borehole = temp_borehole
borefield.create_rectangular_borefield(6, 6, 6, 6, 146, 4)
list_of_test_objects.add(
    OptimiseLoadProfileObject(borefield, load, 146, 3.7913504204793522, 0.981383824029113, 3.122966054364708,
                              2.0050722504500778, 672.2523157608471, 534.3652424579583,
                              name='Optimise load profile (eer combined) (balance)', power=3,
                              hourly=False))
data = GroundFluxTemperature(1.8, 9.7, flux=0.08)
borefield = Borefield()
borefield.ground_data = data
borefield.Rb = 0.131
borefield.create_rectangular_borefield(3, 5, 6, 6, 100, 1, 0.07)
load = HourlyBuildingLoad(efficiency_heating=4.5, efficiency_cooling=20)
load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True, separator=";",
                         col_cooling=0, col_heating=1)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 100, 100.0, 92.62620369846371,
                                                   25.315, 42.119132843891755, 0.0, 64.4014083207306,
                                                   name='Optimise load profile (auditorium) (energy)', power=2,
                                                   hourly=False))
temp_borehole = copy.deepcopy(borefield.borehole)
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
borefield.flow_data = ConstantFlowRate(vfr=0.3)
borefield.pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

borefield.borehole.use_constant_Rb = False

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 100, 100.0, 94.80200373804159,
                                                   25.31511111111111, 48.02830239678713, 0.0, 60.82918685101889,
                                                   name='Optimise load profile (auditorium) (energy, var temp)',
                                                   power=2,
                                                   hourly=False))
borefield.borehole = temp_borehole

borefield = Borefield()
data = GroundConstantTemperature(3, 10)
borefield.ground_data = data
borefield.set_Rb(0.2)
borefield.set_borefield(borefield_gt)
borefield.set_max_avg_fluid_temperature(16)
borefield.set_min_avg_fluid_temperature(0)
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"), col_heating=1,
                                col_cooling=0)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.976, 66.492,
                                                   643.137, 195.331, 33.28226963696875, 340.705,
                                                   name='Optimise load profile 1, reversed (power, dhw not preferential)',
                                                   power=1,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.971, 66.424,
                                                   639.283, 195.053, 37.132, 340.983,
                                                   name='Optimise load profile 1, reversed (power, hourly, dhw not preferential)',
                                                   power=1,
                                                   hourly=True, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.956, 41.9184,
                                                   628.137, 108.489, 48.28226963696875, 427.547637708311,
                                                   name='Optimise load profile 1, reversed (balance, dhw not preferential)',
                                                   power=3,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.949, 41.871,
                                                   624.267, 108.333, 52.149, 427.703,
                                                   name='Optimise load profile 1, reversed (balance, hourly, dhw not preferential)',
                                                   power=3,
                                                   hourly=True, dhw_preferential=False))
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"), col_heating=1,
                                col_cooling=0, col_dhw=1)
hourly_load.set_hourly_heating_load(np.zeros(8760))
hourly_load.cop_dhw = 10 ** 6
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.976, 66.492,
                                                   643.137, 195.331, 0, 340.705,
                                                   name='Optimise load profile 1, reversed (power, dhw load)',
                                                   power=1,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.971, 66.424,
                                                   639.283, 195.053, 0, 340.983,
                                                   name='Optimise load profile 1, reversed (power, hourly, dhw load)',
                                                   power=1,
                                                   hourly=True, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.976, 66.492,
                                                   643.137, 195.331, 0, 340.705,
                                                   name='Optimise load profile 1, reversed (power, dhw load, preferential)',
                                                   power=1,
                                                   hourly=False, dhw_preferential=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.971, 66.424,
                                                   639.283, 195.053, 0, 340.983,
                                                   name='Optimise load profile 1, reversed (power, hourly, dhw load, preferential)',
                                                   power=1,
                                                   hourly=True, dhw_preferential=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.956, 41.91844,
                                                   628.137, 108.4886, 0, 427.5476,
                                                   name='Optimise load profile 1, reversed (balance, dhw load)',
                                                   power=3,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.949, 41.871,
                                                   624.26657, 108.333, 0, 427.7028,
                                                   name='Optimise load profile 1, reversed (balance, hourly, dhw load)',
                                                   power=3,
                                                   hourly=True, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.956, 41.9184,
                                                   628.137, 108.4886, 0, 427.548,
                                                   name='Optimise load profile 1, reversed (balance, dhw load, preferential)',
                                                   power=3,
                                                   hourly=False, dhw_preferential=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.949, 41.871,
                                                   624.26656, 108.333, 0, 427.703,
                                                   name='Optimise load profile 1, reversed (balance, hourly, dhw load, preferential)',
                                                   power=3,
                                                   hourly=True, dhw_preferential=True))

hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"), col_heating=1,
                                col_cooling=0, col_dhw=1)
hourly_load.cop_dhw = 10 ** 6
hourly_load.exclude_DHW_from_peak = True
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 50.0408, 66.59413927618634,
                                                   642.4146383835514, 195.75123383540765, 34.10098970116769,
                                                   340.28509791563044,
                                                   name='Optimise load profile 1, reversed (power, dhw load, include DHW)',
                                                   power=1,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.93439, 88.668155,
                                                   1276.9398, 382.37345, 97.32781, 228.14127,
                                                   name='Optimise load profile 1, reversed (energy, dhw load, include DHW)',
                                                   power=2,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 50.0313, 41.83306546766215,
                                                   627.9416520743445, 108.20894217579638, 48.573990483375496,
                                                   427.82730203303765,
                                                   name='Optimise load profile 1, reversed (balance, dhw load, include DHW)',
                                                   power=3,
                                                   hourly=False, dhw_preferential=False))
hourly_load.exclude_DHW_from_peak = False

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 50.0407722, 66.559,
                                                   642.371, 195.608, 34.14809938164649, 340.42902155006277,
                                                   name='Optimise load profile 1, reversed (power, dhw load, exclude DHW)',
                                                   power=1,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.5636, 88.5654,
                                                   1171.5038, 382.0792, 203.4107, 229.096,
                                                   name='Optimise load profile 1, reversed (energy, dhw load, exclude DHW)',
                                                   power=2,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 50.0313, 41.9655,
                                                   627.9537, 108.643, 48.56576937945056, 427.3935736820914,
                                                   name='Optimise load profile 1, reversed (balance, dhw load, exclude DHW)',
                                                   power=3,
                                                   hourly=False, dhw_preferential=False))
borefield = Borefield()
eer_combined = EERCombined(20, 5, 10)
borefield.create_rectangular_borefield(10, 10, 6, 6, 146, 4)
borefield.set_min_avg_fluid_temperature(0)
borefield.set_max_avg_fluid_temperature(18)
borefield.load.peak_duration = 6
load = HourlyBuildingLoad(efficiency_heating=4, efficiency_cooling=eer_combined)
# column order is inverted
load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"), col_heating=1, col_cooling=0)
load.simulation_period = 40
load.add_dhw(50000)
borefield.load = load
borefield.ground_data = GroundTemperatureGradient(1.9, 10, gradient=2)
borefield.fluid_data = ConstantFluidData(0.475, 1033, 3930, 0.001)
borefield.flow_data = ConstantFlowRate(mfr=0.1)
borefield.pipe_data = SingleUTube(1.5, 0.016, 0.02, 0.42, 0.04)

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 99.99999, 31.1983,
                                                   511.59302, 89.29736, 0, 461.62167,
                                                   name='Optimise balance with EER',
                                                   power=3,
                                                   hourly=True, dhw_preferential=None))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 99.99999, 31.1983,
                                                   511.59302, 89.29736, 0, 461.62167,
                                                   name='Optimise balance with EER and dhw preferential',
                                                   power=3,
                                                   hourly=True, dhw_preferential=True))
load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"), col_dhw=0, col_cooling=1)
load.hourly_heating_load = np.zeros(8760)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 55.7643, 82.92732,
                                                   115.882806, 250.72453, 0, 467.47916,
                                                   name='Optimise balance with EER and dhw preferential and dhw',
                                                   power=3,
                                                   hourly=True, dhw_preferential=True))

borefield.fluid_data = TemperatureDependentFluidData('MEG', 25)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 94.94969483547132, 74.61296857235718,
                                                   948.587403343, 267.317836, 427.471233, 316.3346658,
                                                   name='Optimise load profile 1, reversed (energy, dhw load, '
                                                        'include DHW, variable fluid)',
                                                   power=2,
                                                   hourly=False, dhw_preferential=False))
