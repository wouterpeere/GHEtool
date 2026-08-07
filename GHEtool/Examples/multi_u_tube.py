"""
This files contains the code to create graphs for the borehole thermal resistance and pressure drop for a
Multi-U-Tube probe from BLZ Geotechnik GmbH for different cases.

"""
import matplotlib.pyplot as plt
import numpy as np

from GHEtool import *


def resistances():
    """
    This function creates a graph with the local, internal and effective borehole thermal resistance for different flow rates.
    """
    meg = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)

    borehole_radius = 0.075

    flow_rates = np.arange(0.1, 1.5, 0.01)

    list_conv_cen, list_conv_sat = [], []
    list_ra, list_rb, list_rb_star = [], [], []

    multi_u_tube = MultiUTube(1.2, 0.05, False)

    for val in flow_rates:
        flow = ConstantFlowRate(vfr=val)

        borehole_multi_u = Borehole(meg, multi_u_tube, flow)

        cen, sat = multi_u_tube.calculate_convective_resistance(flow, meg, temperature=5)
        list_conv_cen.append(cen)
        list_conv_sat.append(sat)
        cen_conv, sat_conv = multi_u_tube.calculate_conductive_resistance()
        ra, rb = multi_u_tube.predict_Rb_Ra_series(borehole_radius, 0.05, cen + cen_conv, sat + sat_conv, 2, 2)
        list_ra.append(rb)
        list_rb.append(ra)
        list_rb_star.append(
            borehole_multi_u.calculate_Rb(100, 0.7, borehole_radius, 2, use_explicit_models=True, temperature=5))

    plt.figure()
    plt.plot(flow_rates, list_conv_cen, label="Inner")
    plt.plot(flow_rates, list_conv_sat, label="Satellite")
    plt.title(f'Convective resistance (d={borehole_radius * 2 * 1000:.0f}mm, MEG 25v/v%)')
    plt.ylabel('Convective resistance [mK/W]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()

    plt.figure()
    plt.plot(flow_rates, list_ra, label="Internal resistance")
    plt.plot(flow_rates, list_rb, label="Local resistance")
    plt.plot(flow_rates, list_rb_star, label="Effective borehole resistance")
    plt.title(f'Borehole resistances (d={borehole_radius * 2 * 1000:.0f}mm, MEG 25v/v%)')
    plt.ylabel('Resistances [mK/W]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()

    plt.show()


def resistances_2():
    """
    Create graphs comparing the local and internal borehole thermal resistances of a multi U tube and a double U tube for different flow rates.
    """
    fluid = TemperatureDependentFluidData('MEG', 25, mass_percentage=False)

    borehole_radius = 0.075
    grout_conductivity = 2
    ground_conductivity = 2
    temperature = 5

    flow_rates = np.arange(0.1, 1.5, 0.01)

    list_ra_multi_u, list_rb_multi_u = [], []
    list_ra_double_u, list_rb_double_u = [], []

    multi_u_tube = MultiUTube(grout_conductivity, 0.05, False)
    double_u_tube = DoubleUTube(2, 0.013, 0.016, 0.4, 0.03)

    cen_cond, sat_cond = multi_u_tube.calculate_conductive_resistance()

    for val in flow_rates:
        flow = ConstantFlowRate(vfr=val)

        borehole_double_u = Borehole(fluid, double_u_tube, flow)

        cen_conv, sat_conv = multi_u_tube.calculate_convective_resistance(flow, fluid, temperature=temperature)

        ra_multi_u, rb_multi_u = multi_u_tube.predict_Rb_Ra_series(borehole_radius, 0.05, cen_conv + cen_cond,
                                                                   sat_conv + sat_cond, grout_conductivity,
                                                                   ground_conductivity)
        list_ra_multi_u.append(ra_multi_u)
        list_rb_multi_u.append(rb_multi_u)

        borehole_double_u.calculate_Rb(100, 0.7, borehole_radius, ground_conductivity, use_explicit_models=True,
                                       temperature=temperature)
        list_ra_double_u.append(double_u_tube._R_a)
        list_rb_double_u.append(double_u_tube._R_b)

    plt.figure()
    plt.plot(flow_rates, list_rb_multi_u, label="Multi U tube Rb")
    plt.plot(flow_rates, list_rb_double_u, label="Double U tube Rb")
    plt.plot(flow_rates, list_ra_multi_u, label="Multi U tube Ra")
    plt.plot(flow_rates, list_ra_double_u, label="Double U tube Ra")
    plt.title(f'Borehole resistances, (d={borehole_radius * 2 * 1000:.0f}mm, MEG 25v/v%)')
    plt.ylabel('Thermal resistance [mK/W]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()

    plt.show()


def create_graphs():
    """
    This function creates the borehole resistance graph in function of the flow rate.
    """
    meg = TemperatureDependentFluidData('MEG', 25, mass_percentage=False)

    rb = 0.075

    flow_rates = np.arange(0.1, 0.8, 0.01)

    list_rb_double, list_rb_multi_u = [], []
    list_dp_double, list_dp_multi_u = [], []

    double = DoubleUTube(2, 0.013, 0.016, 0.4, rb / 2, )
    multi_u_tube = MultiUTube(2, 0.06, False)

    for val in flow_rates:
        flow = ConstantFlowRate(vfr=val)

        borehole_double_u = Borehole(meg, double, flow)
        borehole_multi_u = Borehole(meg, multi_u_tube, flow)

        list_rb_double.append(
            borehole_double_u.calculate_Rb(100, 0.7, rb, 2, temperature=5,
                                           use_explicit_models=True))
        list_rb_multi_u.append(
            borehole_multi_u.calculate_Rb(100, 0.7, rb, 2, temperature=5, use_explicit_models=True))

        list_dp_double.append(double.pressure_drop(meg, flow, 100 - 0.7, temperature=5))
        list_dp_multi_u.append(multi_u_tube.pressure_drop(meg, flow, 100 - 0.7, temperature=5))

    multi_u_tube.draw_borehole_internal(rb)
    plt.figure()
    plt.plot(flow_rates, list_rb_double, label="Double DN32")
    plt.plot(flow_rates, list_rb_multi_u, label="Multi-U-Tube")

    plt.title(f'Borehole thermal resistance (d={rb * 1000:.0f}mm, MEG 25v/v%)')
    plt.ylabel('Effective borehole thermal resistance [mK/W]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.figure()

    plt.plot(flow_rates, list_dp_double, label="Double DN32")
    plt.plot(flow_rates, list_dp_multi_u, label="Multi-U-Tube")

    plt.title(f'Pressure drop (MEG 25v/v%)')
    plt.ylabel('Pressure drop [kPa]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.show()


def create_graphs_2():
    meg = TemperatureDependentFluidData('MEG', 25, mass_percentage=False)

    for borehole_depth in (75, 100, 125, 150):
        borehole_radius = 0.075
        buried_depth = 0.7
        ground_conductivity = 2
        temperature = 5

        flow_rates = np.arange(0.1, 0.8, 0.01)
        satellite_positions = [0.04, 0.05, 0.06]

        fig_rb, ax_rb = plt.subplots()
        fig_dp, ax_dp = plt.subplots()

        for satellite_position in satellite_positions:
            double_u = DoubleUTube(2, 0.013, 0.016, 0.4, borehole_radius / 2)
            multi_u_tube = MultiUTube(2, satellite_position, False)

            list_rb_double = []
            list_rb_multi_u = []
            list_dp_double = []
            list_dp_multi_u = []

            for flow_rate in flow_rates:
                flow = ConstantFlowRate(vfr=flow_rate)

                borehole_double_u = Borehole(meg, double_u, flow)
                borehole_multi_u = Borehole(meg, multi_u_tube, flow)

                list_rb_double.append(
                    borehole_double_u.calculate_Rb(borehole_depth, buried_depth, borehole_radius, ground_conductivity,
                                                   temperature=temperature, use_explicit_models=True))
                list_rb_multi_u.append(
                    borehole_multi_u.calculate_Rb(borehole_depth, buried_depth, borehole_radius, ground_conductivity,
                                                  temperature=temperature, use_explicit_models=True))

                list_dp_double.append(
                    double_u.pressure_drop(meg, flow, borehole_depth - buried_depth, temperature=temperature))
                list_dp_multi_u.append(
                    multi_u_tube.pressure_drop(meg, flow, borehole_depth - buried_depth, temperature=temperature))

            spacing_mm = satellite_position * 1000

            rb_multi_line, = ax_rb.plot(flow_rates, list_rb_multi_u,
                                        label=f'Multi U tube, sat. radius {spacing_mm:.0f} mm')

            dp_multi_line, = ax_dp.plot(flow_rates, list_dp_multi_u,
                                        label=f'Multi U tube, sat. radius {spacing_mm:.0f} mm')

        ax_rb.plot(flow_rates, list_rb_double, linestyle=':',
                   label=f'Double DN32, spacing {borehole_radius / 2 * 1000:.0f} mm')
        ax_dp.plot(flow_rates, list_dp_double, linestyle=':',
                   label=f'Double DN32, spacing {borehole_radius / 2 * 1000:.0f} mm')
        ax_rb.set_title(
            f'Borehole thermal resistance (d={2 * borehole_radius * 1000:.0f}mm, depth={borehole_depth}m, MEG 25v/v%)')
        ax_rb.set_ylabel('Effective borehole thermal resistance [mK/W]')
        ax_rb.set_xlabel('Flow rate [l/s]')
        ax_rb.legend()
        ax_rb.grid()

        ax_dp.set_title(f'Pressure drop (depth={borehole_depth}m, MEG 25v/v%)')
        ax_dp.set_ylabel('Pressure drop [kPa]')
        ax_dp.set_xlabel('Flow rate [l/s]')
        ax_dp.legend()
        ax_dp.grid()

        plt.show()


if __name__ == "__main__":  # pragma: no-cover
    resistances()
    resistances_2()
    create_graphs()
    create_graphs_2()
