"""
This files contains the code to create graphs for the borehole thermal resistance and pressure drop in a single DN32
turbocollector for different fluids and flow rates.
"""
import matplotlib.pyplot as plt
import numpy as np

from GHEtool import *

single_turbo_collector = Turbocollector(1.5, 0.013, 0.016, 0.035, 1)
single_smooth = SingleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
double_turbo_collector = Turbocollector(1.5, 0.013, 0.016, 0.035, 2)
double_smooth = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

mpg = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)
meg = TemperatureDependentFluidData('MEG', 25, mass_percentage=False)
water = TemperatureDependentFluidData('Water', 100, mass_percentage=False)

flow_rates = np.arange(0.1, 0.8, 0.01)

for fluid in (mpg, meg, water):
    list_rb_single_turbo, list_rb_single_smooth, list_rb_double_turbo, list_rb_double_smooth = [], [], [], []
    list_dp_single_turbo, list_dp_single_smooth, list_dp_double_turbo, list_dp_double_smooth = [], [], [], []

    for val in flow_rates:
        flow = ConstantFlowRate(vfr=val)

        borehole_single_turbo = Borehole(fluid, single_turbo_collector, flow)
        borehole_single_smooth = Borehole(fluid, single_smooth, flow)
        borehole_double_turbo = Borehole(fluid, double_turbo_collector, flow)
        borehole_double_smooth = Borehole(fluid, double_smooth, flow)

        list_rb_single_turbo.append(borehole_single_turbo.calculate_Rb(100, 0.7, 0.07, 2, temperature=5))
        list_rb_single_smooth.append(borehole_single_smooth.calculate_Rb(100, 0.7, 0.07, 2, temperature=5))
        list_rb_double_turbo.append(borehole_double_turbo.calculate_Rb(100, 0.7, 0.07, 2, temperature=5))
        list_rb_double_smooth.append(borehole_double_smooth.calculate_Rb(100, 0.7, 0.07, 2, temperature=5))

        list_dp_single_turbo.append(single_turbo_collector.pressure_drop(fluid, flow, 100 - 0.7, temperature=5))
        list_dp_single_smooth.append(single_smooth.pressure_drop(fluid, flow, 100 - 0.7, temperature=5))
        list_dp_double_turbo.append(double_turbo_collector.pressure_drop(fluid, flow, 100 - 0.7, temperature=5))
        list_dp_double_smooth.append(double_smooth.pressure_drop(fluid, flow, 100 - 0.7, temperature=5))

    plt.figure()
    plt.plot(flow_rates, list_rb_single_turbo, label="Single turbo")
    plt.plot(flow_rates, list_rb_single_smooth, label="Single smooth")
    plt.plot(flow_rates, list_rb_double_turbo, label="Double turbo")
    plt.plot(flow_rates, list_rb_double_smooth, label="Double smooth")

    plt.title(f'Borehole thermal resistance for {fluid._name}')
    plt.ylabel('Effective borehole thermal resistance [W/(mK)]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.savefig(f'resistance_{fluid._name}.svg')
    plt.figure()

    plt.plot(flow_rates, list_dp_single_turbo, label="Single turbo")
    plt.plot(flow_rates, list_dp_single_smooth, label="Single smooth")
    plt.plot(flow_rates, list_dp_double_turbo, label="Double turbo")
    plt.plot(flow_rates, list_dp_double_smooth, label="Double smooth")

    plt.title(f'Pressure drop for {fluid._name}')
    plt.ylabel('Pressure drop [kPa]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.show()
    plt.savefig(f'pressure_{fluid._name}.svg')
