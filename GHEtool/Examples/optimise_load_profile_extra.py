"""
This document is an example of load optimisation.
First an hourly profile is imported and a fixed borefield size is set.
Then, based on a load-duration curve, the heating and cooling load is altered in order to fit as much load as possible on the field.
The results are returned.

"""
import numpy as np

from GHEtool import *
from GHEtool.Methods import *


def optimise():
    data = GroundFluxTemperature(1.8, 9.7, flux=0.08)
    borefield = Borefield()
    borefield.ground_data = data
    borefield.Rb = 0.131
    borefield.create_rectangular_borefield(3, 5, 6, 6, 100, 1, 0.07)
    load = HourlyBuildingLoad(efficiency_heating=4.5, efficiency_cooling=20)
    load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True, separator=";",
                             col_cooling=0, col_heating=1)

    # optimise the load for a 10x10 field (see data above) and a fixed length of 150m.
    # first for an optimisation based on the power
    building_load, _ = optimise_load_profile_energy(borefield, load)
    borefield.load = building_load

    print(f'Max heating power (primary): {borefield.load.max_peak_extraction:,.0f}kW')
    print(f'Max cooling power (primary): {borefield.load.max_peak_injection:,.0f}kW')

    print(
        f'Total energy extracted from the borefield over simulation period: {np.sum(borefield.load.monthly_baseload_extraction_simulation_period):,.0f}MWh')
    print(
        f'Total energy injected in the borefield over simulation period): {np.sum(borefield.load.monthly_baseload_injection_simulation_period):,.0f}MWh')
    print('------------------------------------------------------------------------')
    borefield.calculate_temperatures(hourly=False)
    borefield.print_temperature_profile(plot_hourly=False)


if __name__ == "__main__":  # pragma: no cover
    optimise()
