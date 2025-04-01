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
borefield = Borefield(peak_extraction=peak_extraction, peak_injection=peak_injection,
                      baseload_extraction=monthly_load_extraction, baseload_injection=monthly_load_injection)
borefield.Rb = 0.2
borefield.set_ground_parameters(data)
borefield.create_rectangular_borefield(10, 12, 6, 6, 100, 4, 0.075)
borefield.set_max_avg_fluid_temperature(16)
borefield.set_min_avg_fluid_temperature(0)

list_of_test_objects.add(SizingObject(borefield, L2_output=92.07, L3_output=91.99, quadrant=1,
                                      name='Main functionalities (1)'))

fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
borefield.calculation_setup(use_constant_Rb=False)

list_of_test_objects.add(SizingObject(borefield, L2_output=52.7, L3_output=52.73, quadrant=1,
                                      name='Main functionalities (2)'))
borefield.calculation_setup(atol=False)
list_of_test_objects.add(SizingObject(borefield, L2_output=52.716, L3_output=52.741, quadrant=1,
                                      name='Main functionalities (2), no atol'))

borefield_gt = gt.boreholes.rectangle_field(10, 12, 6, 6, 110, 1, 0.075)
borefield = Borefield()
borefield.set_ground_parameters(data)
borefield.Rb = 0.12
borefield.set_borefield(borefield_gt)
hourly_load = HourlyGeothermalLoad()
hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/hourly_profile.csv"), header=True,
                                separator=";", col_extraction=0, col_injection=1)
borefield.load = hourly_load

list_of_test_objects.add(SizingObject(borefield, L2_output=182.73, L3_output=182.656, L4_output=182.337, quadrant=1,
                                      name='Hourly profile (1)'))

peak_injection = np.array([0., 0, 3.4, 6.9, 13., 18., 21., 50., 16., 3.7, 0., 0.])  # Peak injection in kW
peak_extraction = np.array([60., 42., 10., 5., 0., 0., 0., 0., 4.4, 8.5, 19., 36.])  # Peak extraction in kW
annual_extraction_load = 30 * 10 ** 3  # kWh
annual_injection_load = 16 * 10 ** 3  # kWh
monthly_load_extraction_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
monthly_load_injection_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
monthly_load_extraction = annual_extraction_load * monthly_load_extraction_percentage  # kWh
monthly_load_injection = annual_injection_load * monthly_load_injection_percentage  # kWh
borefield = Borefield(peak_extraction=peak_extraction, peak_injection=peak_injection,
                      baseload_extraction=monthly_load_extraction, baseload_injection=monthly_load_injection)
borefield.set_ground_parameters(data)
borefield.Rb = 0.2
borefield.set_max_avg_fluid_temperature(16)  # maximum temperature
borefield.set_min_avg_fluid_temperature(0)  # minimum temperature
custom_field = gt.boreholes.L_shaped_field(N_1=4, N_2=5, B_1=5., B_2=5., H=100., D=4, r_b=0.05)
borefield.set_borefield(custom_field)

list_of_test_objects.add(SizingObject(borefield, L2_output=305.176, L3_output=306.898, quadrant=1,
                                      name='Custom config (1)'))

borefield_gt = gt.boreholes.rectangle_field(11, 11, 6, 6, 110, 1, 0.075)
peak_injection = np.array([0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.])  # Peak injection in kW
peak_extraction = np.array([160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.])  # Peak extraction in kW
annual_extraction_load = 150 * 10 ** 3  # kWh
annual_injection_load = 400 * 10 ** 3  # kWh
monthly_load_extraction_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
monthly_load_injection_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
monthly_load_extraction = annual_extraction_load * monthly_load_extraction_percentage  # kWh
monthly_load_injection = annual_injection_load * monthly_load_injection_percentage  # kWh
borefield = Borefield(peak_extraction=peak_extraction, peak_injection=peak_injection,
                      baseload_extraction=monthly_load_extraction, baseload_injection=monthly_load_injection)
borefield.set_ground_parameters(data)
borefield.set_borefield(borefield_gt)
borefield.Rb = 0.2
borefield.set_max_avg_fluid_temperature(16)  # maximum temperature
borefield.set_min_avg_fluid_temperature(0)  # minimum temperature

list_of_test_objects.add(SizingObject(borefield, L2_output=190.223, L3_output=195.939, quadrant=2,
                                      name='Effect of borehole configuration (1)'))

borefield_gt = gt.boreholes.rectangle_field(6, 20, 6, 6, 110, 1, 0.075)
borefield.set_borefield(borefield_gt)

list_of_test_objects.add(SizingObject(borefield, L2_output=186.5208, L3_output=191.196, quadrant=2,
                                      name='Effect of borehole configuration (2)'))

data = GroundConstantTemperature(3.5, 10)
borefield_gt = gt.boreholes.rectangle_field(10, 12, 6.5, 6.5, 110, 4, 0.075)
correct_answers_L2 = (56.75, 117.223, 66.94, 91.266)
correct_answers_L3 = (56.771, 118.738, 66.471, 91.240)
for i in (1, 2, 3, 4):
    load = MonthlyGeothermalLoadAbsolute(*load_case(i))
    borefield = Borefield(load=load)
    borefield.set_ground_parameters(data)
    borefield.set_borefield(borefield_gt)
    borefield.Rb = 0.2
    borefield.set_max_avg_fluid_temperature(16)
    borefield.set_min_avg_fluid_temperature(0)
    list_of_test_objects.add(SizingObject(borefield, L2_output=correct_answers_L2[i - 1],
                                          L3_output=correct_answers_L3[i - 1], quadrant=i, name=f'BS2021 case {i}'))

correct_answers_L2 = (56.749, 117.223, 66.941, 91.266)
correct_answers_L3 = (56.770, 118.738, 66.471, 91.240)
customField = gt.boreholes.rectangle_field(N_1=12, N_2=10, B_1=6.5, B_2=6.5, H=110., D=4, r_b=0.075)
for i in (1, 2, 3, 4):
    load = MonthlyGeothermalLoadAbsolute(*load_case(i))
    borefield = Borefield(load=load)
    borefield.set_ground_parameters(data)
    borefield.set_borefield(customField)
    borefield.Rb = 0.2

    borefield.set_max_avg_fluid_temperature(16)  # maximum temperature
    borefield.set_min_avg_fluid_temperature(0)  # minimum temperature
    list_of_test_objects.add(SizingObject(borefield, L2_output=correct_answers_L2[i - 1],
                                          L3_output=correct_answers_L3[i - 1], quadrant=i,
                                          name=f'Custom field case {i}'))

data = GroundConstantTemperature(3, 10)
borefield = Borefield()
borefield.set_ground_parameters(data)
borefield.Rb = 0.12
borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 1, 0.075)
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"), header=True,
                                separator=";",
                                col_extraction=0, col_injection=1)
borefield.load = hourly_load
borefield.simulation_period = 100
list_of_test_objects.add(SizingObject(borefield, L2_output=285.476, L3_output=288.541, L4_output=266.696, quadrant=4,
                                      name=f'Sizing method comparison (Validation)'))

ground_data = GroundFluxTemperature(3, 10)
fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
borefield = Borefield()
borefield.create_rectangular_borefield(5, 4, 6, 6, 110, 4, 0.075)
borefield.set_ground_parameters(ground_data)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
borefield.calculation_setup(use_constant_Rb=False)
borefield.set_max_avg_fluid_temperature(17)
borefield.set_min_avg_fluid_temperature(3)
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True, separator=";",
                                col_injection=0, col_extraction=1)
borefield.load = hourly_load
list_of_test_objects.add(SizingObject(borefield, L2_output=142.001, L3_output=141.453, L4_output=103.761, quadrant=1,
                                      name='BS2023 Auditorium'))
borefield.calculation_setup(max_nb_of_iterations=2)
list_of_test_objects.add(SizingObject(borefield, error_L2=MaximumNumberOfIterations, error_L3=MaximumNumberOfIterations,
                                      error_L4=MaximumNumberOfIterations, quadrant=1,
                                      name='BS2023 Auditorium (max nb of iter)'))
borefield.calculation_setup(atol=False, max_nb_of_iterations=40)
list_of_test_objects.add(SizingObject(borefield, L2_output=141.286, L3_output=140.768, L4_output=103.451, quadrant=1,
                                      name='BS2023 Auditorium (no atol)'))
borefield.calculation_setup(force_deep_sizing=True)
list_of_test_objects.add(SizingObject(borefield, L2_output=141.286, L3_output=140.654, L4_output=103.374, quadrant=1,
                                      name='BS2023 Auditorium (no atol, deep)'))
borefield.calculation_setup(force_deep_sizing=False)
borefield = Borefield()
borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
borefield.set_ground_parameters(ground_data)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
borefield.calculation_setup(use_constant_Rb=False)
borefield.set_max_avg_fluid_temperature(17)
borefield.set_min_avg_fluid_temperature(3)
hourly_load.simulation_period = 20
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\office.csv"), header=True, separator=";",
                                col_injection=0, col_extraction=1)
borefield.load = hourly_load
list_of_test_objects.add(
    SizingObject(borefield, L2_output=113.955, L3_output=115.945, L4_output=109.629, quadrant=2,
                 name='BS2023 Office'))
borefield.calculation_setup(max_nb_of_iterations=5)
list_of_test_objects.add(SizingObject(borefield, error_L2=MaximumNumberOfIterations, error_L3=MaximumNumberOfIterations,
                                      error_L4=MaximumNumberOfIterations, quadrant=2,
                                      name='BS2023 Office (max nb of iter)'))
borefield.calculation_setup(deep_sizing=True)
list_of_test_objects.add(SizingObject(borefield, error_L2=MaximumNumberOfIterations, error_L3=MaximumNumberOfIterations,
                                      error_L4=MaximumNumberOfIterations, quadrant=2,
                                      name='BS2023 Office (max nb of iter, deep sizing)'))
borefield.calculation_setup(atol=False, max_nb_of_iterations=40)
list_of_test_objects.add(SizingObject(borefield, L2_output=113.739, L3_output=115.682, L4_output=109.35, quadrant=2,
                                      name='BS2023 Office (no atol)'))
borefield.calculation_setup(force_deep_sizing=True)
list_of_test_objects.add(SizingObject(borefield, L2_output=113.739, L3_output=115.727, L4_output=109.313, quadrant=2,
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
borefield.set_ground_parameters(ground_data)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
borefield.calculation_setup(use_constant_Rb=False)
borefield.set_max_avg_fluid_temperature(17)
borefield.set_min_avg_fluid_temperature(3)
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\swimming_pool.csv"), header=True,
                                separator=";",
                                col_injection=0, col_extraction=1)
borefield.load = hourly_load
list_of_test_objects.add(SizingObject(borefield, L2_output=303.172, L3_output=308.416, L4_output=305.979, quadrant=4,
                                      name='BS2023 Swimming pool'))
borefield.calculation_setup(atol=False, max_nb_of_iterations=40)
list_of_test_objects.add(SizingObject(borefield, L2_output=303.162, L3_output=308.434, L4_output=306.001, quadrant=4,
                                      name='BS2023 Swimming pool (no atol)'))
borefield.calculation_setup(force_deep_sizing=True)
# we expect the same values as hereabove, since quadrant 4 is limiting
list_of_test_objects.add(SizingObject(borefield, L2_output=303.162, L3_output=308.434, L4_output=306.001, quadrant=4,
                                      name='BS2023 Swimming pool (no atol, deep)'))
borefield.calculation_setup(force_deep_sizing=False)

ground_data_IKC = GroundFluxTemperature(2.3, 10.5, flux=2.85)
fluid_data_IKC = FluidData(0.2, 0.5, 1021.7, 3919, 0.0033)
pipe_data_IKC = SingleUTube(2.3, 0.016, 0.02, 0.42, 0.04)
monthly_injection = np.array([0, 0, 740, 1850, 3700, 7400, 7400, 7400, 5550, 2220, 740, 0]) * (1 + 1 / 4.86)
monthly_extraction = np.array([20064, 17784, 16644, 13680, 0, 0, 0, 0, 0, 12540, 15618, 17670]) * (1 - 1 / 4.49)
peak_injection = np.array([61] * 12) * (1 + 1 / 4.86)
peak_extraction = np.array([57] * 12) * (1 - 1 / 4.49)
load = MonthlyGeothermalLoadAbsolute(monthly_extraction, monthly_injection, peak_extraction, peak_injection, 25)
borefield = Borefield(load=load)
borefield.create_rectangular_borefield(4, 5, 8, 8, 110, 0.8, 0.07)
borefield.set_ground_parameters(ground_data_IKC)
borefield.set_fluid_parameters(fluid_data_IKC)
borefield.set_pipe_parameters(pipe_data_IKC)
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
borefield.set_ground_parameters(ground_data_IKC)
borefield.calculation_setup(max_nb_of_iterations=40)
list_of_test_objects.add(SizingObject(borefield, L2_output=74.312, L3_output=74.713, quadrant=4,
                                      name='Real case 1 (Correct)'))
borefield.calculation_setup(atol=False)
list_of_test_objects.add(SizingObject(borefield, L2_output=74.312, L3_output=74.733, quadrant=4,
                                      name='Real case 1 (Correct) (no atol)'))
borefield.calculation_setup(atol=0.05)
borefield.set_ground_parameters(ground_data_IKC)
borefield.create_rectangular_borefield(2, 10, 8, 8, 60, 0.8, 0.07)
list_of_test_objects.add(SizingObject(borefield, L2_output=71.50, L3_output=71.907, quadrant=4,
                                      name='Real case 2 (Correct)'))

peakCooling = [0] * 12
peakHeating = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]  # Peak extraction in kW
annualHeatingLoad = 300 * 10 ** 3  # kWh
monthlyLoadHeatingPercentage = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144]
monthlyLoadHeating = list(map(lambda x: x * annualHeatingLoad, monthlyLoadHeatingPercentage))  # kWh
monthlyLoadCooling = [0] * 12  # kWh
borefield = Borefield(peak_extraction=peakHeating, peak_injection=peakCooling,
                      baseload_extraction=monthlyLoadHeating, baseload_injection=monthlyLoadCooling)
borefield.set_ground_parameters(data)
borefield.create_rectangular_borefield(10, 12, 6, 6, 110, 4, 0.075)
borefield.set_max_avg_fluid_temperature(16)
borefield.set_min_avg_fluid_temperature(0)
list_of_test_objects.add(SizingObject(borefield, L2_output=81.205, L3_output=82.077, quadrant=4,
                                      name='No injection L2/L3'))

peakCooling = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]  # Peak injection in kW
peakHeating = [0] * 12
annualCoolingLoad = 160 * 10 ** 3  # kWh
monthlyLoadCoolingPercentage = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]
monthlyLoadHeating = [0] * 12  # kWh
monthlyLoadCooling = list(map(lambda x: x * annualCoolingLoad, monthlyLoadCoolingPercentage))  # kWh
borefield = Borefield(peak_extraction=peakHeating, peak_injection=peakCooling,
                      baseload_extraction=monthlyLoadHeating, baseload_injection=monthlyLoadCooling)
borefield.set_ground_parameters(data)
borefield.create_rectangular_borefield(10, 12, 6, 6, 110, 4, 0.075)
borefield.set_max_avg_fluid_temperature(16)  # maximum temperature
borefield.set_min_avg_fluid_temperature(0)  # minimum temperature
list_of_test_objects.add(SizingObject(borefield, L2_output=120.913, L3_output=123.346, quadrant=2,
                                      name='No extraction L2/L3'))
borefield = Borefield()
borefield.set_ground_parameters(data)
borefield.create_rectangular_borefield(10, 12, 6, 6, 110, 4, 0.075)
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"))
borefield.load = hourly_load
borefield.load.hourly_injection_load = np.zeros(8760)
list_of_test_objects.add(SizingObject(borefield, L4_output=244.04826670835274, quadrant=4, name='No injection L4'))

hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"))
borefield.load = hourly_load
borefield.load.hourly_extraction_load = np.zeros(8760)
list_of_test_objects.add(SizingObject(borefield, L4_output=305.55338863384287, quadrant=2, name='No extraction L4'))

borefield = Borefield(load=MonthlyGeothermalLoadAbsolute(*load_case(2)))
borefield.set_ground_parameters(GroundFluxTemperature(3, 12))
borefield.create_rectangular_borefield(10, 12, 6, 6, 110, 4, 0.075)
borefield.set_Rb(0.2)
list_of_test_objects.add(
    SizingObject(borefield, error_L2=MaximumNumberOfIterations, error_L3=UnsolvableDueToTemperatureGradient,
                 quadrant=2, name='Cannot size'))
list_of_test_objects.add(SizingObject(borefield, error_L4=ValueError, quadrant=2, name='Cannot size L4'))

data = GroundConstantTemperature(3, 10)
borefield_gt = gt.boreholes.rectangle_field(10, 12, 6, 6, 110, 4, 0.075)
borefield = Borefield()
borefield.set_max_avg_fluid_temperature(16)
borefield.set_min_avg_fluid_temperature(0)
borefield.set_ground_parameters(data)
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
    SizingObject(borefield, L4_output=368.50138222702657, quadrant=2, name='Hourly profile reversed'))

temp = hourly_load.hourly_extraction_load
temp[0] = 100_000
borefield._borefield_load.hourly_extraction_load = temp
list_of_test_objects.add(
    SizingObject(borefield, L4_output=18602.210559679363, quadrant=3, name='Hourly profile, quadrant 3'))
hourly_load = HourlyBuildingLoad(efficiency_heating=10 ** 6, efficiency_cooling=10 ** 6)
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"))
# set borefield depth to 150
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 87.506, 97.012,
                                                   305.842, 384.204, 230.193, 292.212,
                                                   name='Optimise load profile 1 (power)', power=1, hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 70.054, 87.899,
                                                   210.800, 247.186, 325.236, 429.231,
                                                   name='Optimise load profile 2 (power)', power=1, hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 50, 44.791, 63.799,
                                                   117.898, 117.804, 418.138, 558.612,
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
                                                   102.962, 359.838, 433.074, 316.579,
                                                   name='Optimise load profile 1 (balance)', power=3, hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 36.114, 85.953,
                                                   89.715, 230.894, 446.322, 445.522,
                                                   name='Optimise load profile 2 (balance)', power=3, hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 50, 25.769, 61.305, 58.930,
                                                   109.804, 477.106, 566.612,
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
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 93.2297, 99.577,
                                                   536.035, 663.782, 233.4426, 287.344,
                                                   name='Optimise load profile 1 (energy)', power=2))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 77.543, 96.331,
                                                   385.653, 417.8915, 316.2857, 419.908,
                                                   name='Optimise load profile 2 (energy)', power=2))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 50, 50.771, 75.461,
                                                   181.332, 209.819, 402.0338, 553.2355,
                                                   name='Optimise load profile 3 (energy)', power=2))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 67.621, 81.579,
                                                   200, 200, 336.036, 476.416,
                                                   name='Optimise load profile 1 (power, limit)', power=1,
                                                   hourly=False,
                                                   max_peak_heating=200, max_peak_cooling=200))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 67.621, 81.579,
                                                   200, 200, 336.036, 476.416,
                                                   name='Optimise load profile 1 (energy, limit)', power=2,
                                                   max_peak_heating=200, max_peak_cooling=200))
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
                                                   106.282, 426.460, 429.75, 249.957,
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
borefield.set_ground_parameters(data)
borefield.set_Rb(0.2)
borefield.set_borefield(borefield_gt)
borefield.set_max_avg_fluid_temperature(16)
borefield.set_min_avg_fluid_temperature(0)
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"), col_heating=1,
                                col_cooling=0)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.976, 66.492,
                                                   643.137, 195.331, 33.278, 340.705,
                                                   name='Optimise load profile 1, reversed (power)', power=1,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.971, 66.424,
                                                   639.283, 195.053, 37.132, 340.983,
                                                   name='Optimise load profile 1, reversed (power, hourly)', power=1,
                                                   hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.956, 41.9184,
                                                   628.137, 108.489, 48.278, 427.548,
                                                   name='Optimise load profile 1, reversed (balance)', power=3,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.949, 41.871,
                                                   624.266, 108.333, 52.149, 427.703,
                                                   name='Optimise load profile 1, reversed (balance, hourly)', power=3,
                                                   hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.999, 72.205,
                                                   676.415, 345.9849, 22.46646, 342.1411,
                                                   name='Optimise load profile 1, reversed (energy)', power=2))
borefield.set_max_avg_fluid_temperature(20)
borefield.set_min_avg_fluid_temperature(4)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 97.012, 87.506,
                                                   384.204, 305.842, 292.211, 230.195,
                                                   name='Optimise load profile 2, reversed (power)', power=1,
                                                   hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 87.899, 70.054,
                                                   247.186, 210.800, 429.23, 325.236,
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
                                                   359.838, 102.962, 316.578, 433.075,
                                                   name='Optimise load profile 2, reversed (balance)', power=3,
                                                   hourly=False))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 85.953, 36.114,
                                                   230.895, 89.714, 445.52, 446.322,
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
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.577, 93.230,
                                                   663.782, 536.037, 287.343, 233.4438,
                                                   name='Optimise load profile 2, reversed (energy)', power=2))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 100, 96.331, 77.543,
                                                   417.8919, 385.6529, 419.9076, 316.2865,
                                                   name='Optimise load profile 3, reversed (energy)', power=2))

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

borefield.set_ground_parameters(GroundTemperatureGradient(1.9, 10, gradient=2))
borefield.set_fluid_parameters(FluidData(0.1, 0.475, 1033, 3930, 0.001))
borefield.set_pipe_parameters(SingleUTube(1.5, 0.016, 0.02, 0.42, 0.04))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 81.746, 87.453,
                                                   22.3508, 38.72645142738253, 55.214, 59.163,
                                                   name='Optimise load profile (stuck in loop) (power)', power=1,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 80.572, 83.887,
                                                   21.7649, 35.0615, 55.995, 62.6873,
                                                   name='Optimise load profile (stuck in loop) (power, hourly)',
                                                   power=1, hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 30.1166, 82.498,
                                                   5.8865, 33.8087, 77.16616, 63.892,
                                                   name='Optimise load profile (stuck in loop) (balance)', power=3,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 28.7926, 79.804,
                                                   5.5742, 31.582, 77.583, 66.033,
                                                   name='Optimise load profile (stuck in loop) (balance, hourly)',
                                                   power=3, hourly=True))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 89.7188, 98.304,
                                                   57.202, 74.339, 54.507, 57.254,
                                                   name='Optimise load profile (stuck in loop) (energy)', power=2))

ground_data = GroundFluxTemperature(3, 10)
fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
borefield = Borefield()
borefield.create_rectangular_borefield(5, 4, 6, 6, 110, 4, 0.075)
borefield.set_ground_parameters(ground_data)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
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
borefield.set_ground_parameters(ground_data)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
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
    SizingObject(borefield, L2_output=115.945, L3_output=115.945, L4_output=109.629, quadrant=2,
                 name='BS2023 Office'))

borefield = Borefield()
borefield.create_rectangular_borefield(15, 20, 6, 6, 110, 4, 0.075)
borefield.set_ground_parameters(ground_data)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
borefield.calculation_setup(use_constant_Rb=False)
borefield.set_max_avg_fluid_temperature(17)
borefield.set_min_avg_fluid_temperature(3)
hourly_load_building.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\swimming_pool.csv"), header=True,
                                         separator=";", col_cooling=0, col_heating=1)
hourly_load_building.hourly_cooling_load = hourly_load_building.hourly_cooling_load * 20 / 21
hourly_load_building.hourly_heating_load = hourly_load_building.hourly_heating_load * 5 / 4
borefield.load = hourly_load_building
list_of_test_objects.add(SizingObject(borefield, L2_output=308.416, L3_output=308.416, L4_output=305.979, quadrant=4,
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

borefield.set_ground_parameters(GroundTemperatureGradient(1.9, 10, gradient=2))
borefield.set_fluid_parameters(FluidData(0.1, 0.475, 1033, 3930, 0.001))
borefield.set_pipe_parameters(SingleUTube(1.5, 0.016, 0.02, 0.42, 0.04))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 45.978137699335, 10.93,
                                                   52.82586122830533, 27.731458, 605.9817888622596,
                                                   512.9266,
                                                   name='Optimise load profile (eer combined) (power)', power=1,
                                                   hourly=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 146, 50.33431191906354, 12.762423542357437,
                                                   96.26241738571167, 66.21037142995145, 602.66560630039,
                                                   509.995718403938,
                                                   name='Optimise load profile (eer combined) (energy)', power=2,
                                                   hourly=False))
borefield.create_rectangular_borefield(6, 6, 6, 6, 146, 4)
list_of_test_objects.add(
    OptimiseLoadProfileObject(borefield, load, 146, 3.7914, 0.98138, 3.123036, 2.00507225, 672.2522, 534.3652,
                              name='Optimise load profile (eer combined) (balance)', power=3,
                              hourly=False))
data = GroundFluxTemperature(1.8, 9.7, flux=0.08)
borefield = Borefield()
borefield.set_ground_parameters(data)
borefield.Rb = 0.131
borefield.create_rectangular_borefield(3, 5, 6, 6, 100, 1, 0.07)
load = HourlyBuildingLoad(efficiency_heating=4.5, efficiency_cooling=20)
load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True, separator=";",
                         col_cooling=0, col_heating=1)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, load, 100, 100.0, 92.67160769044457,
                                                   25.315, 42.2817092190839, 0.0, 64.4014083207306,
                                                   name='Optimise load profile (auditorium) (energy)', power=2,
                                                   hourly=False))
borefield = Borefield()
data = GroundConstantTemperature(3, 10)
borefield.set_ground_parameters(data)
borefield.set_Rb(0.2)
borefield.set_borefield(borefield_gt)
borefield.set_max_avg_fluid_temperature(16)
borefield.set_min_avg_fluid_temperature(0)
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"), col_heating=1,
                                col_cooling=0)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.976, 66.492,
                                                   643.137, 195.331, 33.278, 340.705,
                                                   name='Optimise load profile 1, reversed (power, dhw not preferential)',
                                                   power=1,
                                                   hourly=False, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.971, 66.424,
                                                   639.283, 195.053, 37.132, 340.983,
                                                   name='Optimise load profile 1, reversed (power, hourly, dhw not preferential)',
                                                   power=1,
                                                   hourly=True, dhw_preferential=False))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.956, 41.9184,
                                                   628.137, 108.489, 48.278, 427.548,
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
borefield.set_ground_parameters(GroundTemperatureGradient(1.9, 10, gradient=2))
borefield.set_fluid_parameters(FluidData(0.1, 0.475, 1033, 3930, 0.001))
borefield.set_pipe_parameters(SingleUTube(1.5, 0.016, 0.02, 0.42, 0.04))
# borefield.print_temperature_profile(plot_hourly=True)

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.949, 41.871,
                                                   624.26656, 108.333, 0, 427.703,
                                                   name='Optimise balance with EER',
                                                   power=3,
                                                   hourly=True, dhw_preferential=None))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.949, 41.871,
                                                   624.26656, 108.333, 0, 427.703,
                                                   name='Optimise balance with EER and dhw preferential',
                                                   power=3,
                                                   hourly=True, dhw_preferential=True))
load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"), col_dhw=0, col_cooling=1)
load.hourly_heating_load = np.zeros(8760)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.949, 41.871,
                                                   624.26656, 108.333, 0, 427.703,
                                                   name='Optimise balance with EER and dhw preferential and dhw',
                                                   power=3,
                                                   hourly=True, dhw_preferential=True))
