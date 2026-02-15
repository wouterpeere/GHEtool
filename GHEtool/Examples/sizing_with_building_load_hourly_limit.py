"""
This document contains an example on sizing with an hourly building load and the difference between L3 and L4 sizing.
It can be seen that sizing with an hourly method not only gives a completely different result, but also that the SCOP
differs and is more accurate.
"""

from GHEtool import *
from GHEtool.VariableClasses.Efficiency._Efficiency import combine_n_heat_pumps
from typing import Tuple

# initiate ground data
data = GroundFluxTemperature(2.1, 10, flux=0.07)
borefield_gt = gt.borefield.Borefield.rectangle_field(10, 12, 6, 6, 110, 1, 0.075)

points_HP500 = np.array([
    [-4.5, 84.7],
    [-4.5, 66.3],
    [-4.5, 38.6],
    [-1.5, 93.0],
    [-1.5, 72.9],
    [-1.5, 42.4],
    [3.5, 107.8],
    [3.5, 84.6],
    [3.5, 49.4],
    [8.5, 123.5],
    [8.5, 97.4],
    [8.5, 56.9],
    [11.5, 133.2],
    [11.5, 105.4],
    [11.5, 61.4],
])
eff_HP500 = np.array([
    3.87, 4.12, 3.78,
    4.12, 4.39, 4.04,
    4.57, 4.89, 4.49,
    5.10, 5.50, 5.08,
    5.48, 5.92, 5.48,
])
points_HP400 = np.array([
    [-4.5, 67.2],
    [-4.5, 49.9],
    [-4.5, 29.1],
    [-1.5, 73.7],
    [-1.5, 54.8],
    [-1.5, 32.0],
    [3.5, 85.2],
    [3.5, 63.5],
    [3.5, 37.2],
    [8.5, 97.7],
    [8.5, 73.1],
    [8.5, 42.7],
    [11.5, 105.7],
    [11.5, 79.0],
    [11.5, 46.0],
])
eff_HP400 = np.array([
    3.91, 4.38, 3.99,
    4.14, 4.64, 4.27,
    4.58, 5.16, 4.77,
    5.12, 5.80, 5.34,
    5.51, 6.22, 5.75,
])
cascaded_system_points, cascaded_system_eff = combine_n_heat_pumps([points_HP500] * 4 + [points_HP400],
                                                                   [eff_HP500] * 4 + [eff_HP400])

cop_system = COP(cascaded_system_eff, cascaded_system_points, True)


def L3_sizing() -> Tuple[float, float]:
    """
    Size the borefield with a monthly sizing method.

    Returns
    -------
    length, SCOP
    """
    # initiate borefield
    borefield = Borefield()

    # set parameters
    borefield.set_min_fluid_temperature(0)
    borefield.set_max_fluid_temperature(25)

    # set ground data in borefield
    borefield.ground_data = data

    # set Rb
    borefield.Rb = 0.12

    # set borefield
    borefield.set_borefield(borefield_gt)

    # load the hourly profile
    load = HourlyBuildingLoad(efficiency_heating=cop_system)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"), header=True, separator=";")
    borefield.load = load

    # size the borefield and plot the resulting temperature evolution
    length = borefield.size(100, L3_sizing=True)
    print(
        f'When sizing with an L3 method (without limit), the required borehole length is {length:.2f}m. '
        f'The SCOP is {borefield.load.SCOP_total:.2f}.')

    # with limit
    borefield.load._limit_to_max_heat_pump_power = True
    length = borefield.size(100, L3_sizing=True)
    borefield.print_temperature_profile()
    return length


def L4_sizing() -> Tuple[float, float]:
    """
    Size the borefield with an hourly sizing method.

    Returns
    -------
    length, SCOP
    """
    # initiate borefield
    borefield = Borefield()

    # set parameters
    borefield.set_min_fluid_temperature(0)
    borefield.set_max_fluid_temperature(25)

    # set ground data in borefield
    borefield.ground_data = data

    # set Rb
    borefield.Rb = 0.12

    # set borefield
    borefield.set_borefield(borefield_gt)

    # load the hourly profile
    load = HourlyBuildingLoad(efficiency_heating=cop_system)
    load.load_hourly_profile(FOLDER.joinpath("Examples/hourly_profile.csv"), header=True, separator=";")
    borefield.load = load

    # size the borefield and plot the resulting temperature evolution
    length = borefield.size(100, L4_sizing=True)
    print(
        f'When sizing with an L4 method, the required borehole length is {length:.2f}m. '
        f'The SCOP is {borefield.load.SCOP_total:.2f}.')
    borefield.load._limit_to_max_heat_pump_power = True
    length = borefield.size(100, L4_sizing=True)
    print(
        f'When sizing with an L4 method (with limit), the required borehole length is {length:.2f}m. '
        f'The SCOP is {borefield.load.SCOP_total:.2f}.')
    missing_power = borefield.load.hourly_heating_load_simulation_period - borefield.load.cop._get_max_power(
        borefield.results.Tf)
    missing_power = np.maximum(missing_power, 0)
    print(f'Over the whole simulation period, a maximum of {max(missing_power):.2f} kW cannot be delivered by the '
          f'cascaded heat pumps at 0°C. This accumulates to {np.sum(missing_power):.2f} kWh over the whole simulation period.')

    borefield.set_min_fluid_temperature(3)
    length = borefield.size(100, L4_sizing=True)
    print(
        f'When sizing with an L4 method (with limit at 3°C), the required borehole length is {length:.2f}m. '
        f'The SCOP is {borefield.load.SCOP_total:.2f}.')
    missing_power = borefield.load.hourly_heating_load_simulation_period - borefield.load.cop._get_max_power(
        borefield.results.Tf)
    missing_power = np.maximum(missing_power, 0)
    print(f'Over the whole simulation period, a maximum of {max(missing_power):.2f} kW cannot be delivered by the '
          f'cascaded heat pumps at 0°C. This accumulates to {np.sum(missing_power):.2f} kWh over the whole simulation period.')

    borefield.print_temperature_profile(plot_hourly=True)
    borefield.load.SEER
    return length, borefield.load.SCOP_heating


if __name__ == "__main__":
    L3_sizing()
    L4_sizing()
