"""
In this file, the explicit formulation of the multipole method to calculate the borehole effective thermal resistance
is being validated against the model implemented in pygfunction (which is default in GHEtool).

The single U models (zeroth, first and second order) are based on the work of (Javed & Claesson, 2018).
The double U models (zeroth and first order) are based on the work of (Claesson & Javed, 2019).

References
----------
Claesson, J., & Javed, S. (2018). Explicit Multipole Formulas for Calculating Thermal Resistance of Single U-Tube Ground Heat Exchangers. Energies, 11(1), 214. https://doi.org/10.3390/en11010214
Claesson, J., & Javed, S. (2019). Explicit multipole formulas and thermal network models for calculating thermal resistances of double U-pipe borehole heat exchangers. Science and Technology for the Built Environment, 25(8), 980–992. https://doi.org/10.1080/23744731.2019.1620565
"""

from GHEtool import *
import matplotlib.pyplot as plt
import numpy as np


def validate_convective_resistance():
    """
    This function validates convective resistance as implemented for the explicit formulation with the one
    implemented in pygfunction. The difference is non-existent for the Darcy-Weisbach equation (since this is also
    implemented in pygfunction) and minor for Haaland.

    Returns
    -------
    None
    """
    pipe = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    fluid = TemperatureDependentFluidData('MPG', 25).create_constant(0)

    Rf_pygfunction = []
    Rf_explicit_haaland = []
    Rf_explicit_darcy_weisbach = []

    flow_range = np.linspace(0.1, 3, 20)
    for flow in flow_range:
        pipe.calculate_resistances(fluid, ConstantFlowRate(mfr=flow))
        Rf_pygfunction.append(pipe.R_f)
        Rf_explicit_haaland.append(
            pipe.calculate_convective_resistance(ConstantFlowRate(mfr=flow), fluid, haaland=True))
        Rf_explicit_darcy_weisbach.append(
            pipe.calculate_convective_resistance(ConstantFlowRate(mfr=flow), fluid, haaland=False))

    plt.figure()
    plt.plot(flow_range, Rf_pygfunction, label="pygfunction")
    plt.plot(flow_range, Rf_explicit_haaland, label="explicit (Haaland)")
    plt.plot(flow_range, Rf_explicit_darcy_weisbach, label="explicit (Darcy-Weisbach)")
    plt.xlabel('Mass flow rate per borehole [kg/s]')
    plt.ylabel('Convective resistance [mK/W]')
    plt.legend()

    plt.figure()
    plt.plot(flow_range, (np.array(Rf_pygfunction) - np.array(Rf_explicit_haaland)) / np.array(Rf_pygfunction) * 100,
             label="Relative difference (Haaland)")
    plt.plot(flow_range,
             (np.array(Rf_pygfunction) - np.array(Rf_explicit_darcy_weisbach)) / np.array(Rf_pygfunction) * 100,
             label="Relative difference (Darcy-Weisbach)")
    plt.xlabel('Mass flow rate per borehole [kg/s]')
    plt.ylabel('Convective resistance [mK/W]')
    plt.legend()
    plt.show()

    assert np.isclose(np.mean(Rf_pygfunction), 0.0569210708867547)
    assert np.isclose(np.mean(Rf_explicit_haaland), 0.05706228270598758)


if __name__ == "__main__":
    validate_convective_resistance()
