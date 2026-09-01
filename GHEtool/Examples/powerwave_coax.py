"""
This files contains the code to create graphs for the borehole thermal resistance and pressure drop for the
JANSEN powerwave coax. The models for the pressure drop and the effective borehole thermal resistance are described in
Peere et al. (2026) [#PeereEtAl_].

References
----------
.. [#PeereEtAl] Peere, W., Hidman, N., Hofstetter, R. (2026) Development of a thermohydraulic model for the JANSEN powerwave with direct numerical simulation and its impact on the thermal borehole resistance. In Proceedings of Der Geothermiekongress. Postdam (Germany), 20-22 October 2026.

"""
import matplotlib.pyplot as plt
import numpy as np

from GHEtool import *
from GHEtool.VariableClasses.PipeData.PowerwaveCoax import PowerwaveCoax


def create_graphs():
    mpg = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)

    flow_rates = np.arange(0.1, 0.8, 0.01)

    # important parameters
    k_g = 2
    depth = 50
    for rb in (90e-3, 120e-3, 150e-3):
        list_rb_double, list_rb_powerwave, list_rb_coax, list_rb_single = [], [], [], []
        list_dp_double, list_dp_powerwave, list_dp_coax, list_dp_single = [], [], [], []

        double = MultipleUTube(k_g, 0.013, 0.016, 0.4, (rb / 2) / 2, 2)
        single = MultipleUTube(k_g, 0.013, 0.016, 0.4, (rb / 2) / 2, 1)
        coax = CoaxialPipe(0.013, 0.016, 0.0266, 0.03, 0.4, k_g)
        powerwave_coax = PowerwaveCoax(k_g)

        for val in flow_rates:
            flow = ConstantFlowRate(vfr=val)

            borehole_double = Borehole(mpg, double, flow)
            borehole_single = Borehole(mpg, single, flow)
            borehole_powerwave = Borehole(mpg, powerwave_coax, flow)
            borehole_coax = Borehole(mpg, coax, flow)

            list_rb_double.append(
                borehole_double.calculate_Rb(depth, 0.7, rb / 2, 2, temperature=5,
                                             use_explicit_models=True))
            list_rb_single.append(
                borehole_single.calculate_Rb(depth, 0.7, rb / 2, 2, temperature=5,
                                             use_explicit_models=True))
            list_rb_powerwave.append(
                borehole_powerwave.calculate_Rb(depth, 0.7, rb / 2, 2, temperature=5, use_explicit_models=True))

            list_rb_coax.append(
                borehole_coax.calculate_Rb(depth, 0.7, rb / 2, 2, temperature=5, use_explicit_models=True))

            list_dp_double.append(double.pressure_drop(mpg, flow, depth - 0.7, temperature=5))
            list_dp_powerwave.append(powerwave_coax.pressure_drop(mpg, flow, depth - 0.7, temperature=5))
            list_dp_coax.append(coax.pressure_drop(mpg, flow, depth - 0.7, temperature=5))
            list_dp_single.append(single.pressure_drop(mpg, flow, depth - 0.7, temperature=5))

        plt.figure()
        plt.plot(flow_rates, list_rb_double, label="Double DN32")
        plt.plot(flow_rates, list_rb_single, label="Single DN32")
        plt.plot(flow_rates, list_rb_coax, label="Coax")
        plt.plot(flow_rates, list_rb_powerwave, label="Powerwave coax")

        plt.title(f'Borehole thermal resistance (d={rb * 1000:.0f}mm, MPG 25v/v%)')
        plt.ylabel('Effective borehole thermal resistance [mK/W]')
        plt.xlabel('Flow rate [l/s]')
        plt.legend()
        plt.figure()

        plt.plot(flow_rates, list_dp_double, label="Double DN32")
        plt.plot(flow_rates, list_dp_single, label="Single DN32")
        plt.plot(flow_rates, list_dp_coax, label="Coax")
        plt.plot(flow_rates, list_dp_powerwave, label="Powerwave coax")

        plt.title(f'Pressure drop (MPG 25v/v%)')
        plt.ylabel('Pressure drop [kPa]')
        plt.xlabel('Flow rate [l/s]')
        plt.legend()
        plt.show()


def realistic_case():
    meg = TemperatureDependentFluidData('MEG', 25, mass_percentage=False)

    flow_rates = np.arange(0.1, 0.8, 0.01)

    list_rb_smooth, list_rb_muoviellipse = [], []
    list_dp_smooth, list_dp_muoviellipse = [], []

    smooth_pipe = MultipleUTube(1.5, 0.045 / 2 - 4.1e-3, 0.045 / 2, 0.4, (110e-3 / 2) / 2, 1)
    muoviellipse = MuoviEllipse(1.5, 51e-3, 37e-3, 4.1e-3, (90e-3 / 2) / 2)

    for val in flow_rates:
        flow = ConstantFlowRate(vfr=val)

        borehole_smooth = Borehole(meg, smooth_pipe, flow)
        borehole_muoviellipse = Borehole(meg, muoviellipse, flow)

        list_rb_smooth.append(
            borehole_smooth.calculate_Rb(100, 0.7, (110e-3) / 2, 2, temperature=5,
                                         use_explicit_models=True))
        list_rb_muoviellipse.append(
            borehole_muoviellipse.calculate_Rb(100, 0.7, 90e-3 / 2, 2, temperature=5, use_explicit_models=True))

        list_dp_smooth.append(smooth_pipe.pressure_drop(meg, flow, 100 - 0.7, temperature=5))
        list_dp_muoviellipse.append(muoviellipse.pressure_drop(meg, flow, 100 - 0.7, temperature=5))

    plt.figure()
    plt.plot(flow_rates, list_rb_smooth, label="Smooth DN45 (d=110mm)")
    plt.plot(flow_rates, list_rb_muoviellipse, label="MuoviELLIPSE DN45 (d=90mm)")

    plt.title(f'Borehole thermal resistance (MEG 25v/v%)')
    plt.ylabel('Effective borehole thermal resistance [mK/W]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.figure()

    plt.plot(flow_rates, list_dp_smooth, label="Smooth DN45 (d=110mm)")
    plt.plot(flow_rates, list_dp_muoviellipse, label="MuoviELLIPSE DN45 (d=90mm)")

    plt.title(f'Pressure drop')
    plt.ylabel('Pressure drop [kPa]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.show()


def realistic_case2():
    mpg = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)

    flow_rates = np.arange(0.1, 0.8, 0.01)

    list_rb_smooth, list_rb_muoviellipse = [], []
    list_dp_smooth, list_dp_muoviellipse = [], []

    smooth = MultipleUTube(1.5, 0.045 / 2 - 4.1e-3, 0.045 / 2, 0.4, (110e-3 / 2) / 2, 1)
    muoviellipse = MuoviEllipse(1.5, 58e-3, 41e-3, 4.6e-3, (110e-3 / 2) / 2)

    for val in flow_rates:
        flow = ConstantFlowRate(vfr=val)

        borehole_turbo_collector = Borehole(mpg, smooth, flow)
        borehole_muoviellipse = Borehole(mpg, muoviellipse, flow)

        list_rb_smooth.append(
            borehole_turbo_collector.calculate_Rb(100, 0.7, (110e-3) / 2, 2, temperature=5,
                                                  use_explicit_models=True))
        list_rb_muoviellipse.append(
            borehole_muoviellipse.calculate_Rb(100, 0.7, 110e-3 / 2, 2, temperature=5, use_explicit_models=True))

        list_dp_smooth.append(smooth.pressure_drop(mpg, flow, 100 - 0.7, temperature=5))
        list_dp_muoviellipse.append(muoviellipse.pressure_drop(mpg, flow, 100 - 0.7, temperature=5))

    plt.figure()
    plt.plot(flow_rates, list_rb_smooth, label="Smooth DN45 (d=110mm)")
    plt.plot(flow_rates, list_rb_muoviellipse, label="MuoviELLIPSE DN50 (d=110mm)")

    plt.title(f'Borehole thermal resistance')
    plt.ylabel('Effective borehole thermal resistance [mK/W]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.figure()

    plt.plot(flow_rates, list_dp_smooth, label="Smooth DN45 (d=110mm)")
    plt.plot(flow_rates, list_dp_muoviellipse, label="MuoviELLIPSE DN50 (d=110mm)")

    plt.title(f'Pressure drop')
    plt.ylabel('Pressure drop [kPa]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.show()


if __name__ == "__main__":  # pragma: no-cover
    create_graphs()
    realistic_case()
    realistic_case2()
