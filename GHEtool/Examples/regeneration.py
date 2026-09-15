"""
This file contains a couple of examples for the regeneration.
"""
import matplotlib.pyplot as plt

from GHEtool import *
from GHEtool.Methods.regeneration import calculate_regeneration

# get weather data
weather_file = open(FOLDER.joinpath("Examples/BEL_Brussels.064510_IWEC.epw"), 'rb')
weather_file.seek(0)
TMY: pd.DataFrame = pd.read_csv(weather_file, sep=",", header=None, skiprows=8)

TMY.drop(columns=TMY.columns[:5], inplace=True)
solar: np.ndarray = np.tile(np.array(TMY.iloc[:, 8]), 20)
temperature: np.ndarray = np.tile(np.array(TMY.iloc[:, 1]), 20)

# illustrative figures from datasheets
surface = 200  # m²

a0 = 0.45
a1 = 24.76  # W/K/m²
dualsun_spring = Regeneration(power=solar * a0, temperature=temperature, a1=a1)

a0 = 0.473
a1 = 19.91  # W/K/m²
dualsun_max = Regeneration(power=solar * a0, temperature=temperature, a1=a1)

a0 = 0.47
a1 = 22.9  # W/k/m²
triple_solar = Regeneration(power=solar * a0, temperature=temperature, a1=a1)

a0 = 0.912
a1 = 15.66
aqsol = Regeneration(power=solar * a0, temperature=temperature, a1=a1)

ground_data = GroundFluxTemperature(2, 10)
fluid_data = TemperatureDependentFluidData('MPG', 0, mass_percentage=False)
flow_data = ConstantDeltaTFlowRate(delta_temp_extraction=3, delta_temp_injection=3)
pipe_data = DoubleUTube(1, 0.013, 0.016, 0.4, 0.035)


def auditorium():
    ground_data = GroundFluxTemperature(2, 10)
    fluid_data = TemperatureDependentFluidData('MPG', 0, mass_percentage=False)
    flow_data = ConstantDeltaTFlowRate(delta_temp_extraction=3, delta_temp_injection=3)
    pipe_data = DoubleUTube(1, 0.013, 0.016, 0.4, 0.035)
    borefield = Borefield()
    borefield.create_rectangular_borefield(4, 3, 6, 6, 105, 0.7, 0.07)
    borefield.ground_data = ground_data
    borefield.fluid_data = fluid_data
    borefield.flow_data = flow_data
    borefield.pipe_data = pipe_data
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_fluid_temperature(25)
    borefield.set_min_fluid_temperature(5.5)
    hourly_load_building = HourlyBuildingLoad(efficiency_cooling=7, efficiency_heating=6)
    hourly_load_building.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True,
                                             separator=";", col_cooling=0, col_heating=1)
    borefield.load = hourly_load_building
    borefield.load.simulation_period = 5

    # initiate regeneration object
    a0 = 0.45
    a1 = 24.76  # W/K/m²

    surface = 150  # m²

    regeneration_object = Regeneration(power=solar * a0, temperature=temperature, a1=a1, surface=surface)

    profile, yearly = calculate_regeneration(
        borefield=copy.deepcopy(borefield),
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='yearly')

    # the summer period gets no regeneration to ensure that the maximum fluid temperature is not crossed.
    plt.figure()
    plt.plot(borefield.load.hourly_net_resulting_injection_power, label="Building load")
    plt.plot(yearly, label="Regeneration")
    plt.xlabel('Time [hours]')
    plt.ylabel('Power [kW]')
    plt.legend()
    plt.xlim(0, 8760 * 5)
    plt.show()

    borefield.load = profile
    borefield.print_temperature_profile(plot_hourly=True)


def auditorium_variation():
    ground_data = GroundFluxTemperature(2, 10)
    fluid_data = TemperatureDependentFluidData('MPG', 0, mass_percentage=False)
    flow_data = ConstantDeltaTFlowRate(delta_temp_extraction=3, delta_temp_injection=3)
    pipe_data = DoubleUTube(1, 0.013, 0.016, 0.4, 0.035)
    borefield = Borefield()
    borefield.create_rectangular_borefield(4, 3, 6, 6, 105, 0.7, 0.07)
    borefield.ground_data = ground_data
    borefield.fluid_data = fluid_data
    borefield.flow_data = flow_data
    borefield.pipe_data = pipe_data
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_fluid_temperature(20)
    borefield.set_min_fluid_temperature(5.5)
    hourly_load_building = HourlyBuildingLoad(efficiency_cooling=7, efficiency_heating=6)
    hourly_load_building.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True,
                                             separator=";", col_cooling=0, col_heating=1)
    borefield.load = hourly_load_building
    borefield.load.simulation_period = 10

    # initiate regeneration object
    a0 = 0.45
    a1 = 24.76  # W/K/m²

    surface = 200  # m²

    regeneration_object = Regeneration(power=solar * a0 * surface, temperature=temperature, a1=a1 * surface)

    proceeding_my, proceeding = calculate_regeneration(
        borefield=copy.deepcopy(borefield),
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='proceeding')
    yearly_my, yearly = calculate_regeneration(
        borefield=copy.deepcopy(borefield),
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='yearly')
    total_my, total = calculate_regeneration(
        borefield=copy.deepcopy(borefield),
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='total')
    proceeding_extra_my, proceeding_extra = calculate_regeneration(
        borefield=copy.deepcopy(borefield),
        regen_obj=regeneration_object,
        rules=(1, 2, 3),
        algorithm='proceeding_extra')
    plt.figure()
    plt.plot(total, label='Total')
    plt.plot(yearly, label='Yearly')
    plt.plot(proceeding, label='Proceeding')
    plt.plot(proceeding_extra, label='Proceeding extra')

    plt.xlabel('Time [hours]')
    plt.ylabel('Regeneration power [kW]')
    plt.title('Different regeneration strategies')
    plt.legend()
    plt.show()

    data = {
        'Yearly': yearly_my,
        'Total': total_my,
        'Proceeding w/o': proceeding_my,
        'Proceeding': proceeding_extra_my
    }

    fig, axes = plt.subplots(
        nrows=len(data),
        ncols=1,
        figsize=(9, 10),
        sharex=True,
    )

    for ax, (key, value) in zip(axes, data.items()):
        borefield.load = value
        borefield.calculate_temperatures(hourly=True)
        tf = borefield.results.Tf
        time_array = borefield.load.time_L4 / 12 / 3600 / 730

        ax.plot(time_array, tf, linewidth=0.7)
        ax.set_title(key)
        ax.set_ylabel('Fluid temperature [°C]')

        ax.axhline(
            borefield.Tf_min,
            color='black',
            linestyle='dashed',
            linewidth=0.7,
        )
        ax.axhline(
            borefield.Tf_max,
            color='black',
            linestyle='dashed',
            linewidth=0.7,
        )

        ax.set_xlim(0, borefield.simulation_period)

    axes[-1].set_xlabel('Time [year]')
    axes[-1].set_xticks(range(0, borefield.simulation_period + 1, 2))

    fig.tight_layout()
    plt.show()


def office():
    borefield = Borefield()
    borefield.create_rectangular_borefield(8, 9, 6, 6, 100, 4, 0.075)
    fluid_data = TemperatureDependentFluidData('MPG', 0, mass_percentage=False)
    flow_data = ConstantDeltaTFlowRate(delta_temp_extraction=3, delta_temp_injection=3)
    pipe_data = DoubleUTube(1, 0.013, 0.016, 0.4, 0.035)
    ground_data = GroundFluxTemperature(2, 10)
    borefield.ground_data = ground_data
    borefield.fluid_data = fluid_data
    borefield.pipe_data = pipe_data
    borefield.flow_data = flow_data
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_fluid_temperature(25)
    borefield.set_min_fluid_temperature(0)
    hourly_load = HourlyBuildingLoad(efficiency_cooling=5)
    hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/office.csv"), header=True,
                                    separator=";", col_cooling=0, col_heating=1)
    borefield.load = hourly_load
    borefield.print_temperature_profile(plot_hourly=True)

    # initiate regeneration object
    a0 = 0.45
    a1 = 24.76  # W/K/m²

    surface = 200  # m²

    regeneration_object = Regeneration(power=solar * a0 * surface, temperature=temperature, a1=a1 * surface)
    load, regen = calculate_regeneration(borefield=borefield, regen_obj=regeneration_object)
    plt.figure()
    plt.plot(regen)
    plt.show()
    borefield.load = load
    borefield.print_temperature_profile(plot_hourly=True)


if __name__ == '__main__':
    office()
    auditorium()
    auditorium_variation()
