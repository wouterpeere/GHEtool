"""
Different possibilities for dividing the finite line source segments are compared. When using the IBPSA borefield model 
in Modelica for validation purposes, ensure that the segments are defined analogously to those in pygfunction. The default
setting in pygfunction does not use equal segment lengths, whereas Modelica does. Therefore, you need to enforce equal 
segment lengths in pygfunction by setting 'segment_ratios': None. Additionally, the default number of segments in 
Modelica is 10, while in pygfunction it is 12. Adjust one of these settings to ensure the results are comparable.

References:
-----------
    - Meertens, L., Peere, W., and Helsen, L. (2024). Influence of short-term dynamic effects on geothermal borefield size. 
In _Proceedings of International Ground Source Heat Pump Association Conference 2024_. Montreal (Canada), 28-30 May 2024. 
https://doi.org/10.22488/okstate.24.000004 
    - Peere, W., L. Hermans, W. Boydens, and L. Helsen. 2023. Evaluation of the oversizing and computational speed of different
open-source borefield sizing methods. BS2023 Conference, Shanghai, China, April
"""
import os
import time

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import sys

sys.path.append("C:\Workdir\Develop\ghetool")

from GHEtool import *


def Swimming_pool_seg():
    number_of_segments = [8, 10, 12]
    results_cst = []
    results_not_cst = []

    for nSeg in number_of_segments:
        # initiate ground, fluid and pipe data
        ground_data = GroundFluxTemperature(k_s=3, T_g=10, volumetric_heat_capacity=2.4 * 10 ** 6, flux=0.06)
        fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
        pipe_data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 1)

        # initiate borefield
        borefield = Borefield()

        # set ground data in borefield
        borefield.ground_data = ground_data
        borefield.fluid_data = fluid_data
        borefield.pipe_data = pipe_data
        borefield.create_rectangular_borefield(15, 20, 6, 6, 100, 4, 0.075)
        # borefield.set_Rb(0.12)

        # set temperature bounds
        borefield.set_max_avg_fluid_temperature(17)
        borefield.set_min_avg_fluid_temperature(3)

        # load the hourly profile
        load = HourlyGeothermalLoad(simulation_period=20)
        load.load_hourly_profile(os.path.join(os.path.dirname(__file__), 'swimming_pool.csv'), header=True,
                                 separator=";", decimal_seperator=".", col_extraction=1, col_injection=0)
        borefield.load = load

        SEER = 20
        SCOP = 4

        # load hourly heating and cooling load and convert it to geothermal loads
        primary_geothermal_load = HourlyGeothermalLoad(simulation_period=load.simulation_period)
        primary_geothermal_load.set_hourly_injection_load(load.hourly_injection_load.copy() * (1 + 1 / SEER))
        primary_geothermal_load.set_hourly_extraction_load(load.hourly_extraction_load.copy() * (1 - 1 / SCOP))
        # set geothermal load
        borefield.load = primary_geothermal_load

        options = {'nSegments': nSeg,
                   'segment_ratios': None,
                   'disp': False,
                   'profiles': True,
                   'method': 'equivalent'
                   }

        borefield.set_options_gfunction_calculation(options)

        # according to L4
        depth_L4 = borefield.size(100, L4_sizing=True)
        results_cst = np.append(results_cst, depth_L4)

    for nSeg in number_of_segments:
        # initiate ground, fluid and pipe data
        ground_data = GroundFluxTemperature(k_s=3, T_g=10, volumetric_heat_capacity=2.4 * 10 ** 6, flux=0.06)
        fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
        pipe_data = MultipleUTube(1, 0.015, 0.02, 0.4, 0.05, 1)

        # initiate borefield
        borefield = Borefield()

        # set ground data in borefield
        borefield.ground_data = ground_data
        borefield.fluid_data = fluid_data
        borefield.pipe_data = pipe_data
        borefield.create_rectangular_borefield(15, 20, 6, 6, 100, 4, 0.075)
        # borefield.set_Rb(0.12)

        # set temperature bounds
        borefield.set_max_avg_fluid_temperature(17)
        borefield.set_min_avg_fluid_temperature(3)

        # load the hourly profile
        load = HourlyGeothermalLoad(simulation_period=20)
        load.load_hourly_profile(os.path.join(os.path.dirname(__file__), 'swimming_pool.csv'), header=True,
                                 separator=";", decimal_seperator=".", col_extraction=1, col_injection=0)
        borefield.load = load

        SEER = 20
        SCOP = 4

        # load hourly heating and cooling load and convert it to geothermal loads
        primary_geothermal_load = HourlyGeothermalLoad(simulation_period=load.simulation_period)
        primary_geothermal_load.set_hourly_injection_load(load.hourly_injection_load.copy() * (1 + 1 / SEER))
        primary_geothermal_load.set_hourly_extraction_load(load.hourly_extraction_load.copy() * (1 - 1 / SCOP))
        # set geothermal load
        borefield.load = primary_geothermal_load

        options = {'nSegments': nSeg,
                   'disp': False,
                   'profiles': True,
                   'method': 'equivalent'
                   }

        borefield.set_options_gfunction_calculation(options)

        # according to L4
        depth_L4 = borefield.size(100, L4_sizing=True)
        results_not_cst = np.append(results_not_cst, depth_L4)

    print(
        f"The sizing according to L4 and using {number_of_segments[0]}segments has a depth of {results_cst[0]}m (using segments of equal length) and {results_not_cst[0]}m (using pygfunction default segments lenghts)")
    print(
        f"The sizing according to L4 and using {number_of_segments[1]}segments has a depth of {results_cst[1]}m (using segments of equal length) and {results_not_cst[1]}m (using pygfunction default segments lenghts)")
    print(
        f"The sizing according to L4 and using {number_of_segments[2]}segments has a depth of {results_cst[2]}m (using segments of equal length) and {results_not_cst[2]}m (using pygfunction default segments lenghts)")


if __name__ == "__main__":  # pragma: no cover
    Swimming_pool_seg()
