"""
This file contains a design example with the separatus probe, in comparison with a single and double U-tube.
A borehole diameter of DN90 was chosen for the separatus probe whereas for the single and double U-tube a DN140 was assumed.
A mass flow rate of 0.3 kg/s was assumed for all cases and no glycol was taken into account.
The grout thermal conductivity is 2 W/(mK), and the borehole dimensions where 1x4 with a borehole length of 110m.
The building heating and cooling demand was obtained from a residential building in Belgium.

It is shown that both single U and separatus have similar performance, whilst the double U-tube has a somewhat better
performance. These results have to be placed next to an economic evaluation of the different borefield designs.
"""

import numpy as np
import pygfunction as gt

from GHEtool import *

# set general parameters
ground_data = GroundFluxTemperature(1.9, 9.6, flux=0.07)
flow_data = ConstantFlowRate(mfr=0.3)
fluid_data = TemperatureDependentFluidData('MPG', 0)

# set building load
load = MonthlyBuildingLoadAbsolute(
    baseload_heating=np.array([2105, 2081, 1686, 1196, 550, 0, 0, 0, 144, 777, 1471, 1961]),
    baseload_cooling=np.array([0, 0, 0, 0, 682, 1248, 1650, 1608, 907, 0, 0, 0]),
    peak_heating=np.array([9.2, 9.12, 7.38, 5.21, 2.43, 0, 0, 0, 0.61, 3.39, 6.42, 8.59]),
    peak_cooling=np.array([0, 0, 0, 0, 3.61, 6.58, 8.7, 8.49, 4.78, 0, 0, 0]),
    simulation_period=40,
    dhw=2800,
    efficiency_heating=5.03,
    efficiency_cooling=20,
    efficiency_dhw=3.93
)


def design_with_single_U():
    """
    This function plots the temperature profile for a system with a single U-tube.

    Returns
    -------
    None
    """
    pipe_data = SingleUTube(2, 0.013, 0.016, 0.42, 0.035)

    borefield = Borefield(load=load, ground_data=ground_data, fluid_data=fluid_data, flow_data=flow_data,
                          pipe_data=pipe_data)
    borefield.set_min_fluid_temperature(6)
    borefield.set_max_fluid_temperature(17)

    borefield.create_rectangular_borefield(1, 4, 6, 6, 110, 0.7, 0.07)
    borefield.print_temperature_profile()


def design_with_double_U():
    """
    This function plots the temperature profile for a system with a double U-tube.

    Returns
    -------
    None
    """
    pipe_data = DoubleUTube(2, 0.013, 0.016, 0.42, 0.035)

    borefield = Borefield(load=load, ground_data=ground_data, fluid_data=fluid_data, flow_data=flow_data,
                          pipe_data=pipe_data)

    borefield.set_min_fluid_temperature(6)
    borefield.set_max_fluid_temperature(17)

    borefield.create_rectangular_borefield(1, 4, 6, 6, 110, 0.7, 0.07)
    borefield.print_temperature_profile()


def design_with_separatus():
    """
    This function plots the temperature profile for a system with a separatus probe.

    Returns
    -------
    None
    """
    pipe_data = Separatus(2)

    borefield = Borefield(load=load, ground_data=ground_data, fluid_data=fluid_data, flow_data=flow_data,
                          pipe_data=pipe_data)

    borefield.set_min_fluid_temperature(6)
    borefield.set_max_fluid_temperature(17)

    borefield.create_rectangular_borefield(1, 4, 6, 6, 110, 0.7, 0.045)
    borefield.print_temperature_profile()


def comparison():
    """
    This function validates the explicit multipole model for the single U (zeroth, first and second order).
    Returns
    -------
    None
    """
    fluid_data = TemperatureDependentFluidData('MEG', 25, mass_percentage=False).create_constant(0)
    from GHEtool.VariableClasses.PipeData.SeparatusNew import SeparatusNew
    separatus = SeparatusNew(2)
    separatus_old = Separatus(2)
    double_pipe = DoubleUTube(1, 0.013, 0.016, 0.4, 0.035)

    separatus_140 = []
    separatus_90 = []
    separatus_90_old = []
    double = []
    flow_range = np.linspace(0.05, 2, 200)
    depth = 100

    for flow in flow_range:
        borehole = Borehole(fluid_data, separatus, ConstantFlowRate(mfr=flow))
        separatus_140.append(borehole.calculate_Rb(depth, 0, 0.07, 2, use_explicit_models=True))
        borehole = Borehole(fluid_data, separatus, ConstantFlowRate(mfr=flow))
        separatus_90.append(borehole.calculate_Rb(depth, 0, 0.045, 2, use_explicit_models=True))
        borehole = Borehole(fluid_data, separatus_old, ConstantFlowRate(mfr=flow))
        separatus_90_old.append(borehole.calculate_Rb(depth, 0, 0.045, 2, use_explicit_models=True))
        borehole = Borehole(fluid_data, double_pipe, ConstantFlowRate(mfr=flow))
        double.append(borehole.calculate_Rb(depth, 0, 0.07, 2, use_explicit_models=True))
    import matplotlib.pyplot as plt

    plt.figure()
    plt.plot(flow_range, separatus_140, label="Separatus (2026) (d=140mm, kg=2W/(mK))")
    plt.plot(flow_range, separatus_90, label="Separatus (2026) (d=90mm, kg=2W/(mK))")
    plt.plot(flow_range, separatus_90_old, label="Separatus (2025) (d=90mm, kg=2W/(mK))")
    plt.plot(flow_range, double, label="Double DN32 (d=140mm, kg=1W/(mK))")

    plt.legend()
    plt.xlabel('Mass flow rate per borehole [kg/s]')
    plt.ylabel('Borehole effective thermal resistance [mK/W]')
    plt.title(f'Borehole depth 100m @ 25v/v% MEG')
    # plt.plot(flow_range, (np.array(original_model) - np.array(new_model)) / np.array(original_model) * 100,
    #          label="diff %")
    # plt.xlabel('Mass flow rate per borehole [kg/s]')
    # plt.ylabel('Difference in borehole effective thermal resistance [%]')
    plt.show()


if __name__ == "__main__":
    comparison()
    design_with_single_U()
    design_with_double_U()
    design_with_separatus()
