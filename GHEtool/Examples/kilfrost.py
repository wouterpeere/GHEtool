"""
This file contains the code for the effective borehole thermal resistance graph and pressure drop graph for the
Kilfrost GEO and Kilfrost GEO Plus products.
"""

from GHEtool import *

import matplotlib.pyplot as plt
import numpy as np

single = SingleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
double = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

meg = TemperatureDependentFluidData('MEG', 26, mass_percentage=False).create_constant(0)
mpg = TemperatureDependentFluidData('MPG', 30, mass_percentage=False).create_constant(0)
kilfrostgeo = TemperatureDependentFluidData('Kilfrost GEO', 30, mass_percentage=False).create_constant(0)
kilfrostgeoplus = TemperatureDependentFluidData('Kilfrost GEO', 33, mass_percentage=False).create_constant(0)

flow_range = np.arange(0.1, 1.5, 0.01)

for jdx, pipe in enumerate((single, double)):
    dp_meg = np.zeros(len(flow_range))
    dp_mpg = np.zeros(len(flow_range))
    dp_kilfrost = np.zeros(len(flow_range))
    dp_kilfrostplus = np.zeros(len(flow_range))
    rb_meg = np.zeros(len(flow_range))
    rb_mpg = np.zeros(len(flow_range))
    rb_kilfrost = np.zeros(len(flow_range))
    rb_kilfrostplus = np.zeros(len(flow_range))

    for idx, flow in enumerate(flow_range):
        borehole_meg = Borehole(meg, pipe, ConstantFlowRate(vfr=flow))
        borehole_mpg = Borehole(mpg, pipe, ConstantFlowRate(vfr=flow))
        borehole_kilfrost = Borehole(kilfrostgeo, pipe, ConstantFlowRate(vfr=flow))
        borehole_kilfrostplus = Borehole(kilfrostgeoplus, pipe, ConstantFlowRate(vfr=flow))

        dp_meg[idx] = borehole_meg.pipe_data.pressure_drop(borehole_meg.fluid_data, borehole_meg.flow_data, 150)
        dp_mpg[idx] = borehole_mpg.pipe_data.pressure_drop(borehole_mpg.fluid_data, borehole_mpg.flow_data, 150)
        dp_kilfrost[idx] = borehole_kilfrost.pipe_data.pressure_drop(borehole_kilfrost.fluid_data,
                                                                     borehole_kilfrost.flow_data, 150)
        dp_kilfrostplus[idx] = borehole_kilfrostplus.pipe_data.pressure_drop(borehole_kilfrostplus.fluid_data,
                                                                             borehole_kilfrostplus.flow_data, 150)

        rb_meg[idx] = borehole_meg.calculate_Rb(150, 1, 0.075, 2)
        rb_mpg[idx] = borehole_mpg.calculate_Rb(150, 1, 0.075, 2)
        rb_kilfrost[idx] = borehole_kilfrost.calculate_Rb(150, 1, 0.075, 2)
        rb_kilfrostplus[idx] = borehole_kilfrostplus.calculate_Rb(150, 1, 0.075, 2)

    plt.figure()
    plt.plot(flow_range, dp_meg, label="MEG 26 v/v%")
    plt.plot(flow_range, dp_mpg, label="MPG 30 v/v%")
    plt.plot(flow_range, dp_kilfrost, label="Kilfrost GEO 30 v/v%")
    plt.plot(flow_range, dp_kilfrostplus, label="Kilfrost GEO Plus 33 v/v%")

    plt.title(f'Pressure drop for a borehole of 150m deep with a {("single", "double")[jdx]} DN32')
    plt.ylabel('Pressure drop [kPa]')
    plt.xlabel('Volume flow [l/s]')
    plt.legend()
    plt.figure()

    plt.plot(flow_range, rb_meg, label="MEG 26 v/v%")
    plt.plot(flow_range, rb_mpg, label="MPG 30 v/v%")
    plt.plot(flow_range, rb_kilfrost, label="Kilfrost GEO 30 v/v%")
    plt.plot(flow_range, rb_kilfrostplus, label="Kilfrost GEO Plus 33 v/v%")

    plt.title(f'Borehole thermal resistance for a borehole of 150m deep with a {("single", "double")[jdx]} DN32')
    plt.ylabel('Effective borehole thermal resistance [mK/W]')
    plt.xlabel('Volume flow [l/s]')
    plt.legend()
    plt.show()
