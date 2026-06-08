"""
This files contains the code to create graphs for the borehole thermal resistance and pressure drop for a
MuoviELLIPSE DN45 from Muovitech for different borehole diameters. The results are compared with the TurboCollector DN45.

The correlations for both the convective heat transfer coefficient and the friction factor, which are used internally
to calculate respectively the effective borehole thermal resistance and the pressure drop, were created by Niklas Hidman,
Division of Fluid Dynamics, Department of Mechanical and Maritime Sciences, Chalmers University of Technology, Gothenburg, Sweden.
"""
import matplotlib.pyplot as plt
import numpy as np

from GHEtool import *


def create_graphs():
    mpg = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)

    flow_rates = np.arange(0.1, 0.8, 0.01)

    for rb in (90e-3, 120e-3, 150e-3):
        list_rb_turbo_collector, list_rb_muoviellipse = [], []
        list_dp_turbo_collector, list_dp_muoviellipse = [], []

        turbo_collector = Turbocollector(1.5, 0.045 / 2 - 4.1e-3, 0.045 / 2, (rb / 2) / 2, 1)
        muoviellipse = MuoviEllipse(1.5, 51e-3, 37e-3, 4.1e-3, (rb / 2) / 2)

        for val in flow_rates:
            flow = ConstantFlowRate(vfr=val)

            borehole_turbo_collector = Borehole(mpg, turbo_collector, flow)
            borehole_muoviellipse = Borehole(mpg, muoviellipse, flow)

            list_rb_turbo_collector.append(
                borehole_turbo_collector.calculate_Rb(100, 0.7, rb / 2, 2, temperature=5,
                                                      use_explicit_models=True))
            list_rb_muoviellipse.append(
                borehole_muoviellipse.calculate_Rb(100, 0.7, rb / 2, 2, temperature=5, use_explicit_models=True))

            list_dp_turbo_collector.append(turbo_collector.pressure_drop(mpg, flow, 100 - 0.7, temperature=5))
            list_dp_muoviellipse.append(muoviellipse.pressure_drop(mpg, flow, 100 - 0.7, temperature=5))

        plt.figure()
        plt.plot(flow_rates, list_rb_turbo_collector, label="TurboCollector")
        plt.plot(flow_rates, list_rb_muoviellipse, label="MuoviELLIPSE")

        plt.title(f'Borehole thermal resistance for a borehole diameter of {rb * 1000} mm')
        plt.ylabel('Effective borehole thermal resistance [mK/W]')
        plt.xlabel('Flow rate [l/s]')
        plt.legend()
        plt.figure()

        plt.plot(flow_rates, list_dp_turbo_collector, label="TurboCollector")
        plt.plot(flow_rates, list_dp_muoviellipse, label="MuoviELLIPSE")

        plt.title(f'Pressure drop for a borehole diameter of {rb * 1000} mm')
        plt.ylabel('Pressure drop [kPa]')
        plt.xlabel('Flow rate [l/s]')
        plt.legend()
        plt.show()


def realistic_case():

    mpg = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)

    flow_rates = np.arange(0.1, 0.8, 0.01)

    list_rb_turbo_collector, list_rb_muoviellipse = [], []
    list_dp_turbo_collector, list_dp_muoviellipse = [], []

    turbo_collector = Turbocollector(1.5, 0.045 / 2 - 4.1e-3, 0.045 / 2, (110e-3 / 2) / 2, 1)
    muoviellipse = MuoviEllipse(1.5, 51e-3, 37e-3, 4.1e-3, (90e-3 / 2) / 2)

    for val in flow_rates:
        flow = ConstantFlowRate(vfr=val)

        borehole_turbo_collector = Borehole(mpg, turbo_collector, flow)
        borehole_muoviellipse = Borehole(mpg, muoviellipse, flow)

        list_rb_turbo_collector.append(
            borehole_turbo_collector.calculate_Rb(100, 0.7, (110e-3) / 2, 2, temperature=5,
                                                  use_explicit_models=True))
        list_rb_muoviellipse.append(
            borehole_muoviellipse.calculate_Rb(100, 0.7, rb / 2, 2, temperature=5, use_explicit_models=True))

        list_dp_turbo_collector.append(turbo_collector.pressure_drop(mpg, flow, 100 - 0.7, temperature=5))
        list_dp_muoviellipse.append(muoviellipse.pressure_drop(mpg, flow, 100 - 0.7, temperature=5))

    plt.figure()
    plt.plot(flow_rates, list_rb_turbo_collector, label="TurboCollector (rb=110mm)")
    plt.plot(flow_rates, list_rb_muoviellipse, label="MuoviELLIPSE (rb=90mm)")

    plt.title(f'Borehole thermal resistance')
    plt.ylabel('Effective borehole thermal resistance [mK/W]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.figure()

    plt.plot(flow_rates, list_dp_turbo_collector, label="TurboCollector (rb=110mm)")
    plt.plot(flow_rates, list_dp_muoviellipse, label="MuoviELLIPSE (rb=90mm)")

    plt.title(f'Pressure drop')
    plt.ylabel('Pressure drop [kPa]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.show()


if __name__ == "__main__":  # pragma: no-cover
    # create_graphs()
    realistic_case()
