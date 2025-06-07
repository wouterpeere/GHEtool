"""
This files contains the code to create graphs for the borehole thermal resistance and pressure drop in a single U
tube at different flow rates and temperatures.
"""
import matplotlib.pyplot as plt
import numpy as np

from GHEtool import *

pipe = SingleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

mpg = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)
meg = TemperatureDependentFluidData('MEG', 23, mass_percentage=False)
thermox = TemperatureDependentFluidData('Thermox DTX', 23, mass_percentage=False)
coolflow = TemperatureDependentFluidData('Coolflow NTP', 25, mass_percentage=False)

flow_rates = np.arange(0.1, 0.8, 0.01)

for temp in (-10, -5, 0, 5, 10):
    list_rb_mpg, list_rb_meg, list_rb_thermox, list_rb_coolflow = [], [], [], []
    list_dp_mpg, list_dp_meg, list_dp_thermox, list_dp_coolflow = [], [], [], []

    for val in flow_rates:
        flow = ConstantFlowRate(vfr=val)

        borehole_mpg = Borehole(mpg, pipe, flow)
        borehole_meg = Borehole(meg, pipe, flow)
        borehole_thermox = Borehole(thermox, pipe, flow)
        borehole_coolflow = Borehole(coolflow, pipe, flow)

        list_rb_mpg.append(borehole_mpg.calculate_Rb(100, 0.7, 0.07, 2, temperature=temp))
        list_rb_meg.append(borehole_meg.calculate_Rb(100, 0.7, 0.07, 2, temperature=temp))
        list_rb_thermox.append(borehole_thermox.calculate_Rb(100, 0.7, 0.07, 2, temperature=temp))
        list_rb_coolflow.append(borehole_coolflow.calculate_Rb(100, 0.7, 0.07, 2, temperature=temp))

        list_dp_mpg.append(pipe.pressure_drop(mpg, flow, 100 - 0.7, temperature=temp))
        list_dp_meg.append(pipe.pressure_drop(meg, flow, 100 - 0.7, temperature=temp))
        list_dp_thermox.append(pipe.pressure_drop(thermox, flow, 100 - 0.7, temperature=temp))
        list_dp_coolflow.append(pipe.pressure_drop(coolflow, flow, 100 - 0.7, temperature=temp))

    plt.figure()
    plt.plot(flow_rates, list_rb_mpg, label="MPG 25 v/v%")
    plt.plot(flow_rates, list_rb_meg, label="MEG 23 v/v%")
    plt.plot(flow_rates, list_rb_thermox, label="Thermox DTX 23 v/v%")
    plt.plot(flow_rates, list_rb_coolflow, label="Coolflow NTP 25 v/v%")

    plt.title(f'Borehole thermal resistance at {temp}°C')
    plt.ylabel('Effective borehole thermal resistance [W/(mK)]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.savefig(f'resistance_{temp}.svg')
    plt.figure()

    plt.plot(flow_rates, list_dp_mpg, label="MPG 25 v/v%")
    plt.plot(flow_rates, list_dp_meg, label="MEG 23 v/v%")
    plt.plot(flow_rates, list_dp_thermox, label="Thermox DTX 23 v/v%")
    plt.plot(flow_rates, list_dp_coolflow, label="Coolflow NTP 25 v/v%")

    plt.title(f'Pressure drop at {temp}°C')
    plt.ylabel('Pressure drop [kPa]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.savefig(f'pressure_{temp}.svg')
