import copy

import numpy as np
import pandas as pd
import pygfunction as gt
import matplotlib.pyplot as plt

from GHEtool import *

# design parameters
ground_data = GroundConstantTemperature(2.29, 12.3, 2.41 * 10 ** 6)
pipe_data = DoubleUTube(2, 0.013, 0.016, 0.42, 0.065 / 2)
fluid_data = FluidData(vfr=0.8)
fluid_data.import_fluid_from_pygfunction(gt.media.Fluid('MPG', 25, 2))
r_b = 0.13 / 2  # 130 mm diameter
H = 120  # depth m

# TCO parameters
SEER_LW = 5
SEER_AC = 7  # EER(np.array([15.943, 6.153]), np.array([5, 30]))
SEER_PC = 20
# SCOP = COP(np.array(
#     [4.42, 5.21, 6.04, 7.52, 9.5, 3.99, 4.58, 5.21, 6.02, 6.83, 3.86, 4.39, 4.97,
#      5.62, 6.19, 3.8, 4.3, 4.86, 5.44, 5.9, 3.76, 4.25, 4.79, 5.34, 5.74]),
#     np.array([[-5, 1.06], [0, 1.25], [5, 1.45], [10, 1.66], [15, 1.9], [-5, 2.05], [0, 2.42], [5, 2.81], [10, 3.2],
#               [15, 3.54], [-5, 3.05], [0, 3.6], [5, 4.17], [10, 4.73], [15, 5.18], [-5, 4.04], [0, 4.77], [5, 5.54],
#               [10, 6.27], [15, 6.82], [-5, 5.03], [0, 5.95], [5, 6.9], [10, 7.81], [15, 8.46]]),
#     part_load=True, reference_nominal_power=1, nominal_power=1500)
SCOP = 5
SCOP_DHW = 3
SIMULATION_PERIOD = 25
E_PRICE = 0.10  # €/kWh
COST_BOREFIELD = 35  # €/lm
RDR = -0.0011  # %
COST_GSHP = 550  # €/kW
COST_ASHP = 650  # €/kW
COST_HEX = 46  # €/kW

vermogen_lw_terminal = 7 * 238
vermogen_lw_kantoor = 2 * 468
vermogen_lw_hotel = 3 * 330
vermogen_ww_terminal = 2 * 180
vermogen_ww_kantoor = 2 * 280
vermogen_ww_hotel = 2 * 280
vermogen_lw = vermogen_lw_terminal + vermogen_lw_hotel + vermogen_lw_kantoor
vermogen_ww = vermogen_ww_hotel + vermogen_ww_kantoor + vermogen_ww_terminal

# load data
eer_active_passive = EERCombined(SEER_PC, SEER_AC, 17)

kantoor = HourlyBuildingLoad(simulation_period=SIMULATION_PERIOD, efficiency_heating=SCOP,
                             efficiency_cooling=eer_active_passive, efficiency_dhw=SCOP_DHW)
terminal = HourlyBuildingLoad(simulation_period=SIMULATION_PERIOD, efficiency_heating=SCOP,
                              efficiency_cooling=eer_active_passive, efficiency_dhw=SCOP_DHW)
hotel = HourlyBuildingLoad(simulation_period=SIMULATION_PERIOD, efficiency_heating=SCOP,
                           efficiency_cooling=eer_active_passive, efficiency_dhw=SCOP_DHW)

kantoor.load_hourly_profile('kantoor.csv', decimal_seperator=',', col_cooling=0, col_heating=1)
terminal.load_hourly_profile('terminal.csv', decimal_seperator=',', col_cooling=0, col_heating=1)
hotel.load_hourly_profile('hotel.csv', decimal_seperator=',', col_cooling=0, col_heating=1)

sww = pd.read_csv('hotel.csv', header=0, sep=";", decimal=",")
hotel.add_dhw(np.array(sww['Totale warmtelevering [kW] SWW']))

combined = HourlyBuildingLoad(
    heating_load=kantoor.hourly_heating_load + terminal.hourly_heating_load + hotel.hourly_heating_load,
    cooling_load=kantoor.hourly_cooling_load + terminal.hourly_cooling_load + hotel.hourly_cooling_load,
    simulation_period=SIMULATION_PERIOD, efficiency_heating=SCOP, efficiency_cooling=eer_active_passive,
    efficiency_dhw=SCOP_DHW)
combined.add_dhw(np.array(sww['Totale warmtelevering [kW] SWW']))

# load borefield coordinates
coordinates = pd.read_csv('coordinatenlijst optie 1.csv', header=0, sep=";", decimal=",")
borefield1 = []
for idx, row in coordinates.iterrows():
    borefield1.append(gt.boreholes.Borehole(H=H + row['Z'], D=-row['Z'], r_b=r_b, x=row['X'], y=-row['Y']))

coordinates = pd.read_csv('coordinatenlijst optie 2.csv', header=0, sep=";", decimal=",")
borefield2 = []
for idx, row in coordinates.iterrows():
    borefield2.append(gt.boreholes.Borehole(H=H + row['Z'], D=-row['Z'], r_b=r_b, x=row['X'], y=row['Y']))


def make_results(borefield, name, sec_load=None):
    # get further results
    active_cooling_array = borefield.load.eer.get_time_series_active_cooling(borefield.results.peak_injection,
                                                                             borefield.load.month_indices)
    yearly_share_active_cooling = np.sum(
        np.reshape(borefield.load.hourly_cooling_load_simulation_period * active_cooling_array,
                   (SIMULATION_PERIOD, 8760)), axis=1) / borefield.load.yearly_injection_load_simulation_period * 100
    active_cooling_power = borefield.load.hourly_cooling_load_simulation_period * active_cooling_array
    passive_cooling_power = borefield.load.hourly_cooling_load_simulation_period * np.invert(active_cooling_array)
    active_cooling_energy = np.sum(np.reshape(active_cooling_power, (SIMULATION_PERIOD, 8760)), axis=1)
    passive_cooling_energy = np.sum(np.reshape(passive_cooling_power, (SIMULATION_PERIOD, 8760)), axis=1)

    # print numerical results
    print(f'\n{name}')
    print(f'Average SEER {borefield.load.SEER:.2f}')
    print(
        f'Geothermal heating: {borefield.load.max_peak_heating:.2f}kW | {borefield.load.yearly_average_heating_load / 1000:.2f}MWh')
    print(
        f'Geothermal active: {np.max(active_cooling_power):.2f}kW | {np.mean(active_cooling_energy) / 1000:.2f}MWh')
    print(
        f'Geothermal passive: {np.max(passive_cooling_power):.2f}kW | {np.mean(passive_cooling_energy) / 1000:.2f}MWh')
    if sec_load is not None:
        print(
            f'LW cooling: {np.max(sec_load.max_peak_cooling):.2f}kW | {sec_load.yearly_average_cooling_load / 1000:.2f}MWh')
        print(
            f'LW heating: {np.max(sec_load.max_peak_heating):.2f}kW | {sec_load.yearly_average_heating_load / 1000:.2f}MWh')

    make_TCO(borefield, sec_load)

    # plot active/passive and SEER
    fig3, ax5 = plt.subplots()
    ax5.plot(range(1, SIMULATION_PERIOD + 1), borefield.load.yearly_SEER, linestyle='-',
             label='SEER')
    ax2 = ax5.twinx()
    ax2.plot(range(1, SIMULATION_PERIOD + 1), yearly_share_active_cooling, linestyle='--',
             label='Actief koelen')

    handles1, labels1 = ax5.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    handles = handles1 + handles2
    labels = labels1 + labels2
    ax5.legend(handles, labels, loc='upper center', ncol=2)
    ax5.set_xlim(left=1, right=SIMULATION_PERIOD)
    ax5.set_ylim(bottom=7, top=15)
    ax2.set_ylim(bottom=30, top=70)
    ax5.set_xlabel('Tijd [jaar]')
    ax5.set_ylabel(f'Jaarlijks SEER [-]')
    ax2.set_ylabel(f'Jaarlijks aandeel actieve koeling [%]')

    if sec_load is None:
        # hybrid graph
        fig1, ax1 = plt.subplots()
        # First pie chart - Cooling load
        labels = ['BEO (A)', 'BEO (P)']
        sizes = [np.mean(active_cooling_energy), np.mean(passive_cooling_energy)]
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax1.set_title('Aandeel koeling')

    else:
        # hybrid graph
        fig1, ax1 = plt.subplots()
        # First pie chart - Cooling load
        labels = ['BEO (A)', 'BEO (P)', 'LW']
        sizes = [np.mean(active_cooling_energy), np.mean(passive_cooling_energy),
                 sec_load.yearly_average_cooling_load]
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax1.set_title('Aandeel koeling')

        # energy graph
        fig2, ax3 = plt.subplots()

        # Add sorted loads to plot
        ax3.plot(range(1, SIMULATION_PERIOD + 1),
                 borefield.load.yearly_heating_load_simulation_period / 1000,
                 'r-', label='Geothermische verwarming')
        ax3.plot(range(1, SIMULATION_PERIOD + 1),
                 borefield.load.yearly_cooling_load_simulation_period / 1000,
                 'b-', label='Geothermische koeling')

        # Add a second y-axis to the right
        ax4 = ax3.twinx()

        # Optionally, plot something on the second y-axis
        ax4.plot(range(1, SIMULATION_PERIOD + 1),
                 borefield.load.yearly_heating_peak_simulation_period,
                 'r--',
                 label='Geothermische piekverwarming')
        ax4.plot(range(1, SIMULATION_PERIOD + 1),
                 borefield.load.yearly_cooling_peak_simulation_period,
                 'b--',
                 label='Geothermische piekkoeling')

        # Combine handles and labels from both axes
        handles1, labels1 = ax3.get_legend_handles_labels()
        handles2, labels2 = ax4.get_legend_handles_labels()
        handles = handles1 + handles2
        labels = labels1 + labels2

        # Plot legend with combined handles and labels
        ax3.legend(handles, labels)

        ax3.set_xlim(left=1, right=SIMULATION_PERIOD)
        ax3.set_xlabel('Tijd [jaar]')
        ax3.set_ylabel(f'Energie [MWh]')

        # Optional: set labels and properties for the second y-axis
        ax4.set_ylabel(f'Vermogen [kW]')

    # plot borefield
    borefield.print_temperature_profile(plot_hourly=True)


def make_TCO(borefield, sec_load):
    active_cooling_array = borefield.load.eer.get_time_series_active_cooling(borefield.results.peak_injection,
                                                                             borefield.load.month_indices)
    active_cooling_power = borefield.load.hourly_cooling_load_simulation_period * active_cooling_array
    passive_cooling_power = borefield.load.hourly_cooling_load_simulation_period * np.invert(active_cooling_array)
    active_cooling_energy = np.sum(np.reshape(active_cooling_power, (borefield.load.simulation_period, 8760)),
                                   axis=1)
    passive_cooling_energy = np.sum(np.reshape(passive_cooling_power, (borefield.load.simulation_period, 8760)),
                                    axis=1)

    electricity_consumption_per_year = borefield.load.yearly_electricity_consumption

    peak_ac, peak_pc, peak_heating, lw_heating, lw_cooling = get_individual_powers_one_field(borefield, sec_load)

    investment_cost = np.sum(np.maximum(peak_heating, peak_ac)) * COST_GSHP \
                      + np.sum(peak_pc) * COST_HEX + borefield.number_of_boreholes * borefield.H * COST_BOREFIELD \
                      + np.sum(np.maximum(lw_heating, lw_cooling))

    if sec_load is not None:
        electricity_consumption_per_year += sec_load.yearly_cooling_load_simulation_period / SEER_LW
        investment_cost += max(np.max(sec_load.max_peak_cooling), 1481) * COST_ASHP
    else:
        # there is always an ASHP
        investment_cost += 1481 * COST_ASHP

    TCO = investment_cost + np.sum(
        [electricity_consumption_per_year[i - 1] * E_PRICE / (1 + RDR) ** i for i in range(1, 26)])
    print('---------------------------------------')
    print(f'Investment: €{investment_cost:,.0f}')
    print(
        f'Electricity cost: €{np.sum([electricity_consumption_per_year[i - 1] * E_PRICE / (1 + RDR) ** i for i in range(1, 26)]):,.0f}')
    print(f'TCO: €{TCO:,.0f}')


def get_individual_powers_one_field(borefield, sec_load=None):
    names = ["kantoor", "hotel", "terminal"]

    loads = [kantoor, hotel, terminal]

    peak_ac, peak_pc, peak_heating, lw_heating, lw_cooling = [], [], [], [], []

    for idx, load in enumerate(loads):
        load_temp = HourlyBuildingLoadMultiYear(load.hourly_heating_load_simulation_period,
                                                load.hourly_cooling_load_simulation_period,
                                                SCOP,
                                                eer_active_passive,
                                                load.hourly_dhw_load_simulation_period,
                                                SCOP_DHW)
        cooling_sec = np.array([0])
        heating_sec = np.array([0])
        if sec_load is not None:
            ratio = np.divide(borefield.load.hourly_cooling_load_simulation_period,
                              combined.hourly_cooling_load_simulation_period)
            load_temp.hourly_cooling_load = load_temp.hourly_cooling_load_simulation_period * np.nan_to_num(ratio,
                                                                                                            nan=1)
            cooling_sec = load.hourly_cooling_load_simulation_period * (1 - np.nan_to_num(ratio, nan=1))
            ratio = np.divide(borefield.load.hourly_heating_load_simulation_period,
                              combined.hourly_heating_load_simulation_period)
            load_temp.hourly_heating_load = load_temp.hourly_heating_load_simulation_period * np.nan_to_num(ratio,
                                                                                                            nan=1)
            heating_sec = load.hourly_heating_load_simulation_period * (1 - np.nan_to_num(ratio, nan=1))

        active_cooling_array = load_temp.eer.get_time_series_active_cooling(borefield.results.peak_injection,
                                                                            load_temp.month_indices)
        active_cooling_power = load_temp.hourly_cooling_load_simulation_period * active_cooling_array
        passive_cooling_power = load_temp.hourly_cooling_load_simulation_period * np.invert(active_cooling_array)

        peak_ac.append(np.max(active_cooling_power))
        peak_pc.append(np.max(passive_cooling_power))
        peak_heating.append(np.max(load_temp.max_peak_heating))
        lw_heating.append(np.max(heating_sec))
        lw_cooling.append(np.max(cooling_sec))
        print('***********')
        print(f'WW heating {names[idx]}: {peak_heating[idx]:.2f}kW')
        print(f'WW ac {names[idx]}: {peak_ac[idx]:.2f}kW')
        print(f'HEX pc {names[idx]}: {peak_pc[idx]:.2f}kW')
        print(f'LW heating {names[idx]}: {lw_heating[idx]:.2f}kW')
        print(f'LW cooling {names[idx]}: {lw_cooling[idx]:.2f}kW')

    return peak_ac, peak_pc, peak_heating, lw_heating, lw_cooling


def one_field():
    # initiate borefield
    borefield = Borefield(borefield=borefield1, load=combined)

    borefield.ground_data = ground_data
    borefield.set_pipe_parameters(pipe_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_max_avg_fluid_temperature(17)
    borefield.set_min_avg_fluid_temperature(2)

    # do calculations
    # 1) all load on one field
    borefield.set_max_avg_fluid_temperature(17)
    borefield.calculate_temperatures(hourly=True)
    make_results(borefield, 'All load on one field')

    # 2p) optimise power (100% passive)
    _, sec_load = borefield.optimise_load_profile_power(combined)
    borefield.calculate_temperatures(hourly=True)
    make_results(borefield, 'Optimise power, 100% passive', sec_load)

    # # 2e) optimise energy (100% passive)
    # borefield.set_max_avg_fluid_temperature(16)
    # _, sec_load = borefield.optimise_load_profile_energy(combined)
    # borefield.calculate_temperatures(hourly=True)
    # make_results(borefield, 'Optimise energy, 100% passive', sec_load)

    # # 3p) optimise power
    # borefield.set_max_avg_fluid_temperature(25)
    # _, sec_load = borefield.optimise_load_profile_power(combined)
    # borefield.calculate_temperatures(hourly=True)
    # make_results(borefield, 'Optimise power', sec_load)
    #
    # # 3e) optimise energy
    # borefield.set_max_avg_fluid_temperature(25)
    # _, sec_load = borefield.optimise_load_profile_energy(combined)
    # borefield.calculate_temperatures(hourly=True)
    # make_results(borefield, 'Optimise energy', sec_load)

    # adapt size borefield

    borefield_smaller = [bor for bor in borefield1 if bor.y > -74]
    borefield.borefield = borefield_smaller
    # 4p) optimise power
    borefield.set_max_avg_fluid_temperature(25)
    _, sec_load = borefield.optimise_load_profile_power(combined)
    borefield.calculate_temperatures(hourly=True)
    make_results(borefield, 'Optimise power, +- 50% koelvermogen', sec_load)

    # # 4e) optimise energy
    # borefield.set_max_avg_fluid_temperature(25)
    # _, sec_load = borefield.optimise_load_profile_energy(combined)
    # borefield.calculate_temperatures(hourly=True)
    # make_results(borefield, 'Optimise energy, max 50% cooling', sec_load)


def multiple_fields():
    def select_borefield(x_min, x_max, y_max):
        borefield_temp = []
        for bor in borefield1:
            if bor.x >= x_min and bor.x < x_max and bor.y > -y_max:
                borefield_temp.append(bor)
        return borefield_temp

    borefield_kantoor = select_borefield(0, 70, 120)
    borefield_hotel = select_borefield(70, 100, 120)
    borefield_terminal = select_borefield(100, 180, 120)

    borefields = [Borefield(borefield=borefield_kantoor, load=kantoor),
                  Borefield(borefield=borefield_hotel, load=hotel),
                  Borefield(borefield=borefield_terminal, load=terminal)]

    names = ["kantoor", "hotel", "terminal"]

    for idx, borefield in enumerate(borefields):
        borefield.ground_data = ground_data
        borefield.set_pipe_parameters(pipe_data)
        borefield.set_fluid_parameters(fluid_data)
        borefield.set_max_avg_fluid_temperature(17)
        borefield.set_min_avg_fluid_temperature(2)

        borefield.calculate_temperatures(hourly=True)
        make_results(borefield, names[idx])


if __name__ == "__main__":
    one_field()
    # multiple_fields()
