"""
This document contains checks to see whether or not adaptations to the code still comply with some specific cases.
It also shows the difference between the original L2 sizing methode (Peere et al., 2021) and a more general L3 one.
"""

import numpy as np
import pygfunction as gt

from GHEtool import Borefield, GroundData
from GHEtool.Validation.cases_loads import load_case

# relevant borefield data for the calculations
data = GroundData(3.5,  # conductivity of the soil (W/mK)
                  10,   # Ground temperature at infinity (degrees C)
                  0.2)  # equivalent borehole resistance (K/W)

borefield_gt = gt.boreholes.rectangle_field(10, 12, 6.5, 6.5, 110, 4, 0.075)


def check_cases():

    """
    This function checks whether the borefield sizing gives the correct (i.e. validated) results for the 4 cases.
    If not, an assertion error is raised.
    NOTE: these values differ slightly from the values in the mentioned paper. This is due to the fact that GHEtool uses slightly different precalculated data.
    """

    correct_answers_L2 = (56.75, 117.23, 66.94, 91.32)
    correct_answers_L3 = (56.81, 118.82, 66.54, 91.4)

    for i in (1, 2, 3, 4):
        monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(i)

        borefield = Borefield(simulation_period=20,
                              peak_heating=peak_heating,
                              peak_cooling=peak_cooling,
                              baseload_heating=monthly_load_heating,
                              baseload_cooling=monthly_load_cooling)

        borefield.set_ground_parameters(data)
        borefield.set_borefield(borefield_gt)

        # set temperature boundaries
        borefield.set_max_ground_temperature(16)  # maximum temperature
        borefield.set_min_ground_temperature(0)  # minimum temperature

        borefield.size(100, L2_sizing=True)
        print(f'correct answer L2: {correct_answers_L2[i-1]}; calculated answer L2: {round(borefield.H,2)}; error: '
              f'{round(abs(1 - borefield.H / correct_answers_L2[i - 1]) * 100, 4)} %')
        assert round(borefield.H, 2) == correct_answers_L2[i-1]

        borefield.size(100, L3_sizing=True)
        print(f'correct answer L3: {correct_answers_L3[i - 1]}; calculated answer L3: {round(borefield.H, 2)}; error: '
              f'{round(abs(1 - borefield.H / correct_answers_L3[i - 1]) * 100, 4)} %')
        assert round(borefield.H, 2) == correct_answers_L3[i - 1]


def check_custom_datafile():
    """
    This function checks whether the borefield sizing gives the correct (i.e. validated) results for the 4 cases given the custom datafile.
    If not, an assertion error is raised.
    """

    # create custom datafile

    correct_answers = (56.75, 117.23, 66.94, 91.32)
    li = [i for i in range(0, 12)]
    borefield = Borefield(simulation_period=20,
                          peak_heating=li,
                          peak_cooling=li,
                          baseload_heating=li,
                          baseload_cooling=li)

    borefield.set_ground_parameters(data)

    customField = gt.boreholes.rectangle_field(N_1=12, N_2=10, B_1=6.5, B_2=6.5, H=110., D=4, r_b=0.075)

    for i in (1, 2, 3, 4):
        monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(i)

        borefield = Borefield(simulation_period=20,
                              peak_heating=peak_heating,
                              peak_cooling=peak_cooling,
                              baseload_heating=monthly_load_heating,
                              baseload_cooling=monthly_load_cooling)

        borefield.set_ground_parameters(data)
        borefield.set_borefield(customField)

        # set temperature boundaries
        borefield.set_max_ground_temperature(16)  # maximum temperature
        borefield.set_min_ground_temperature(0)  # minimum temperature

        borefield.size(100)
        print(f'correct answer: {correct_answers[i-1]}; calculated '
              f'answer: {round(borefield.H,2)}; error: '
              f'{round(abs(1-borefield.H/correct_answers[i - 1])*100,4)} %')
        assert abs(1-borefield.H/correct_answers[i - 1]) <= 0.002


check_cases()  # check different cases
check_custom_datafile()  # check if the custom datafile is correct

monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(1)  # load case 1

borefield = Borefield(simulation_period=20,
                      peak_heating=peak_heating,
                      peak_cooling=peak_cooling,
                      baseload_heating=monthly_load_heating,
                      baseload_cooling=monthly_load_cooling)

borefield.set_ground_parameters(data)
borefield.set_borefield(borefield_gt)

# set temperature boundaries
borefield.set_max_ground_temperature(16)  # maximum temperature
borefield.set_min_ground_temperature(0)  # minimum temperature

borefield.size(100)
print(borefield.H)
borefield.print_temperature_profile()
