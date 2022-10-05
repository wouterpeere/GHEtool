"""
This document contains all the scripts for coming up with the figures of the article written by
Verleyen L., Peere W. and Helsen L.
"""
import math

from GHEtool import Borefield, GroundData
import matplotlib.pyplot as plt
import numpy as np

# code for making figures black-and-white ready
from cycler import cycler
color_c = cycler('color', ['k'])
style_c = cycler('linestyle', ['-', '--', ':', '-.'])
markr_c = cycler('marker', ['', '.', 'o'])
c_cms = color_c * markr_c * style_c
c_csm = color_c * style_c * markr_c
plt.rc('axes', prop_cycle=c_cms)
plt.rcParams['lines.markersize'] = 8


def figure_1():
    """
    This function generates the first figure (part a/b) of the article.
    """

    # initiate ground data
    ground_data = GroundData(100, 6, 2.4, 10, 0.12, 10, 10)

    # initiate borefield model
    borefield = Borefield()
    borefield.set_ground_parameters(ground_data)

    # initiate depth array
    depth = 150

    # dimensionless time
    ts = 150**2 / (9 * ground_data.k_s)

    # time array
    nb_of_timesteps = 50
    time_dimensionless = np.linspace(2, 14, nb_of_timesteps)

    # convert to seconds
    time_in_seconds = np.exp(time_dimensionless) * ts

    # calculate g-functions
    result = np.zeros(nb_of_timesteps)
    result = borefield.gfunction(time_in_seconds, depth)

    # create figure
    fig, axs = plt.subplots(1, 2, figsize=(10, 3), constrained_layout=True)

    # create figure g-function (lin)
    # plot g-functions
    axs[0].plot(time_in_seconds/8760/3600, result / (2 * math.pi * 2.4))

    # layout
    axs[0].set_title("Step response when applying a constant heat injection")
    axs[0].set_xlabel("Time (years)")
    axs[0].set_ylabel("Temperature difference (K)")
    axs[0].set_ylim(0, 5)
    axs[0].set_xlim(0, 40)

    # create figure g-function (semi-log)
    # plot g-functions
    axs[1].plot(time_dimensionless, result)

    # layout
    axs[1].set_title("Equivalent g-function for the step response")
    axs[1].set_xlabel("ln(t/ts)")
    axs[1].set_ylabel("g-function value")
    axs[1].set_ylim(-2, 60)

    # plt.legend()
    plt.show()


def figure_2():
    """
    This function generates the second figure of the article.
    """

    # initiate ground data
    ground_data = GroundData(100, 6, 2.4, 10, 0.12, 10, 10)

    # initiate borefield model
    borefield = Borefield()
    borefield.set_ground_parameters(ground_data)

    # initiate depth array
    depths = np.array([25, 50, 100, 150, 200])

    # dimensionless time
    ts = 150**2 / (9 * ground_data.k_s)

    # time array
    nb_of_timesteps = 50
    time_dimensionless = np.linspace(2, 14, nb_of_timesteps)

    # convert to seconds
    time_in_seconds = np.exp(time_dimensionless) * ts

    # calculate g-functions
    results = np.zeros((5, nb_of_timesteps))
    for i in range(5):
        results[i] = borefield.gfunction(time_in_seconds, depths[i])

    # create figure
    plt.figure()

    # plot g-functions
    plt.plot(time_dimensionless, results[0], label="25m")
    plt.plot(time_dimensionless, results[1], label="50m")
    plt.plot(time_dimensionless, results[2], label="100m")
    plt.plot(time_dimensionless, results[3], label="150m")
    plt.plot(time_dimensionless, results[4], label="200m")

    # plot lines for Ra
    line1 = math.log(6*3600/ts)
    line2 = math.log((20 * 8760 + 730) * 3600 / ts)
    plt.vlines(line1, ymin=-5, ymax=5, colors="black", lw=0.75, ls="--")
    plt.vlines(line2, ymin=-5, ymax=50, colors="black", lw=0.75, ls="--")

    plt.annotate('', xy=(line1, -0.4), xytext=(line2, -0.4),
                 arrowprops=dict(arrowstyle='<->', color='black'))
    plt.text((line1+line2)/2, 0.2, "Ra", horizontalalignment='center')

    # layout
    plt.title("G-function values for different borefield depths")
    plt.xlabel("ln(t/ts)")
    plt.ylabel("g-function value")
    plt.ylim(-2, 60)

    plt.legend()
    plt.show()


def figure_3():
    """
    This function creates the third figure of the article.
    """

    # initiate borefield model
    borefield = Borefield()

    # initiate depth for evaluations
    nb_depths = 20
    depth_array = np.linspace(50, 350, nb_depths)

    # initiate list of borefield configurations
    configs = [(10, 10), (11, 11), (12, 12), (14, 14),
               (15, 15), (18, 18), (20, 20)]

    results = []

    for n1, n2 in configs:
        depths = []
        for H in depth_array:
            # set ground data
            ground_data = GroundData(H, 7, 2.4, 10, 0.12, n1, n2)

            # set ground data
            borefield.set_ground_parameters(ground_data)

            # calculate gfunction
            gfunction = borefield.gfunction(borefield.time, H)

            # calculate Ra
            Ra = (gfunction[2] - gfunction[1]) / (2 * math.pi * borefield.k_s)

            # add to depths
            depths.append(Ra)

        # add to results
        results.append(depths)

    # create figure
    plt.figure()
    for i, config in enumerate(configs):
        plt.plot(depth_array, results[i], label=str(config[0]) + "x" + str(config[1]))

    plt.title("Ra for different borefield configurations")
    plt.xlabel("Depth (m)")
    plt.ylabel("Ra (mK/W)")

    plt.legend()
    plt.show()


def figure_4():
    """
    This code creates the fourth figure of the article
    """
    # initiate borefield
    borefield = Borefield()

    # set the correct sizing method
    borefield.sizing_setup(L2_sizing=True)

    # initiate array with imbalances
    imbalance_array = np.linspace(200, 1600, 20)

    # initiate list of borefield configurations
    configs = [(10, 10), (11, 11), (12, 12), (14, 14),
               (15, 15), (18, 18), (20, 20)]

    # initiate loads
    monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, .117, 0.144])
    monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
    monthly_load_heating = monthly_load_heating_percentage * 100 * 10 ** 3  # kWh
    monthly_load_cooling_init = monthly_load_cooling_percentage * 100 * 10 ** 3  # kWh
    peak_cooling_init = np.array([0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.])  # Peak cooling in kW
    peak_heating = np.array([160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.])

    # set heating loads
    borefield.set_peak_heating(peak_heating)
    borefield.set_baseload_heating(monthly_load_heating)

    results = []
    for i, config in enumerate(configs):
        depth_array = []
        for imbalance in imbalance_array:
            # initiate ground data
            ground_data = GroundData(100, 7, 2.4, 10, 0.12, config[0], config[1])

            # set ground data
            borefield.set_ground_parameters(ground_data)

            # calculate loads
            extra_load = imbalance / 12 * 10 ** 3  # kWh
            monthly_load_cooling = monthly_load_cooling_init + extra_load
            peak_cooling = peak_cooling_init + extra_load / 730

            # set cooling loads
            borefield.set_peak_cooling(peak_cooling)
            borefield.set_baseload_cooling(monthly_load_cooling)
            try:
                depth = borefield.size()
                depth_array.append(depth)
            except:
                pass

        results.append(depth_array)

    # create figure
    plt.figure()
    for i, config in enumerate(configs):
        plt.plot(imbalance_array[:len(results[i])], results[i], label=str(config[0]) + "x" + str(config[1]))

    plt.title("Depth for different imbalances")
    plt.xlabel("Imbalance (MWh/y)")
    plt.ylabel("Depth (m)")

    plt.legend()
    plt.show()

if __name__ == "__main__":
    # figure_1()
    # figure_2()
    # figure_3()
    # figure_4()