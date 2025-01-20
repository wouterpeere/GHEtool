"""
This example shows how you can design a borefield with tilted boreholes.
"""
import math

from GHEtool import *

import matplotlib.pyplot as plt
import numpy as np
import pygfunction as gt


def tilted():
    # define params
    ground_data = GroundFluxTemperature(1.9, 10)
    pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    fluid_data = FluidData(mfr=0.2)
    fluid_data.import_fluid_from_pygfunction(gt.media.Fluid('MPG', 30, 2))
    load_data = MonthlyBuildingLoadAbsolute(
        np.array([.176, .174, .141, .1, .045, 0, 0, 0, 0.012, 0.065, 0.123, 0.164]) * 8 * 1350,
        np.array([0, 0, 0, 0, .112, .205, .27, .264, .149, 0, 0, 0]) * 4 * 700,
        np.array([1, .991, .802, .566, .264, 0, 0, 0, .0606, .368, .698, .934]) * 8,
        np.array([0, 0, 0, 0, .415, .756, 1, .976, .549, 0, 0, 0]) * 4
    )

    # define borefield
    borefield_tilted = [gt.boreholes.Borehole(150, 0.75, 0.07, -3, 0, math.pi / 7, orientation=math.pi),
                        gt.boreholes.Borehole(150, 0.75, 0.07, 3, 0, math.pi / 7, orientation=0)]
    borefield_without_tilt = [gt.boreholes.Borehole(150, 0.75, 0.07, -3, 0),
                              gt.boreholes.Borehole(150, 0.75, 0.07, 3, 0)]

    # initiate GHEtool object with tilted borefield
    borefield = Borefield(borefield=borefield_tilted, load=load_data)
    borefield.set_ground_parameters(ground_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.set_fluid_parameters(fluid_data)

    borefield.print_temperature_profile()

    # initiate GHEtool object without tilted borefield
    borefield = Borefield(borefield=borefield_without_tilt, load=load_data)
    borefield.set_ground_parameters(ground_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.set_fluid_parameters(fluid_data)

    borefield.print_temperature_profile()


if __name__ == "__main__":
    tilted()
