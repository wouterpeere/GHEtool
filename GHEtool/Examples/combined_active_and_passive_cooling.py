"""
This file contains an example code of how the EERCombined works. For an auditorium building, two cases for the
active/passive combination will be considered:
    1) Default active cooling in certain months
    2) Active cooling above a certain temperature threshold

It is shown that a temperature threshold will lead to 90% less active cooling over the simulation period. Due to the
imbalance, active cooling will take up a smaller percentage of cooling load over time.
"""

import numpy as np
import matplotlib.pyplot as plt

from GHEtool import *

# set general parameters
ground_data = GroundFluxTemperature(3, 10)
fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)

load = HourlyBuildingLoad(efficiency_heating=5)  # use SCOP of 5 for heating
load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True,
                         separator=";", col_cooling=0, col_heating=1)

eer_active = EER(np.array([15.943, 6.153]), np.array([5, 30]))  # based on the data of the WRE092 chiller of Galletti


def default_cooling_in_summer():
    borefield = Borefield()
    borefield.create_rectangular_borefield(3, 3, 6, 6, 110, 0.7, 0.075)
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.set_max_avg_fluid_temperature(25)
    borefield.set_min_avg_fluid_temperature(3)

    # create combined active and passive EER
    eer = EERCombined(20, eer_active, months_active_cooling=[6, 7, 8])

    # set variables
    load.eer = eer
    borefield.load = load
    print(borefield)
    borefield.print_temperature_profile(plot_hourly=True)

    # get active cooling data
    active_cooling_array = borefield.load.eer.get_time_series_active_cooling(borefield.results.peak_injection,
                                                                             load.month_indices)
    active_cooling_energy = load.hourly_cooling_load_simulation_period * active_cooling_array
    passive_cooling_energy = load.hourly_cooling_load_simulation_period * np.invert(active_cooling_array)
    print(f'{np.sum(active_cooling_energy) / load.simulation_period:.0f}kWh of active cooling on average per year. '
          f'This is {np.sum(active_cooling_energy) / np.sum(load.hourly_cooling_load_simulation_period) * 100:.2f}% '
          f'of the building cooling load.')
    print(
        f'The peak power for active and passive cooling is: {np.max(active_cooling_energy):.2f}kW and {np.max(passive_cooling_energy):.2f}kW respectively.')

    # create graphs
    fig = plt.figure()
    ax = fig.add_subplot(111)
    time_array = load.time_L4 / 12 / 3600 / 730
    ax.plot(time_array, active_cooling_array)
    fig.suptitle('Active cooling on')
    ax.set_xlabel('Time [years]')
    ax.set_xticks(range(0, load.simulation_period + 1, 2))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(np.sum(
        np.reshape(load.hourly_cooling_load_simulation_period * active_cooling_array, (load.simulation_period, 8760)),
        axis=1))
    fig.suptitle('Active cooling energy')
    ax.set_xlabel('Time [years]')
    ax.set_ylabel('Energy per year [kWh]')
    ax.set_xticks(range(0, load.simulation_period + 1, 2))
    plt.show()
    return np.sum(active_cooling_energy)


def active_above_threshold():
    borefield = Borefield()
    borefield.create_rectangular_borefield(3, 3, 6, 6, 110, 0.7, 0.075)
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.set_max_avg_fluid_temperature(25)
    borefield.set_min_avg_fluid_temperature(3)

    eer = EERCombined(20, eer_active, threshold_temperature=17)

    load.eer = eer
    borefield.load = load

    borefield.print_temperature_profile(plot_hourly=True)

    # get active cooling data
    active_cooling_array = borefield.load.eer.get_time_series_active_cooling(borefield.results.peak_injection,
                                                                             load.month_indices)
    active_cooling_energy = load.hourly_cooling_load_simulation_period * active_cooling_array
    passive_cooling_energy = load.hourly_cooling_load_simulation_period * np.invert(active_cooling_array)
    print(f'{np.sum(active_cooling_energy) / load.simulation_period:.0f}kWh of active cooling on average per year. '
          f'This is {np.sum(active_cooling_energy) / np.sum(load.hourly_cooling_load_simulation_period) * 100:.2f}% '
          f'of the building cooling load.')
    print(
        f'The peak power for active and passive cooling is: {np.max(active_cooling_energy):.2f}kW and {np.max(passive_cooling_energy):.2f}kW respectively.')

    # create graphs
    fig = plt.figure()
    ax = fig.add_subplot(111)
    time_array = load.time_L4 / 12 / 3600 / 730
    ax.plot(time_array, active_cooling_array)
    fig.suptitle('Active cooling on')
    ax.set_xlabel('Time [years]')
    ax.set_xticks(range(0, load.simulation_period + 1, 2))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(np.sum(
        np.reshape(load.hourly_cooling_load_simulation_period * active_cooling_array, (load.simulation_period, 8760)),
        axis=1))
    fig.suptitle('Active cooling energy')
    ax.set_xlabel('Time [years]')
    ax.set_ylabel('Energy per year [kWh]')
    ax.set_xticks(range(0, load.simulation_period + 1, 2))
    plt.show()
    return np.sum(active_cooling_energy)


if __name__ == "__main__":
    default_cooling_in_summer()
    active_above_threshold()
