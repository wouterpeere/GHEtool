"""
This file contains an example on how GHEtool can be used to size a borefield
using a combination of active and passive cooling.
This example is based on the work of Coninx and De Nies, 2021.
Coninx, M., De Nies, J. (2022). Cost-efficient Cooling of Buildings by means of Borefields
with Active and Passive Cooling. Master thesis, Department of Mechanical Engineering, KU Leuven, Belgium.
"""

from GHEtool import Borefield, GroundData

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# load data
columnNames = ['HeatingSpace', 'HeatingAHU', 'CoolingSpace', 'CoolingAHU']
df = pd.read_csv("Active_passive_example.csv", names=columnNames, header=0)
heating_data = df.HeatingSpace + df.HeatingAHU
cooling_data = df.CoolingSpace + df.CoolingAHU

# variable COP and EER data
COP = [0.122, 4.365]  # ax+b
EER = [-3.916, 17,901]  # ax+b
threshold_active_cooling = 16

# set simulation period
SIMULATION_PERIOD: int = 50
heating_building: np.ndarray = np.tile(np.array(heating_data), SIMULATION_PERIOD)
cooling_building: np.ndarray = np.tile(np.array(cooling_data), SIMULATION_PERIOD)

def update_load_COP(temp_profile: np.ndarray,
                COP:np.ndarray,
                load_profile: np.ndarray) -> np.ndarray:
    """
    This function updates the load profile for a given COP dependency and a temperature profile.
    """
    COP_array = temp_profile * COP[0] + COP[1]
    return load_profile * (1 - 1/COP_array)


def update_load_EER(temp_profile: np.ndarray,
                    EER: np.ndarray,
                    threshold_active_cooling: int,
                    load_profile: np.ndarray) -> np.ndarray:
    EER_array = temp_profile * EER[0] + EER[1]
    passive: np.ndarray = temp_profile < threshold_active_cooling
    active = np.invert(passive)
    return active * load_profile * (1 + 1/EER_array) + passive * load_profile


borefield = Borefield(SIMULATION_PERIOD)
borefield.example_active_passive = True
borefield.set_max_ground_temperature(17)

borefield.create_rectangular_borefield(12, 12, 6, 6, 100)
borefield.set_ground_parameters(GroundData(2.1, 11, 0.12))

### PASSIVE COOLING
depths = [0.9, 0]

# set initial loads
cooling_ground = cooling_building.copy()
heating_ground = heating_building.copy()

while abs(depths[0] - depths[1]) > 0.1:
    print("iter", depths)
    # set loads
    borefield.set_hourly_cooling_load(cooling_ground)
    borefield.set_hourly_heating_load(heating_ground)

    # size borefield
    depth = borefield.size_L4(100)
    depths.insert(0, depth)

    # get temperature profile
    temp_profile = borefield.results_peak_heating

    # recalculate heating load
    heating_ground = update_load_COP(temp_profile, COP, heating_building)

borefield.print_temperature_profile(plot_hourly=True)


### ACTIVE COOLING
depths = [0.9, 0]

# set initial loads
cooling_ground = cooling_building.copy()
heating_ground = heating_building.copy()

borefield.set_max_ground_temperature(25)
while abs(depths[0] - depths[1]) > 0.1:
    print("iter", depths)
    # set loads
    borefield.set_hourly_cooling_load(cooling_ground)
    borefield.set_hourly_heating_load(heating_ground)

    # size borefield
    depth = borefield.size_L4(100)
    depths.insert(0, depth)

    # get temperature profile
    temp_profile = borefield.results_peak_heating

    # recalculate heating load
    heating_ground = update_load_COP(temp_profile, COP, heating_building)
    cooling_ground = update_load_EER(temp_profile, EER, 16, cooling_building)

borefield.print_temperature_profile(plot_hourly=True)