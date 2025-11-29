"""
The goal of this file is to validate the artificial neural network, based on the work of Blanke et al. ([#BlankeEtAl]_).
It shows that all simulations are withing 2% and that the ANN gives a slight overestimation (so it is on the safe side).
The simulation time is 200-1000 times faster.

References
----------
.. [#BlankeEtAl] Blanke T., Pfeiffer F., Göttsche J., Döring B. (2024) Artificial neural networks use
for the design of geothermal probe fields. In Proceedings of BauSim Conference 2024:  10th Conference of
IBPSA-Germany and Austria. Vienna (Austria), 23-26 September 2024. https://doi.org/10.26868/29761662.2024.12
"""
import copy

import pytest

from GHEtool import *
from GHEtool.Methods.optimise_borefield_configuration import optimise_borefield_configuration_config_all_in_once
from GHEtool.Validation.cases import load_case

import time


## define cases
def borefield_case_1():
    borefield = Borefield(ground_data=GroundConstantTemperature(3.5, 10),
                          load=MonthlyGeothermalLoadAbsolute(*load_case(1)))
    borefield.create_rectangular_borefield(10, 6, 6.5, 6.5, 100, 4, 0.075)
    borefield.calculation_setup(use_neural_network=True)

    # optimise for minimum borehole length
    result = optimise_borefield_configuration_config_all_in_once(borefield, 80, 70, 5, 7, 0.5, 60, 150)
    borefield.borefield = result[0][-1]
    print(
        f'{len(result)} solutions are found. The optimal borehole length is: {result[0][0]:.2f}m. '
        f'There are {result[0][2]} boreholes. The configuration is {result[0][1]}.')
    result = optimise_borefield_configuration_config_all_in_once(borefield, 80, 70, 5, 7, 0.5, 60, 150, optimise='nb')
    borefield.borefield = result[0][-1]
    print(
        f'{len(result)} solutions are found. The optimal number of boreholes {result[0][2]}. '
        f'The total borehole lengths is {result[0][0]:.2f}m. The configuration is {result[0][1]}.')


def borefield_case_2():
    borefield = Borefield(ground_data=GroundConstantTemperature(3.5, 10),
                          load=MonthlyGeothermalLoadAbsolute(*load_case(2)))
    borefield.create_rectangular_borefield(10, 6, 6.5, 6.5, 100, 4, 0.075)
    borefield.calculation_setup(use_neural_network=True)

    # optimise for minimum borehole length
    result = optimise_borefield_configuration_config_all_in_once(borefield, 80, 70, 5, 7, 0.5, 60, 150)
    borefield.borefield = result[0][-1]
    print(
        f'{len(result)} solutions are found. The optimal borehole length is: {result[0][0]:.2f}m. '
        f'There are {result[0][2]} boreholes. The configuration is {result[0][1]}.')
    result = optimise_borefield_configuration_config_all_in_once(borefield, 80, 70, 5, 7, 0.5, 60, 150, optimise='nb')
    borefield.borefield = result[0][-1]
    print(
        f'{len(result)} solutions are found. The optimal number of boreholes {result[0][2]}. '
        f'The total borehole lengths is {result[0][0]:.2f}m. The configuration is {result[0][1]}.')


def borefield_case_3():
    borefield = Borefield(ground_data=GroundConstantTemperature(3.5, 10),
                          load=MonthlyGeothermalLoadAbsolute(*load_case(3)))
    borefield.create_rectangular_borefield(10, 6, 6.5, 6.5, 100, 4, 0.075)
    borefield.calculation_setup(use_neural_network=True)

    # optimise for minimum borehole length
    result = optimise_borefield_configuration_config_all_in_once(borefield, 80, 70, 5, 7, 0.5, 60, 150)
    borefield.borefield = result[0][-1]
    print(
        f'{len(result)} solutions are found. The optimal borehole length is: {result[0][0]:.2f}m. '
        f'There are {result[0][2]} boreholes. The configuration is {result[0][1]}.')
    result = optimise_borefield_configuration_config_all_in_once(borefield, 80, 70, 5, 7, 0.5, 60, 150, optimise='nb')
    borefield.borefield = result[0][-1]
    print(
        f'{len(result)} solutions are found. The optimal number of boreholes {result[0][2]}. '
        f'The total borehole lengths is {result[0][0]:.2f}m. The configuration is {result[0][1]}.')


def borefield_case_4():
    borefield = Borefield(ground_data=GroundConstantTemperature(3.5, 10),
                          load=MonthlyGeothermalLoadAbsolute(*load_case(4)))
    borefield.create_rectangular_borefield(10, 6, 6.5, 6.5, 100, 4, 0.075)
    borefield.calculation_setup(use_neural_network=True)

    # optimise for minimum borehole length
    result = optimise_borefield_configuration_config_all_in_once(borefield, 80, 70, 5, 7, 0.5, 60, 150)
    borefield.borefield = result[0][-1]
    print(
        f'{len(result)} solutions are found. The optimal borehole length is: {result[0][0]:.2f}m. '
        f'There are {result[0][2]} boreholes. The configuration is {result[0][1]}.')
    result = optimise_borefield_configuration_config_all_in_once(borefield, 80, 70, 5, 7, 0.5, 60, 150, optimise='nb')
    borefield.borefield = result[0][-1]
    print(
        f'{len(result)} solutions are found. The optimal number of boreholes {result[0][2]}. '
        f'The total borehole lengths is {result[0][0]:.2f}m. The configuration is {result[0][1]}.')


def borefield_office():
    borefield = Borefield()
    borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
    borefield.ground_data = GroundFluxTemperature(3, 10)
    borefield.fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    borefield.flow_data = ConstantFlowRate(mfr=0.2)
    borefield.pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_avg_fluid_temperature(17)
    borefield.set_min_avg_fluid_temperature(3)
    hourly_load = HourlyGeothermalLoad()
    hourly_load.simulation_period = 20
    hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\office.csv"), header=True, separator=";",
                                    col_injection=0, col_extraction=1)
    borefield.load = hourly_load
    borefield.calculation_setup(use_neural_network=True)

    # optimise for minimum borehole length
    result = optimise_borefield_configuration_config_all_in_once(borefield, 80, 70, 5, 7, 0.5, 60, 150)
    borefield.borefield = result[0][-1]
    print(
        f'{len(result)} solutions are found. The optimal borehole length is: {result[0][0]:.2f}m. '
        f'There are {result[0][2]} boreholes. The configuration is {result[0][1]}.')
    result = optimise_borefield_configuration_config_all_in_once(borefield, 80, 70, 5, 7, 0.5, 60, 150, optimise='nb')
    borefield.borefield = result[0][-1]
    print(
        f'{len(result)} solutions are found. The optimal number of boreholes {result[0][2]}. '
        f'The total borehole lengths is {result[0][0]:.2f}m. The configuration is {result[0][1]}.')


def borefield_auditorium():
    borefield = Borefield()
    borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
    borefield.ground_data = GroundFluxTemperature(3, 10)
    borefield.fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    borefield.flow_data = ConstantFlowRate(mfr=0.2)
    borefield.pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_avg_fluid_temperature(17)
    borefield.set_min_avg_fluid_temperature(3)
    hourly_load = HourlyGeothermalLoad()
    hourly_load.simulation_period = 20
    hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True,
                                    separator=";", col_injection=0, col_extraction=1)
    borefield.load = hourly_load
    borefield.calculation_setup(use_neural_network=True)

    # optimise for minimum borehole length
    result = optimise_borefield_configuration_config_all_in_once(borefield, 80, 70, 5, 7, 0.5, 60, 150)
    borefield.borefield = result[0][-1]
    print(
        f'{len(result)} solutions are found. The optimal borehole length is: {result[0][0]:.2f}m. '
        f'There are {result[0][2]} boreholes. The configuration is {result[0][1]}.')
    result = optimise_borefield_configuration_config_all_in_once(borefield, 80, 70, 5, 7, 0.5, 60, 150,
                                                                 optimise='nb')
    borefield.borefield = result[0][-1]
    print(
        f'{len(result)} solutions are found. The optimal number of boreholes {result[0][2]}. '
        f'The total borehole lengths is {result[0][0]:.2f}m. The configuration is {result[0][1]}.')


def borefield_swimming_pool():
    borefield = Borefield()
    borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
    borefield.ground_data = GroundFluxTemperature(3, 10)
    borefield.fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
    borefield.flow_data = ConstantFlowRate(mfr=0.2)
    borefield.pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_avg_fluid_temperature(17)
    borefield.set_min_avg_fluid_temperature(3)
    hourly_load = HourlyGeothermalLoad()
    hourly_load.simulation_period = 20
    hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\swimming_pool.csv"), header=True,
                                    separator=";", col_injection=0, col_extraction=1)
    borefield.load = hourly_load
    borefield.calculation_setup(use_neural_network=True)

    # optimise for minimum borehole length
    result = optimise_borefield_configuration_config_all_in_once(borefield, 120, 120, 5, 7, 0.5, 60, 150)
    borefield.borefield = result[0][-1]
    print(
        f'{len(result)} solutions are found. The optimal borehole length is: {result[0][0]:.2f}m. '
        f'There are {result[0][2]} boreholes. The configuration is {result[0][1]}.')
    result = optimise_borefield_configuration_config_all_in_once(borefield, 120, 120, 5, 7, 0.5, 60, 150, optimise='nb')
    borefield.borefield = result[0][-1]
    print(
        f'{len(result)} solutions are found. The optimal number of boreholes {result[0][2]}. '
        f'The total borehole lengths is {result[0][0]:.2f}m. The configuration is {result[0][1]}.')


if __name__ == "__main__":  # pragma: no cover
    borefield_case_1()
    borefield_case_2()
    borefield_case_3()
    borefield_case_4()
    borefield_office()
    borefield_auditorium()
    borefield_swimming_pool()
