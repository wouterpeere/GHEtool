
import numpy as np
import time
from GHEtool import GroundData, Borefield


def test_L2_sizing():

    initial_guess_range = np.linspace(10, 250, 7)
    relative_diff_range = [0, 0.05, 0.1, 0.15, 0.2, 0.5, 2]

    # relevant borefield data for the calculations
    data = GroundData(3,  # conductivity of the soil (W/mK)
                      10,  # Ground temperature at infinity (degrees C)
                      0.2,  # equivalent borehole resistance (K/W)
                      2.4 * 10 ** 6)  # ground volumetric heat capacity (J/m3K)

    # monthly loading values
    peak_cooling = np.array([0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.])  # Peak cooling in kW
    peak_heating = np.array([160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.])  # Peak heating in kW

    # annual heating and cooling load
    annual_heating_load = 300 * 10 ** 3  # kWh
    annual_cooling_load = 160 * 10 ** 3  # kWh

    # percentage of annual load per month (15.5% for January ...)
    monthly_load_heating_percentage = np.array(
        [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
    monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])

    # resulting load per month
    monthly_load_heating = annual_heating_load * monthly_load_heating_percentage  # kWh
    monthly_load_cooling = annual_cooling_load * monthly_load_cooling_percentage  # kWh

    # create the borefield object
    borefield = Borefield(simulation_period=20,
                          peak_heating=peak_heating,
                          peak_cooling=peak_cooling,
                          baseload_heating=monthly_load_heating,
                          baseload_cooling=monthly_load_cooling)

    borefield.set_ground_parameters(data)
    borefield.create_rectangular_borefield(10, 12, 6, 6, 100, 4, 0.075)

    # set temperature boundaries
    borefield.set_max_ground_temperature(16)  # maximum temperature
    borefield.set_min_ground_temperature(0)  # minimum temperature
    for threshold in relative_diff_range:

        guess_time_start = time.time()
        for guess in initial_guess_range:

            borefield.sizing_setup(H_init=guess, relative_borefield_threshold=threshold)
            borefield.H = guess
            borefield.size()
            print("Depth:", str(borefield.H), "m, with a guess of", str(guess), "and a threshold of", str(threshold))
        print("Time it took", time.time() - guess_time_start)

test_L2_sizing()
