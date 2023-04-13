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
heating_building = df.HeatingSpace + df.HeatingAHU
cooling_building = df.CoolingSpace + df.CoolingAHU

# variable COP and EER data
COP = [0.122, 4.365]  # ax+b
EER = [-3.916, 17,901]  # ax+b


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
                    load_profile: np.ndarray) -> np.ndarray:
    EER_array = temp_profile * EER[0] + EER[1]
    return load_profile * (1 + 1/EER_array)

