"""
This document contains the sizing of a borefield, according to the three sizing methods in GHEtool
for a swimming pool. This swimming pool has an enormous imbalance towards heat extraction.
"""
# import all the relevant functions
from GHEtool import *
import time
from statistics import mean
import numpy as np

if __name__ == "__main__":



    # initiate ground, fluid and pipe data
    ground_data = GroundFluxTemperature(k_s=3, T_g=10, volumetric_heat_capacity= 2.4 * 10**6, flux=0.06)
    fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
    pipe_data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 1)

    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(15, 20, 6, 6, 240, 4)
    #borefield.set_Rb(0.12)

    options = {'nSegments': 12,
                   'segment_ratios': None,
                   'disp': False,
                   'profiles': True,
                   'method': 'equivalent',
                   'cyl_correction': False,
                   'use_short_term_g_function': False,
                   'use_short_term_trc': False,
                   'to_combine': False
                   }

    borefield.set_options_gfunction_calculation(options)

    # set temperature bounds
    borefield.set_min_ground_temperature(3)
    borefield.set_max_ground_temperature(17)

    borefield.calculation_setup(max_nb_of_iterations=100)

    # load the hourly profile
    load = HourlyGeothermalLoad()
    load.load_hourly_profile("swimming_pool.csv", header=True, separator=";", col_heating=1, col_cooling=0)
    borefield.load = load

    SEER = 20
    SCOP = 4

    # load hourly heating and cooling load and convert it to geothermal loads
    primary_geothermal_load = HourlyGeothermalLoad(simulation_period=load.simulation_period)
    primary_geothermal_load.set_hourly_cooling(load.hourly_cooling_load.copy() * (1 + 1 / SEER))
    primary_geothermal_load.set_hourly_heating(load.hourly_heating_load.copy() * (1 - 1 / SCOP))

    #cooling_load = primary_geothermal_load.hourly_cooling_load
    #heating_load = primary_geothermal_load.hourly_heating_load

   # np.savetxt("swimmingpool_test.csv", np.column_stack((cooling_load, heating_load)), delimiter=",", fmt='%s')

    # set geothermal load
    borefield.load = primary_geothermal_load



    # according to L4
    L4_start = time.time()
    #depth_L4 = borefield.size(100, L4_sizing=True)
    L4_stop = time.time()


    #print("The sizing according to L4 took", round((L4_stop - L4_start) * 1000, 4), "ms and was", depth_L4, "m.")
    #print("The average ground temperature for L4 is", borefield._Tg(H=depth_L4))

    borefield.print_temperature_profile(plot_hourly=True)

