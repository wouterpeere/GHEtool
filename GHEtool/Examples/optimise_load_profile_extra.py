"""
This document is an example of load optimisation.
First an hourly profile is imported and a fixed borefield size is set.
Then, based on a load-duration curve, the heating and cooling load is altered in order to fit as much load as possible on the field.
The results are returned.

"""
import numpy as np

from GHEtool import *
from GHEtool.Methods import *

import time


def optimise():
    data = GroundFluxTemperature(2, 9.6, flux=0.07)
    borefield = Borefield()
    borefield.ground_data = data
    borefield.pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
    borefield.flow_data = ConstantFlowRate(mfr=0.3)
    borefield.borehole.use_constant_Rb = False
    borefield.create_rectangular_borefield(20, 4, 6, 6, 150, 1, 0.07)
    load = HourlyBuildingLoad(efficiency_heating=5, efficiency_cooling=20)
    load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\hourly_profile.csv"), header=True,
                             separator=";", col_cooling=1, col_heating=0)
    load.simulation_period = 10
    borefield.set_min_fluid_temperature(3)
    borefield.USE_SPEED_UP_IN_SIZING = False
    # first optimise with the speed
    start = time.time()
    building_load, _ = optimise_load_profile_energy(borefield, load)
    borefield.load = building_load
    print(time.time() - start)
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
