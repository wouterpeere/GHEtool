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


def create_graphs_fluid():
    reg_40 = SingleUTube(1.5, 0.02 - 3.7e-3, 0.02, 0.4, (114e-3) / 4)
    reg_45 = SingleUTube(1.5, 0.0225 - 4.1e-3, 0.0225, 0.4, (114e-3) / 4)
    reg_50 = SingleUTube(1.5, 0.025 - 4.6e-3, 0.025, 0.4, (114e-3) / 4)  # was 41e-3
    ellipse_40 = MuoviEllipse(1.5, 46e-3, 33e-3, 3.7e-3, (89e-3) / 4)
    ellipse_45 = MuoviEllipse(1.5, 51e-3, 37e-3, 4.1e-3, (89e-3) / 4)
    ellipse_50 = MuoviEllipse(1.5, 58e-3, 41e-3, 4.6e-3, (89e-3) / 4)

    mpg = TemperatureDependentFluidData('MPG', 50, mass_percentage=False)
    meg = TemperatureDependentFluidData('MEG', 25, mass_percentage=False)
    mea = TemperatureDependentFluidData('MEA', 28, mass_percentage=False)

    flow_rates = np.arange(0.01, 28, 0.01)

    rb_89 = 89e-3 / 2
    rb_114 = 114e-3 / 2

    probes = {
        ('ellipse', 40): (ellipse_40, rb_89),
        ('ellipse', 45): (ellipse_45, rb_89),
        ('ellipse', 50): (ellipse_50, rb_89),
        ('singleu', 40): (reg_40, rb_114),
        ('singleu', 45): (reg_45, rb_114),
        ('singleu', 50): (reg_50, rb_114),
    }

    colors = {40: 'tab:blue', 45: 'tab:orange', 50: 'tab:green'}
    fluid_pct = {'MPG': 25, 'MEG': 25, 'MEA': 28}

    for fluid in (mpg, meg, mea):
        results = {key: {'rb': [], 'dp': []} for key in probes}

        for val in flow_rates:
            flow = ConstantFlowRate(vfr=val)

            for key, (probe, rb) in probes.items():
                borehole = Borehole(fluid, probe, flow)
                results[key]['rb'].append(
                    borehole.calculate_Rb(100, 0.7, rb, 2, temperature=5, use_explicit_models=True))
                results[key]['dp'].append(
                    probe.pressure_drop(fluid, flow, 100 - 0.7, temperature=5))

        pct = fluid_pct[fluid._name]
        fig, ax1 = plt.subplots(1, 1)

        for dn in [40, 45, 50]:
            color = colors[dn]
            ax1.plot(flow_rates, results[('ellipse', dn)]['rb'],
                     color=color, linestyle='-', label=f'MuoviELLIPSE DN{dn} (Ø89mm)')
            ax1.plot(flow_rates, results[('singleu', dn)]['rb'],
                     color=color, linestyle='--', label=f'SingleU DN{dn} (Ø114mm)')

            # ax2.plot(flow_rates, results[('ellipse', dn)]['dp'],
            #          color=color, linestyle='-', label=f'MuoviELLIPSE DN{dn} (Ø89mm)')
            # ax2.plot(flow_rates, results[('singleu', dn)]['dp'],
            #          color=color, linestyle='--', label=f'SingleU DN{dn} (Ø114mm)')

        ax1.set_title(f'Borehole thermal resistance ({fluid._name} {pct} v/v%)')
        ax1.set_ylabel('Effective borehole thermal resistance [mK/W]')
        ax1.set_xlabel('Flow rate [l/s]')
        ax1.legend()

        # ax2.set_title('Pressure drop')
        # ax2.set_ylabel('Pressure drop [kPa]')
        # ax2.set_xlabel('Flow rate [l/s]')
        # ax2.legend()

        plt.tight_layout()
        plt.show()


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
            borehole_muoviellipse.calculate_Rb(100, 0.7, 90e-3 / 2, 2, temperature=5, use_explicit_models=True))

        list_dp_turbo_collector.append(turbo_collector.pressure_drop(mpg, flow, 100 - 0.7, temperature=5))
        list_dp_muoviellipse.append(muoviellipse.pressure_drop(mpg, flow, 100 - 0.7, temperature=5))

    plt.figure()
    plt.plot(flow_rates, list_rb_turbo_collector, label="TurboCollector DN45 (rb=110mm)")
    plt.plot(flow_rates, list_rb_muoviellipse, label="MuoviELLIPSE DN45 (rb=90mm)")

    plt.title(f'Borehole thermal resistance')
    plt.ylabel('Effective borehole thermal resistance [mK/W]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.figure()

    plt.plot(flow_rates, list_dp_turbo_collector, label="TurboCollector DN45 (rb=110mm)")
    plt.plot(flow_rates, list_dp_muoviellipse, label="MuoviELLIPSE DN45 (rb=90mm)")

    plt.title(f'Pressure drop')
    plt.ylabel('Pressure drop [kPa]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.show()


def realistic_case2():
    mpg = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)

    flow_rates = np.arange(0.1, 0.8, 0.01)

    list_rb_turbo_collector, list_rb_muoviellipse = [], []
    list_dp_turbo_collector, list_dp_muoviellipse = [], []

    turbo_collector = Turbocollector(1.5, 0.045 / 2 - 4.1e-3, 0.045 / 2, (110e-3 / 2) / 2, 1)
    muoviellipse = MuoviEllipse(1.5, 58e-3, 41e-3, 4.6e-3, (110e-3 / 2) / 2)

    for val in flow_rates:
        flow = ConstantFlowRate(vfr=val)

        borehole_turbo_collector = Borehole(mpg, turbo_collector, flow)
        borehole_muoviellipse = Borehole(mpg, muoviellipse, flow)

        list_rb_turbo_collector.append(
            borehole_turbo_collector.calculate_Rb(100, 0.7, (110e-3) / 2, 2, temperature=5,
                                                  use_explicit_models=True))
        list_rb_muoviellipse.append(
            borehole_muoviellipse.calculate_Rb(100, 0.7, 110e-3 / 2, 2, temperature=5, use_explicit_models=True))

        list_dp_turbo_collector.append(turbo_collector.pressure_drop(mpg, flow, 100 - 0.7, temperature=5))
        list_dp_muoviellipse.append(muoviellipse.pressure_drop(mpg, flow, 100 - 0.7, temperature=5))

    plt.figure()
    plt.plot(flow_rates, list_rb_turbo_collector, label="TurboCollector DN45 (rb=110mm)")
    plt.plot(flow_rates, list_rb_muoviellipse, label="MuoviELLIPSE DN50(rb=110mm)")

    plt.title(f'Borehole thermal resistance')
    plt.ylabel('Effective borehole thermal resistance [mK/W]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.figure()

    plt.plot(flow_rates, list_dp_turbo_collector, label="TurboCollector DN45(rb=110mm)")
    plt.plot(flow_rates, list_dp_muoviellipse, label="MuoviELLIPSE DN50 (rb=110mm)")

    plt.title(f'Pressure drop')
    plt.ylabel('Pressure drop [kPa]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.show()


if __name__ == "__main__":  # pragma: no-cover
    create_graphs_fluid()
    create_graphs()
    realistic_case()
    realistic_case2()
