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
    borefield.set_max_fluid_temperature(20)
    borefield.set_min_fluid_temperature(5.5)
    hourly_load_building = HourlyBuildingLoad(efficiency_cooling=7, efficiency_heating=6)
    hourly_load_building.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True,
                                             separator=";", col_cooling=0, col_heating=1)
    borefield.load = hourly_load_building
    borefield.load.simulation_period = 5

    # get weather data
    weather_file = open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb')
    weather_file.seek(0)
    TMY: pd.DataFrame = pd.read_csv(weather_file, sep=",", header=None, skiprows=8)

    TMY.drop(columns=TMY.columns[:5], inplace=True)
    solar: np.ndarray = np.tile(np.array(TMY.iloc[:, 8]), 20)
    temperature: np.ndarray = np.tile(np.array(TMY.iloc[:, 1]), 20)

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

    # get weather data
    weather_file = open(FOLDER.joinpath("test/unit-tests/data/test_epw.epw"), 'rb')
    weather_file.seek(0)
    TMY: pd.DataFrame = pd.read_csv(weather_file, sep=",", header=None, skiprows=8)

    TMY.drop(columns=TMY.columns[:5], inplace=True)
    solar: np.ndarray = np.tile(np.array(TMY.iloc[:, 8]), 20)
    temperature: np.ndarray = np.tile(np.array(TMY.iloc[:, 1]), 20)

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


def swimming_pool():
    borefield = Borefield()
    borefield.create_rectangular_borefield(20, 20, 6, 6, 200, 4, 0.075)
    borefield.ground_data = ground_data
    borefield.fluid_data = fluid_data
    borefield.pipe_data = pipe_data
    borefield.flow_data = flow_data
    borefield.calculation_setup(use_constant_Rb=False)
    borefield.set_max_fluid_temperature(17)
    borefield.set_min_fluid_temperature(3)
    hourly_load = HourlyBuildingLoad(efficiency_dhw=3.5)
    hourly_load.load_hourly_profile(FOLDER.joinpath("test/methods/hourly_data/swimming_pool.csv"), header=True,
                                    separator=";", col_cooling=0, col_heating=1, col_dhw=2)
    borefield.load = hourly_load
    borefield.calculate_temperatures(hourly=True)
    tf_init = borefield.results.Tf
    # borefield.print_temperature_profile(plot_hourly=True)
    triple_solar.surface = 200
    import time
    start = time.time()
    load, regen_ts_200 = calculate_regeneration(borefield, triple_solar, algorithm='proceeding', simulation_horizon=500)
    print(time.time() - start)
    start = time.time()
    load, regen_ts_200_2 = calculate_regeneration(borefield, triple_solar, algorithm='proceeding',
                                                  simulation_horizon=50)
    print(time.time() - start)
    plt.figure()
    plt.plot(regen_ts_200, regen_ts_200_2)
    plt.figure()
    plt.plot(regen_ts_200 - regen_ts_200_2)
    plt.show()

    borefield.load = load
    borefield.calculate_temperatures(hourly=True)
    tf_200 = borefield.results.Tf

    # simulate with 200m² of triple solar
    triple_solar.surface = 400
    load, regen_ts_400 = calculate_regeneration(borefield, triple_solar, algorithm='proceeding')
    borefield.load = load
    borefield.calculate_temperatures(hourly=True)
    tf_400 = borefield.results.Tf

    # simulate with 200m² of aqsol
    aqsol.surface = 4000
    load, regen_aqsol = calculate_regeneration(borefield, aqsol, algorithm='proceeding')
    borefield.load = load
    borefield.calculate_temperatures(hourly=True)
    tf_aq_200 = borefield.results.Tf

    plt.figure()
    plt.plot(tf_init, label="Initial Temperature")
    plt.plot(tf_200, label="With 200 m² of Triple Solar")
    plt.plot(tf_400, label="With 400 m² of Triple Solar")
    plt.plot(tf_aq_200, label="With 4000 m² of Aqsol")
    plt.xlabel("Time [hours]")
    plt.ylabel("Temperature [C]")
    plt.legend()

    plt.figure()
    plt.plot(regen_ts_200, label="Triple Solar 200m²")
    plt.plot(regen_ts_400, label="Triple Solar 400m²")
    plt.plot(regen_aqsol, label="Aqsol 4000m²")
    plt.xlabel("Time [hours]")
    plt.ylabel("Power [kW]")
    plt.show()


if __name__ == '__main__':
    auditorium()
    auditorium_variation()
    swimming_pool()
