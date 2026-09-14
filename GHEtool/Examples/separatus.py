from GHEtool import *
import numpy as np
import matplotlib.pyplot as plt


def create_graphs():
    """
    This function creates a graph for the separatus model.

    Returns
    -------
    None
    """
    fluid_data = TemperatureDependentFluidData('MEG', 25, mass_percentage=False).create_constant(0)
    pipe = Separatus(2)

    sep_90 = []
    sep_140 = []
    double_model = []

    double = DoubleUTube(1, 0.013, 0.016, 0.4, 0.035)
    flow_range = np.arange(0.1, 1, 0.0001) * 3.6

    depth = 100

    for flow in flow_range:
        borehole = Borehole(fluid_data, pipe, ConstantFlowRate(vfr=flow / 3.6))
        sep_90.append(borehole.calculate_Rb(depth, 0, 0.045, 2, use_explicit_models=True))

        sep_140.append(borehole.calculate_Rb(depth, 0, 0.07, 2, use_explicit_models=True, new=True))
        borehole = Borehole(fluid_data, double, ConstantFlowRate(vfr=flow / 3.6))
        double_model.append(borehole.calculate_Rb(depth, 0, 0.07, 2, use_explicit_models=True))

    plt.figure()
    plt.plot(flow_range, sep_140, label="Separatus (d=140mm)")
    plt.plot(flow_range, double_model, label="Double DN32 (d=140mm)")
    plt.plot(flow_range, sep_90, label="Separatus (d=90mm)")
    plt.legend()
    plt.xlabel('Flow rate per borehole [m³/h]')
    plt.ylabel('Borehole effective thermal resistance [mK/W]')
    plt.title(f'Borehole resistance for MEG 25 v/v% @ 0°C')
    plt.show()


if __name__ == "__main__":
    create_graphs()
