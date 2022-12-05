"""
This file contains the code to test whether or not it is valid to set a certain threshold on the relative difference
of the borehole depth below which the gfunctions are not recalculated.
This is shown for a range of thresholds and for all three different sizing methodologies.

It is shown that speed improvements in sizing are possible up to 400% in all methods,
while keeping the error lower then 5%.

"""
import numpy as np
import time
from GHEtool import GroundData, Borefield
import matplotlib.pyplot as plt
from GHEtool.Validation.cases import load_case


def test_L2_sizing():
    """
    This function test the threshold for the L2 sizing.

    Returns
    -------
    None
    """
    initial_guess = 200  # m
    relative_diff_range = np.linspace(0, 1, 10)

    # iterate a couple of times to get a smoother curve for the time
    nb_of_iterations: int = 5

    # relevant borefield data for the calculations
    data = GroundData(3,  # conductivity of the soil (W/mK)
                      10,  # Ground temperature at infinity (degrees C)
                      0.2,  # equivalent borehole resistance (K/W)
                      2.4 * 10 ** 6)  # ground volumetric heat capacity (J/m3K)

    # one can load a specific borefield quadrant
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(2)

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

    # set the answer array
    depth_array: np.ndarray = np.zeros(len(relative_diff_range))
    time_array:  np.ndarray = np.zeros(len(relative_diff_range))

    for iterate in range(nb_of_iterations):

        for idx, threshold in enumerate(relative_diff_range):
            guess_time_start = time.time()

            borefield.sizing_setup(H_init=initial_guess, relative_borefield_threshold=threshold, L2_sizing=True)
            borefield.H = initial_guess
            borefield.size()

            depth_array[idx] = borefield.H
            if iterate == 0:
                time_array[idx] = time.time() - guess_time_start
            else:
                time_array[idx] = (time_array[idx] * iterate + time.time() - guess_time_start) / (iterate + 1)

    # calculate relative differences
    depth_array_rel = (depth_array - depth_array[0])/depth_array[0] * 100  # %
    time_array_rel = (time_array[0] - time_array) / time_array * 100  # %

    # plt.figure()
    fig, axs = plt.subplots(2, 1)
    axs[0].plot(relative_diff_range * 100, time_array)
    axs[0].set_xlabel("Relative difference threshold [%]")
    axs[0].set_title("Time needed to size [ms]")

    axs[1].plot(relative_diff_range * 100, time_array_rel)
    axs[1].set_xlabel("Relative difference threshold [%]")
    axs[1].set_title("Relative speed improvement [%]")

    plt.tight_layout()

    fig, axs1 = plt.subplots(2, 1)
    axs1[0].plot(relative_diff_range * 100, depth_array)
    axs1[0].set_xlabel("Relative difference threshold [%]")
    axs1[0].set_title("Required depth [m]")

    axs1[1].plot(relative_diff_range * 100, depth_array_rel)
    axs1[1].set_xlabel("Relative difference threshold [%]")
    axs1[1].set_title("Relative difference with correct result [%]")

    plt.tight_layout()
    plt.show()


def test_L3_sizing():
    """
    This function test the threshold for the L3 sizing.

    Returns
    -------
    None
    """
    initial_guess = 200  # m
    relative_diff_range = np.linspace(0, 1, 10)

    # iterate a couple of times to get a smoother curve for the time
    nb_of_iterations: int = 5

    # relevant borefield data for the calculations
    data = GroundData(3,  # conductivity of the soil (W/mK)
                      10,  # Ground temperature at infinity (degrees C)
                      0.2,  # equivalent borehole resistance (K/W)
                      2.4 * 10 ** 6)  # ground volumetric heat capacity (J/m3K)

    # one can load a specific borefield quadrant
    monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating = load_case(2)

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

    # set the answer array
    depth_array: np.ndarray = np.zeros(len(relative_diff_range))
    time_array: np.ndarray = np.zeros(len(relative_diff_range))

    for iterate in range(nb_of_iterations):

        for idx, threshold in enumerate(relative_diff_range):
            guess_time_start = time.time()

            borefield.sizing_setup(H_init=initial_guess, relative_borefield_threshold=threshold, L3_sizing=True)
            borefield.H = initial_guess
            borefield.size()

            depth_array[idx] = borefield.H
            if iterate == 0:
                time_array[idx] = time.time() - guess_time_start
            else:
                time_array[idx] = (time_array[idx] * iterate + time.time() - guess_time_start) / (iterate + 1)

    # calculate relative differences
    depth_array_rel = (depth_array - depth_array[0]) / depth_array[0] * 100  # %
    time_array_rel = (time_array[0] - time_array) / time_array * 100  # %

    # plt.figure()
    fig, axs = plt.subplots(2, 1)
    axs[0].plot(relative_diff_range * 100, time_array)
    axs[0].set_xlabel("Relative difference threshold [%]")
    axs[0].set_title("Time needed to size [ms]")

    axs[1].plot(relative_diff_range * 100, time_array_rel)
    axs[1].set_xlabel("Relative difference threshold [%]")
    axs[1].set_title("Relative speed improvement [%]")

    plt.tight_layout()

    fig, axs1 = plt.subplots(2, 1)
    axs1[0].plot(relative_diff_range * 100, depth_array)
    axs1[0].set_xlabel("Relative difference threshold [%]")
    axs1[0].set_title("Required depth [m]")

    axs1[1].plot(relative_diff_range * 100, depth_array_rel)
    axs1[1].set_xlabel("Relative difference threshold [%]")
    axs1[1].set_title("Relative difference with correct result [%]")

    plt.tight_layout()
    plt.show()


def test_L4_sizing():
    """
    This function test the threshold for the L4 sizing.

    Returns
    -------
    None
    """
    initial_guess = 200  # m
    relative_diff_range = np.linspace(0, 1, 10)

    # iterate a couple of times to get a smoother curve for the time
    nb_of_iterations: int = 5

    # relevant borefield data for the calculations
    data = GroundData(3,  # conductivity of the soil (W/mK)
                      10,  # Ground temperature at infinity (degrees C)
                      0.12,  # equivalent borehole resistance (K/W)
                      2.4 * 10 ** 6)  # ground volumetric heat capacity (J/m3K)

    # create the borefield object
    borefield = Borefield(simulation_period=20)

    # load hourly profile
    borefield.load_hourly_profile("../Examples/hourly_profile.csv")
    borefield.set_ground_parameters(data)
    borefield.create_rectangular_borefield(10, 12, 6, 6, 100, 4, 0.075)

    # set temperature boundaries
    borefield.set_max_ground_temperature(16)  # maximum temperature
    borefield.set_min_ground_temperature(0)  # minimum temperature

    # set the answer array
    depth_array: np.ndarray = np.zeros(len(relative_diff_range))
    time_array: np.ndarray = np.zeros(len(relative_diff_range))

    for iterate in range(nb_of_iterations):

        for idx, threshold in enumerate(relative_diff_range):
            guess_time_start = time.time()

            borefield.sizing_setup(H_init=initial_guess, relative_borefield_threshold=threshold, L4_sizing=True)
            borefield.H = initial_guess
            borefield.size()

            depth_array[idx] = borefield.H
            if iterate == 0:
                time_array[idx] = time.time() - guess_time_start
            else:
                time_array[idx] = (time_array[idx] * iterate + time.time() - guess_time_start) / (iterate + 1)

    # calculate relative differences
    depth_array_rel = (depth_array - depth_array[0]) / depth_array[0] * 100  # %
    time_array_rel = (time_array[0] - time_array) / time_array * 100  # %

    # plt.figure()
    fig, axs = plt.subplots(2, 1)
    axs[0].plot(relative_diff_range * 100, time_array)
    axs[0].set_xlabel("Relative difference threshold [%]")
    axs[0].set_title("Time needed to size [ms]")

    axs[1].plot(relative_diff_range * 100, time_array_rel)
    axs[1].set_xlabel("Relative difference threshold [%]")
    axs[1].set_title("Relative speed improvement [%]")

    plt.tight_layout()

    fig, axs1 = plt.subplots(2, 1)
    axs1[0].plot(relative_diff_range * 100, depth_array)
    axs1[0].set_xlabel("Relative difference threshold [%]")
    axs1[0].set_title("Required depth [m]")

    axs1[1].plot(relative_diff_range * 100, depth_array_rel)
    axs1[1].set_xlabel("Relative difference threshold [%]")
    axs1[1].set_title("Relative difference with correct result [%]")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # test the sizing with thresholds
    test_L2_sizing()
    test_L3_sizing()
    test_L4_sizing()
