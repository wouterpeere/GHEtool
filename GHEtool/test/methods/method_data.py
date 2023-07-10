"""
This document contains all the method data used in the test_methods document.
"""
import numpy as np
import pygfunction as gt

from GHEtool.test.methods.TestMethodClass import *
from GHEtool import *
from GHEtool.Validation.cases import load_case

list_of_test_objects = TestMethodClass()


# Case 1 from main_functionalities
data = GroundConstantTemperature(3, 10)
peak_cooling = np.array([0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.])
peak_heating = np.array([160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.])
annual_heating_load = 300 * 10 ** 3
annual_cooling_load = 160 * 10 ** 3
monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
monthly_load_heating = annual_heating_load * monthly_load_heating_percentage
monthly_load_cooling = annual_cooling_load * monthly_load_cooling_percentage
borefield = Borefield(peak_heating=peak_heating, peak_cooling=peak_cooling,
                      baseload_heating=monthly_load_heating, baseload_cooling=monthly_load_cooling)
borefield.Rb = 0.2
borefield.set_ground_parameters(data)
borefield.create_rectangular_borefield(10, 12, 6, 6, 100, 4, 0.075)
borefield.set_max_ground_temperature(16)
borefield.set_min_ground_temperature(0)

list_of_test_objects.add(SizingObject(borefield, L2_output=92.07, L3_output=91.99, quadrant=1,
                                      name='Main functionalities (1)'))

fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
pipe_data = PipeData(1, 0.015, 0.02, 0.4, 0.05, number_of_pipes=2)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
borefield.sizing_setup(use_constant_Rb=False)

list_of_test_objects.add(SizingObject(borefield, L2_output=52.7, L3_output=52.73, quadrant=1,
                                      name='Main functionalities (2)'))

borefield_gt = gt.boreholes.rectangle_field(10, 12, 6, 6, 110, 1, 0.075)
borefield = Borefield()
borefield.set_ground_parameters(data)
borefield.Rb = 0.12
borefield.set_borefield(borefield_gt)
borefield.load_hourly_profile(FOLDER.joinpath("test/methods/hourly data/hourly_profile.csv"), header=True,
                              separator=";", col_heating=0, col_cooling=1)

list_of_test_objects.add(SizingObject(borefield, L2_output=182.73, L3_output=182.656, L4_output=182.337, quadrant=1,
                                      name='Hourly profile (1)'))

peak_cooling = np.array([0., 0, 3.4, 6.9, 13., 18., 21., 50., 16., 3.7, 0., 0.])  # Peak cooling in kW
peak_heating = np.array([60., 42., 10., 5., 0., 0., 0., 0., 4.4, 8.5, 19., 36.])  # Peak heating in kW
annual_heating_load = 30 * 10 ** 3  # kWh
annual_cooling_load = 16 * 10 ** 3  # kWh
monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
monthly_load_heating = annual_heating_load * monthly_load_heating_percentage  # kWh
monthly_load_cooling = annual_cooling_load * monthly_load_cooling_percentage  # kWh
borefield = Borefield(peak_heating=peak_heating,peak_cooling=peak_cooling,
                      baseload_heating=monthly_load_heating, baseload_cooling=monthly_load_cooling)
borefield.set_ground_parameters(data)
borefield.Rb = 0.2
borefield.set_max_ground_temperature(16)  # maximum temperature
borefield.set_min_ground_temperature(0)  # minimum temperature
custom_field = gt.boreholes.L_shaped_field(N_1=4, N_2=5, B_1=5., B_2=5., H=100., D=4, r_b=0.05)
borefield.set_borefield(custom_field)

list_of_test_objects.add(SizingObject(borefield, L2_output=305.176, L3_output=306.898, quadrant=1,
                                      name='Custom config (1)'))

borefield_gt = gt.boreholes.rectangle_field(11, 11, 6, 6, 110, 1, 0.075)
peak_cooling = np.array([0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.])  # Peak cooling in kW
peak_heating = np.array([160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.])  # Peak heating in kW
annual_heating_load = 150 * 10 ** 3  # kWh
annual_cooling_load = 400 * 10 ** 3  # kWh
monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
monthly_load_heating = annual_heating_load * monthly_load_heating_percentage   # kWh
monthly_load_cooling = annual_cooling_load * monthly_load_cooling_percentage   # kWh
borefield = Borefield(peak_heating=peak_heating, peak_cooling=peak_cooling,
                  baseload_heating=monthly_load_heating, baseload_cooling=monthly_load_cooling)
borefield.set_ground_parameters(data)
borefield.set_borefield(borefield_gt)
borefield.Rb = 0.2
borefield.set_max_ground_temperature(16)   # maximum temperature
borefield.set_min_ground_temperature(0)    # minimum temperature

list_of_test_objects.add(SizingObject(borefield, L2_output=190.223, L3_output=195.949, quadrant=2,
                                      name='Effect of borehole configuration (1)'))

borefield_gt = gt.boreholes.rectangle_field(6, 20, 6, 6, 110, 1, 0.075)
borefield.set_borefield(borefield_gt)

list_of_test_objects.add(SizingObject(borefield, L2_output=186.5208, L3_output=191.206, quadrant=2,
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
    borefield.set_max_ground_temperature(16)
    borefield.set_min_ground_temperature(0)
    list_of_test_objects.add(SizingObject(borefield, L2_output=correct_answers_L2[i - 1],
                                          L3_output=correct_answers_L3[i-1], quadrant=i, name=f'BS2021 case {i}'))

correct_answers_L2 = (56.749, 117.223, 66.941, 91.266)
correct_answers_L3 = (56.770, 118.738, 66.471, 91.240)
customField = gt.boreholes.rectangle_field(N_1=12, N_2=10, B_1=6.5, B_2=6.5, H=110., D=4, r_b=0.075)
for i in (1, 2, 3, 4):
    load = MonthlyGeothermalLoadAbsolute(*load_case(i))
    borefield = Borefield(load=load)
    borefield.set_ground_parameters(data)
    borefield.set_borefield(customField)
    borefield.Rb = 0.2

    borefield.set_max_ground_temperature(16)  # maximum temperature
    borefield.set_min_ground_temperature(0)  # minimum temperature
    list_of_test_objects.add(SizingObject(borefield, L2_output=correct_answers_L2[i - 1],
                                          L3_output=correct_answers_L3[i-1], quadrant=i, name=f'Custom field case {i}'))

data = GroundConstantTemperature(3, 10)
borefield = Borefield()
borefield.set_ground_parameters(data)
borefield.Rb = 0.12
borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 1, 0.075)
borefield.load_hourly_profile(FOLDER.joinpath("Examples\hourly_profile.csv"), header=True, separator=";",
                              col_heating=0, col_cooling=1)
borefield.simulation_period = 100
list_of_test_objects.add(SizingObject(borefield, L2_output=285.476, L3_output=288.541, L4_output=266.696, quadrant=4,
                                      name=f'Sizing method comparison (Validation)'))

ground_data = GroundFluxTemperature(3, 10)
fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
pipe_data = PipeData(1, 0.015, 0.02, 0.4, 0.05, 2)
borefield = Borefield()
borefield.create_rectangular_borefield(5, 4, 6, 6, 110, 4, 0.075)
borefield.set_ground_parameters(ground_data)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
borefield.sizing_setup(use_constant_Rb=False)
borefield.set_max_ground_temperature(17)
borefield.set_min_ground_temperature(3)
borefield.load_hourly_profile(FOLDER.joinpath("test\methods\hourly data\\auditorium.csv"), header=True, separator=";",
                              col_cooling=0, col_heating=1)
list_of_test_objects.add(SizingObject(borefield, L2_output=136.780, L3_output=136.294, L4_output=101.285, quadrant=1,
                                      name='BS2023 Auditorium'))

borefield = Borefield()
borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
borefield.set_ground_parameters(ground_data)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
borefield.sizing_setup(use_constant_Rb=False)
borefield.set_max_ground_temperature(17)
borefield.set_min_ground_temperature(3)
borefield.load_hourly_profile(FOLDER.joinpath("test\methods\hourly data\office.csv"), header=True, separator=";",
                              col_cooling=0, col_heating=1)
list_of_test_objects.add(SizingObject(borefield, L2_output=111.180, L3_output=113.069, L4_output=107.081, quadrant=2,
                                      name='BS2023 Office'))

borefield = Borefield()
borefield.create_rectangular_borefield(15, 20, 6, 6, 110, 4, 0.075)
borefield.set_ground_parameters(ground_data)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
borefield.sizing_setup(use_constant_Rb=False)
borefield.set_max_ground_temperature(17)
borefield.set_min_ground_temperature(3)
borefield.load_hourly_profile(FOLDER.joinpath("test\methods\hourly data\swimming_pool.csv"), header=True, separator=";",
                              col_cooling=0, col_heating=1)
list_of_test_objects.add(SizingObject(borefield, L2_output=305.509, L3_output=310.725, L4_output=308.269, quadrant=4,
                                      name='BS2023 Swimming pool'))

ground_data_IKC = GroundFluxTemperature(2.3, 10.5, flux=2.85)
fluid_data_IKC = FluidData(0.2, 0.5, 1021.7, 3919, 0.0033)
pipe_data_IKC = PipeData(2.3, 0.016, 0.02, 0.42, 0.04)
monthly_cooling = np.array([0, 0, 740, 1850, 3700, 7400, 7400, 7400, 5550, 2220, 740, 0]) * (1+1/4.86)
monthly_heating = np.array([20064, 17784, 16644, 13680, 0, 0, 0, 0, 0, 12540, 15618, 17670]) * (1-1/4.49)
peak_cooling = np.array([61]*12) * (1+1/4.86)
peak_heating = np.array([57]*12) * (1-1/4.49)
load = MonthlyGeothermalLoadAbsolute(monthly_heating, monthly_cooling, peak_heating, peak_cooling, 25)
borefield = Borefield(load=load)
borefield.create_rectangular_borefield(4, 5, 8, 8, 110, 0.8, 0.07)
borefield.set_ground_parameters(ground_data_IKC)
borefield.set_fluid_parameters(fluid_data_IKC)
borefield.set_pipe_parameters(pipe_data_IKC)
borefield.sizing_setup(use_constant_Rb=False)
borefield.set_length_peak(10)
borefield.set_max_ground_temperature(25)
borefield.set_min_ground_temperature(0)
list_of_test_objects.add(SizingObject(borefield, error=ValueError, name='Real case 1 (Error)'))

ground_data_IKC = GroundFluxTemperature(2.3, 10.5, flux=2.3*2.85/100)
borefield.set_ground_parameters(ground_data_IKC)
list_of_test_objects.add(SizingObject(borefield, L2_output=74.46, L3_output=74.866, quadrant=4,
                                      name='Real case 1 (Correct)'))

borefield.set_ground_parameters(ground_data_IKC)
borefield.create_rectangular_borefield(2, 10, 8, 8, 60, 0.8, 0.07)
list_of_test_objects.add(SizingObject(borefield, L2_output=71.65, L3_output=72.054, quadrant=4,
                                      name='Real case 2 (Correct)'))

peakCooling = [0] * 12
peakHeating = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]  # Peak heating in kW
annualHeatingLoad = 300 * 10 ** 3  # kWh
monthlyLoadHeatingPercentage = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144]
monthlyLoadHeating = list(map(lambda x: x * annualHeatingLoad, monthlyLoadHeatingPercentage))  # kWh
monthlyLoadCooling = [0]*12  # kWh
borefield = Borefield(peak_heating=peakHeating,peak_cooling=peakCooling,
                      baseload_heating=monthlyLoadHeating,baseload_cooling=monthlyLoadCooling)
borefield.set_ground_parameters(data)
borefield.create_rectangular_borefield(10, 12, 6, 6, 110, 4, 0.075)
borefield.set_max_ground_temperature(16)
borefield.set_min_ground_temperature(0)
list_of_test_objects.add(SizingObject(borefield, L2_output=81.205, L3_output=81.969, quadrant=4,
                                      name='No cooling L2/L3'))

peakCooling = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]  # Peak cooling in kW
peakHeating = [0] * 12
annualCoolingLoad = 160 * 10 ** 3  # kWh
monthlyLoadCoolingPercentage = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]
monthlyLoadHeating = [0]*12  # kWh
monthlyLoadCooling = list(map(lambda x: x * annualCoolingLoad, monthlyLoadCoolingPercentage))  # kWh
borefield = Borefield(peak_heating=peakHeating, peak_cooling=peakCooling,
                      baseload_heating=monthlyLoadHeating, baseload_cooling=monthlyLoadCooling)
borefield.set_ground_parameters(data)
borefield.create_rectangular_borefield(10, 12, 6, 6, 110, 4, 0.075)
borefield.set_max_ground_temperature(16)  # maximum temperature
borefield.set_min_ground_temperature(0)  # minimum temperature
list_of_test_objects.add(SizingObject(borefield, L2_output=120.913, L3_output=123.346, quadrant=2,
                                      name='No heating L2/L3'))
borefield = Borefield()
borefield.set_ground_parameters(data)
borefield.create_rectangular_borefield(10, 12, 6, 6, 110, 4, 0.075)
borefield.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
borefield.load.hourly_cooling_load = np.zeros(8760)
list_of_test_objects.add(SizingObject(borefield, L4_output=244.04826670835274, quadrant=4, name='No cooling L4'))

borefield.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
borefield.load.hourly_heating_load = np.zeros(8760)
list_of_test_objects.add(SizingObject(borefield, L4_output=305.55338863384287, quadrant=2, name='No heating L4'))

borefield = Borefield(load=MonthlyGeothermalLoadAbsolute(*load_case(2)))
borefield.set_ground_parameters(GroundFluxTemperature(3, 12))
borefield.create_rectangular_borefield(10, 12, 6, 6, 110, 4, 0.075)
borefield.set_Rb(0.2)
list_of_test_objects.add(SizingObject(borefield, error=ValueError, quadrant=2, name='Cannot size'))
list_of_test_objects.add(SizingObject(borefield, error_L4=ValueError, quadrant=2, name='Cannot size L4'))


data = GroundConstantTemperature(3, 10)
borefield_gt = gt.boreholes.rectangle_field(10, 12, 6, 6, 110, 4, 0.075)
borefield = Borefield()
borefield.set_max_ground_temperature(16)
borefield.set_min_ground_temperature(0)
borefield.set_ground_parameters(data)
borefield.set_Rb(0.2)
borefield.set_borefield(borefield_gt)
borefield.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
borefield._load.hourly_heating_load[0] = 100000
list_of_test_objects.add(SizingObject(borefield, L4_output=18760.64149089075, quadrant=4, name='Hourly profile, quadrant 4'))

borefield.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"), col_cooling=0, col_heating=1)
list_of_test_objects.add(SizingObject(borefield, L4_output=368.50138222702657, quadrant=2, name='Hourly profile reversed'))

borefield._load.hourly_heating_load[0] = 100000
list_of_test_objects.add(SizingObject(borefield, L4_output=18602.210559679363, quadrant=3, name='Hourly profile, quadrant 3'))

borefield.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"))
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, 150, 10**6, 10**6, 87.506, 97.012,
                                                   305.842, 384.204, 230.193, 292.212, name='Optimise load profile 1'))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, 100, 10**6, 10**6, 70.054, 87.899,
                                                   210.800, 247.186, 325.236, 429.231, name='Optimise load profile 2'))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, 50, 10**6, 10**6, 44.791, 63.799,
                                                   118.898, 117.804, 417.138, 558.612, name='Optimise load profile 3'))

borefield.set_min_ground_temperature(-5)
borefield.set_max_ground_temperature(25)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, 150, 10**6, 10**6, 100, 100,
                                                   536.036, 676.417, 0, 0, name='Optimise load profile 100%'))

borefield = Borefield()
borefield.set_ground_parameters(data)
borefield.set_Rb(0.2)
borefield.set_borefield(borefield_gt)
borefield.set_max_ground_temperature(16)
borefield.set_min_ground_temperature(0)
borefield.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"), col_heating=1, col_cooling=0)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, 150, 10**6, 10**6, 99.976, 66.492,
                                                   643.137, 195.331, 33.278, 340.705,
                                                   name='Optimise load profile 1, reversed'))
borefield.set_max_ground_temperature(20)
borefield.set_min_ground_temperature(4)
list_of_test_objects.add(OptimiseLoadProfileObject(borefield, 150, 10**6, 10**6, 97.012, 87.506,
                                                   384.204, 305.842, 292.211, 230.195,
                                                   name='Optimise load profile 2, reversed'))

list_of_test_objects.add(OptimiseLoadProfileObject(borefield, 100, 10**6, 10**6, 87.899, 70.054,
                                                   247.186, 210.800, 429.23, 325.236,
                                                   name='Optimise load profile 3, reversed'))
