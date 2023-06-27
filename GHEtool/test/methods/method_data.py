"""
This document contains all the method data used in the test_methods document.
"""
import numpy as np
import pygfunction as gt

from GHEtool.test.methods.TestMethodClass import TestObject, TestMethodClass
from GHEtool import *

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
borefield = Borefield(simulation_period=20, peak_heating=peak_heating, peak_cooling=peak_cooling,
                      baseload_heating=monthly_load_heating, baseload_cooling=monthly_load_cooling)
borefield.Rb = 0.2
borefield.set_ground_parameters(data)
borefield.create_rectangular_borefield(10, 12, 6, 6, 100, 4, 0.075)
borefield.set_max_ground_temperature(16)
borefield.set_min_ground_temperature(0)

list_of_test_objects.add(TestObject(borefield, L2_output=92.07, L3_output=91.99, quadrant=1,
                         name='Main functionalities (1)'))

fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
pipe_data = PipeData(1, 0.015, 0.02, 0.4, 0.05, number_of_pipes=2)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
borefield.sizing_setup(use_constant_Rb=False)

list_of_test_objects.add(TestObject(borefield, L2_output=52.7, L3_output=52.73, quadrant=1,
                         name='Main functionalities (2)'))

borefield_gt = gt.boreholes.rectangle_field(10, 12, 6, 6, 110, 1, 0.075)
borefield = Borefield()
borefield.set_ground_parameters(data)
borefield.Rb = 0.12
borefield.set_borefield(borefield_gt)
borefield.load_hourly_profile(FOLDER.joinpath("test/methods/hourly data/hourly_profile.csv"), header=True, separator=";", first_column_heating=True)
borefield.convert_hourly_to_monthly()

list_of_test_objects.add(TestObject(borefield, L2_output=182.73, L3_output=182.656, L4_output=182.337, quadrant=1,
                         name='Hourly profile (1)'))

peak_cooling = np.array([0., 0, 3.4, 6.9, 13., 18., 21., 50., 16., 3.7, 0., 0.])  # Peak cooling in kW
peak_heating = np.array([60., 42., 10., 5., 0., 0., 0., 0., 4.4, 8.5, 19., 36.])  # Peak heating in kW
annual_heating_load = 30 * 10 ** 3  # kWh
annual_cooling_load = 16 * 10 ** 3  # kWh
monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
monthly_load_heating = annual_heating_load * monthly_load_heating_percentage  # kWh
monthly_load_cooling = annual_cooling_load * monthly_load_cooling_percentage  # kWh
borefield = Borefield(simulation_period=20,peak_heating=peak_heating,peak_cooling=peak_cooling,
                      baseload_heating=monthly_load_heating, baseload_cooling=monthly_load_cooling)
borefield.set_ground_parameters(data)
borefield.Rb = 0.2
borefield.set_max_ground_temperature(16)  # maximum temperature
borefield.set_min_ground_temperature(0)  # minimum temperature
custom_field = gt.boreholes.L_shaped_field(N_1=4, N_2=5, B_1=5., B_2=5., H=100., D=4, r_b=0.05)
borefield.set_borefield(custom_field)

list_of_test_objects.add(TestObject(borefield, L2_output=305.176, L3_output=306.898, quadrant=1,
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
borefield = Borefield(simulation_period=20, peak_heating=peak_heating, peak_cooling=peak_cooling,
                  baseload_heating=monthly_load_heating, baseload_cooling=monthly_load_cooling)
borefield.set_ground_parameters(data)
borefield.set_borefield(borefield_gt)
borefield.Rb = 0.2
borefield.set_max_ground_temperature(16)   # maximum temperature
borefield.set_min_ground_temperature(0)    # minimum temperature

list_of_test_objects.add(TestObject(borefield, L2_output=190.223, L3_output=195.949, quadrant=2,
                         name='Effect of borehole configuration (1)'))

borefield_gt = gt.boreholes.rectangle_field(6, 20, 6, 6, 110, 1, 0.075)
borefield.set_borefield(borefield_gt)

list_of_test_objects.add(TestObject(borefield, L2_output=186.5208, L3_output=191.206, quadrant=2,
                         name='Effect of borehole configuration (2)'))

from GHEtool.Validation.cases import load_case
data = GroundConstantTemperature(3.5, 10)
borefield_gt = gt.boreholes.rectangle_field(10, 12, 6.5, 6.5, 110, 4, 0.075)
correct_answers_L2 = (56.75, 117.223, 66.94, 91.266)
correct_answers_L3 = (56.771, 118.738, 66.471, 91.240)
for i in (1, 2, 3, 4):
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(i)
    borefield = Borefield(simulation_period=20, peak_heating=peak_heating, peak_cooling=peak_cooling,
                          baseload_heating=monthly_load_heating,baseload_cooling=monthly_load_cooling)
    borefield.set_ground_parameters(data)
    borefield.set_borefield(borefield_gt)
    borefield.Rb = 0.2
    borefield.set_max_ground_temperature(16)
    borefield.set_min_ground_temperature(0)
    list_of_test_objects.add(TestObject(borefield, L2_output=correct_answers_L2[i-1],
                                        L3_output=correct_answers_L3[i-1], quadrant=i, name=f'BS2021 case {i}'))

correct_answers_L2 = (56.749, 117.223, 66.941, 91.266)
correct_answers_L3 = (56.770, 118.738, 66.471, 91.240)
customField = gt.boreholes.rectangle_field(N_1=12, N_2=10, B_1=6.5, B_2=6.5, H=110., D=4, r_b=0.075)
for i in (1, 2, 3, 4):
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(i)
    borefield = Borefield(simulation_period=20, peak_heating=peak_heating, peak_cooling=peak_cooling,
                          baseload_heating=monthly_load_heating, baseload_cooling=monthly_load_cooling)
    borefield.set_ground_parameters(data)
    borefield.set_borefield(customField)
    borefield.Rb = 0.2

    borefield.set_max_ground_temperature(16)  # maximum temperature
    borefield.set_min_ground_temperature(0)  # minimum temperature
    list_of_test_objects.add(TestObject(borefield, L2_output=correct_answers_L2[i-1],
                                        L3_output=correct_answers_L3[i-1], quadrant=i, name=f'Custom field case {i}'))

data = GroundConstantTemperature(3, 10)
borefield = Borefield(100)
borefield.set_ground_parameters(data)
borefield.Rb = 0.12
borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 1, 0.075)
borefield.load_hourly_profile(FOLDER.joinpath("Examples\hourly_profile.csv"), header=True, separator=";", first_column_heating=True)
list_of_test_objects.add(TestObject(borefield, L2_output=285.476, L3_output=288.541, L4_output=266.696, quadrant=i,
                                    name=f'Sizing method comparison (Validation)'))

ground_data = GroundFluxTemperature(3, 10)
fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
pipe_data = PipeData(1, 0.015, 0.02, 0.4, 0.05, 2)
borefield = Borefield()
borefield.create_rectangular_borefield(5, 4, 6, 6, 110, 4, 0.075)
borefield.set_Rb(0.12)
borefield.set_ground_parameters(ground_data)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
borefield.sizing_setup(use_constant_Rb=False)
borefield.set_max_ground_temperature(17)
borefield.set_min_ground_temperature(3)
borefield.load_hourly_profile(FOLDER.joinpath("test\methods\hourly data\\auditorium.csv"), header=True, separator=";", first_column_heating=False)
list_of_test_objects.add(TestObject(borefield, L2_output=136.780, L3_output=136.294, L4_output=101.285, quadrant=1,
                                    name='BS2023 Auditorium'))

borefield = Borefield()
borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
borefield.set_Rb(0.12)
borefield.set_ground_parameters(ground_data)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
borefield.sizing_setup(use_constant_Rb=False)
borefield.set_max_ground_temperature(17)
borefield.set_min_ground_temperature(3)
borefield.load_hourly_profile(FOLDER.joinpath("test\methods\hourly data\office.csv"), header=True, separator=";", first_column_heating=False)
list_of_test_objects.add(TestObject(borefield, L2_output=111.180, L3_output=113.069, L4_output=107.081, quadrant=2,
                                    name='BS2023 Office'))

borefield = Borefield()
borefield.create_rectangular_borefield(15, 20, 6, 6, 110, 4, 0.075)
borefield.set_Rb(0.12)
borefield.set_ground_parameters(ground_data)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
borefield.sizing_setup(use_constant_Rb=False)
borefield.set_max_ground_temperature(17)
borefield.set_min_ground_temperature(3)
borefield.load_hourly_profile(FOLDER.joinpath("test\methods\hourly data\swimming_pool.csv"), header=True, separator=";", first_column_heating=False)
list_of_test_objects.add(TestObject(borefield, L2_output=305.509, L3_output=310.725, L4_output=308.269, quadrant=4,
                                    name='BS2023 Swimming pool'))