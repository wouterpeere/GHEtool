"""
This file contains the validation of the optimise borefield configuration method.
The result from the hyperparameter fitting is compared to the brute force method in time and result.
"""
from GHEtool import *
from GHEtool.Methods.optimise_borefield_configuration import optimise_borefield_configuration, brute_force_config
from GHEtool.Validation.cases import load_case

import time


def borefield_case_2():
    borefield = Borefield(ground_data=GroundConstantTemperature(3.5, 10),
                          load=MonthlyGeothermalLoadAbsolute(*load_case(2)))
    borefield.create_rectangular_borefield(10, 6, 6.5, 6.5, 100, 4, 0.075)
    borefield.calculation_setup(use_neural_network=True)

    start = time.time()
    # optimise for minimum borehole length
    print('---Using hyperparameter fitting---')
    result = optimise_borefield_configuration(borefield, 80, 70, 5, 7, 0.5, 60, 150)
    print(
        f'{len(result)} solutions are found. The optimal borehole length is: {result[0][0]:.2f}m. '
        f'There are {result[0][2]} boreholes. The configuration is {result[0][1]}.')
    result = optimise_borefield_configuration(borefield, 80, 70, 5, 7, 0.5, 60, 150, optimise='nb')
    print(
        f'{len(result)} solutions are found. The optimal number of boreholes {result[0][2]}. '
        f'The total borehole lengths is {result[0][0]:.2f}m. The configuration is {result[0][1]}.')
    print(f'This required {(time.time() - start):.2f}s.\n')

    # using brute force
    start = time.time()
    print('---Using brute force---')
    result = brute_force_config(borefield, 80, 70, 5, 7, 0.5, 60, 150)
    print(
        f'{len(result)} solutions are found. The optimal borehole length is: {result[0]:.2f}m. '
        f'There are {result[2]} boreholes. The configuration is {result[1]}.')
    result = brute_force_config(borefield, 80, 70, 5, 7, 0.5, 60, 150, optimise='nb')
    print(
        f'{len(result)} solutions are found. The optimal number of boreholes {result[2]}. '
        f'The total borehole lengths is {result[0]:.2f}m. The configuration is {result[1]}.')
    print(f'This required {(time.time() - start):.2f}s.\n')


def borefield_auditorium():  # pragma: no cover
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

    start = time.time()
    # optimise for minimum borehole length
    print('---Using hyperparameter fitting---')
    result = optimise_borefield_configuration(borefield, 80, 70, 5, 7, 0.5, 60, 150)
    print(
        f'{len(result)} solutions are found. The optimal borehole length is: {result[0][0]:.2f}m. '
        f'There are {result[0][2]} boreholes. The configuration is {result[0][1]}.')
    result = optimise_borefield_configuration(borefield, 80, 70, 5, 7, 0.5, 60, 150, size_L3=False, optimise='nb')
    print(
        f'{len(result)} solutions are found. The optimal number of boreholes {result[0][2]}. '
        f'The total borehole lengths is {result[0][0]:.2f}m. The configuration is {result[0][1]}.')
    print(f'This required {(time.time() - start):.2f}s.\n')

    # using brute force
    start = time.time()
    print('---Using brute force---')
    result = brute_force_config(borefield, 80, 70, 5, 7, 0.5, 60, 150)
    print(
        f'{len(result)} solutions are found. The optimal borehole length is: {result[0]:.2f}m. '
        f'There are {result[2]} boreholes. The configuration is {result[1]}.')
    result = brute_force_config(borefield, 80, 70, 5, 7, 0.5, 60, 150, size_L3=False, optimise='nb')
    print(
        f'{len(result)} solutions are found. The optimal number of boreholes {result[2]}. '
        f'The total borehole lengths is {result[0]:.2f}m. The configuration is {result[1]}.')
    print(f'This required {(time.time() - start):.2f}s.\n')


if __name__ == "__main__":  # pragma: no cover
    borefield_case_2()
    borefield_auditorium()
