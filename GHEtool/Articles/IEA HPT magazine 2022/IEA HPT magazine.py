"""
This document contains all the scripts for coming up with the figures of the article written by
Verleyen L., Peere W. and Helsen L.
"""

from GHEtool import Borefield, GroundData
import matplotlib.pyplot as plt
import numpy as np


def figure_1():
    """
    This function generates Figure 1 of the article.
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
    plt.plot(time_dimensionless, results[0], label="25m")
    plt.plot(time_dimensionless, results[1], label="50m")
    plt.plot(time_dimensionless, results[2], label="100m")
    plt.plot(time_dimensionless, results[3], label="150m")
    plt.plot(time_dimensionless, results[4], label="200m")
    plt.title("G-function values for different borefield depths")
    plt.xlabel("ln(t/ts)")
    plt.ylabel("g-function value")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    figure_1()