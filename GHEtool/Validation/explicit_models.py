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
import time


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

    assert np.isclose(np.mean(Rf_pygfunction), 0.03824377850561424)
    assert np.isclose(np.mean(Rf_explicit_haaland), 0.03844466321909467)
    assert np.allclose(Rf_explicit_darcy_weisbach, Rf_pygfunction)


def explicit_double_U():
    """
    This function validates the explicit multipole model for the double U (zeroth and first order) for both
    the diagonal and adjacent pipe configurations.

    Returns
    -------
    None
    """
    fluid_data = TemperatureDependentFluidData('MPG', 25).create_constant(3)
    pipe_diag = DoubleUTube(1, 0.013, 0.016, 0.4, 0.05, config='diagonal')
    pipe_adj = DoubleUTube(1, 0.013, 0.016, 0.4, 0.05, config='adjacent')

    pyg_diag = []
    explicit_0_diag = []
    explicit_1_diag = []
    pyg_adj = []
    explicit_0_adj = []
    explicit_1_adj = []
    flow_range = np.linspace(0.1, 3, 41)

    for flow in flow_range:
        borehole = Borehole(fluid_data, pipe_diag, ConstantFlowRate(mfr=flow))
        pyg_diag.append(borehole.calculate_Rb(100, 4, 0.075, 3))
        explicit_0_diag.append(borehole.calculate_Rb(100, 4, 0.075, 3, use_explicit_models=True, order=0))
        explicit_1_diag.append(borehole.calculate_Rb(100, 4, 0.075, 3, use_explicit_models=True))
        borehole = Borehole(fluid_data, pipe_adj, ConstantFlowRate(mfr=flow))
        pyg_adj.append(borehole.calculate_Rb(100, 4, 0.075, 3))
        explicit_0_adj.append(borehole.calculate_Rb(100, 4, 0.075, 3, use_explicit_models=True, order=0))
        explicit_1_adj.append(borehole.calculate_Rb(100, 4, 0.075, 3, use_explicit_models=True))

    plt.figure()
    plt.plot(flow_range, pyg_diag, label="pygfunction (diag)")
    plt.plot(flow_range, explicit_0_diag, label="explicit (zeroth order) (diag)")
    plt.plot(flow_range, explicit_1_diag, label="explicit (first order) (diag)")
    plt.plot(flow_range, pyg_adj, label="pygfunction (adj)")
    plt.plot(flow_range, explicit_0_adj, label="explicit (zeroth order) (adj)")
    plt.plot(flow_range, explicit_1_adj, label="explicit (first order) (adj)")
    plt.legend()
    plt.xlabel('Mass flow rate per borehole [kg/s]')
    plt.ylabel('Borehole effective thermal resistance [mK/W]')

    plt.figure()
    plt.plot(flow_range, (np.array(explicit_0_diag) - np.array(pyg_diag)) / np.array(pyg_diag) * 100,
             label="explicit (zeroth order) (diag)")
    plt.plot(flow_range, (np.array(explicit_1_diag) - np.array(pyg_diag)) / np.array(pyg_diag) * 100,
             label="explicit (first order) (diag)")
    plt.plot(flow_range, (np.array(explicit_0_adj) - np.array(pyg_adj)) / np.array(pyg_adj) * 100,
             label="explicit (zeroth order) (adj)")
    plt.plot(flow_range, (np.array(explicit_1_adj) - np.array(pyg_adj)) / np.array(pyg_adj) * 100,
             label="explicit (first order) (adj)")
    plt.legend()
    plt.xlabel('Mass flow rate per borehole [kg/s]')
    plt.ylabel('Borehole effective thermal resistance [%]')
    plt.show()

    assert np.isclose(np.mean(explicit_0_diag), 0.08539800627074602)
    assert np.isclose(np.mean(explicit_1_diag), 0.08342306926253379)
    assert np.isclose(np.mean(explicit_0_adj), 0.08502207522826101)
    assert np.isclose(np.mean(explicit_1_adj), 0.08304282218149564)
    assert np.isclose(np.max((np.array(explicit_0_diag) - np.array(pyg_diag)) / np.array(pyg_diag)) * 100,
                      4.094697418965679)
    assert np.isclose(np.max((np.array(explicit_1_diag) - np.array(pyg_diag)) / np.array(pyg_diag)) * 100,
                      0.0007861507511423535)
    assert np.isclose(np.max((np.array(explicit_0_adj) - np.array(pyg_adj)) / np.array(pyg_adj)) * 100,
                      4.095255683936652)
    assert np.isclose(np.max((np.array(explicit_1_adj) - np.array(pyg_adj)) / np.array(pyg_adj)) * 100,
                      0.023209289763124377)


def explicit_single_U():
    """
    This function validates the explicit multipole model for the single U (zeroth, first and second order).
    Returns
    -------
    None
    """
    fluid_data = TemperatureDependentFluidData('MPG', 25).create_constant(3)
    pipe = SingleUTube(1, 0.013, 0.016, 0.4, 0.05)

    pyg = []
    explicit_0 = []
    explicit_1 = []
    explicit_2 = []

    flow_range = np.linspace(0.1, 3, 41)

    for flow in flow_range:
        borehole = Borehole(fluid_data, pipe, ConstantFlowRate(mfr=flow))
        pyg.append(borehole.calculate_Rb(100, 4, 0.075, 3))
        explicit_0.append(borehole.calculate_Rb(100, 4, 0.075, 3, use_explicit_models=True, order=0))
        explicit_1.append(borehole.calculate_Rb(100, 4, 0.075, 3, use_explicit_models=True, order=1))
        explicit_2.append(borehole.calculate_Rb(100, 4, 0.075, 3, use_explicit_models=True, order=2))

    plt.figure()
    plt.plot(flow_range, pyg, label="pygfunction")
    plt.plot(flow_range, explicit_0, label="explicit (zeroth order)")
    plt.plot(flow_range, explicit_1, label="explicit (first order)")
    plt.plot(flow_range, explicit_2, label="explicit (second order)")

    plt.legend()
    plt.xlabel('Mass flow rate per borehole [kg/s]')
    plt.ylabel('Borehole effective thermal resistance [mK/W]')

    plt.figure()
    plt.plot(flow_range, (np.array(explicit_0) - np.array(pyg)) / np.array(pyg) * 100,
             label="explicit (zeroth order)")
    plt.plot(flow_range, (np.array(explicit_1) - np.array(pyg)) / np.array(pyg) * 100,
             label="explicit (first order)")
    plt.plot(flow_range, (np.array(explicit_2) - np.array(pyg)) / np.array(pyg) * 100,
             label="explicit (second order)")
    plt.legend()
    plt.xlabel('Mass flow rate per borehole [kg/s]')
    plt.ylabel('Borehole effective thermal resistance [%]')
    plt.show()

    assert np.isclose(np.mean(explicit_0), 0.141308789605785)
    assert np.isclose(np.mean(explicit_1), 0.14011344398662381)
    assert np.isclose(np.mean(explicit_2), 0.14011372449441875)
    assert np.isclose(np.max((np.array(explicit_0) - np.array(pyg)) / np.array(pyg)) * 100, 1.068381355673901)
    assert np.isclose(np.max((np.array(explicit_1) - np.array(pyg)) / np.array(pyg)) * 100, 0.0014732157859187868)
    assert np.isclose(np.max((np.array(explicit_2) - np.array(pyg)) / np.array(pyg)) * 100, 7.206286403390892e-07)


def compare_multiple_resistances():
    """
    When working with variable fluid properties in GHEtool, the effective borehole thermal resistance is interpolated.
    Due to the implementation of explicit methods, this is no longer needed.
    In this function, the results will be compared in accuracy between the interpolated data, the original data and
    the new explicit way. This is also timed.

    Returns
    -------
    None
    """
    single = SingleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    flow = ConstantFlowRate(vfr=0.2)
    fluid = TemperatureDependentFluidData('MPG', 25)

    temperature_array = np.linspace(-8, 25, 1000)

    borehole = Borehole(fluid, single, flow)

    # 1. calculate iteratively with pygfunction
    pygfunction = []
    start_pyg = time.time()
    for temp in temperature_array:
        pygfunction.append(borehole.calculate_Rb(100, 1, 0.075, 2, use_explicit_models=False, temperature=temp))
    end_py = time.time()

    # 2. calculate iteratively with explicit models
    explicit_one_by_one = []
    start_explicit_obo = time.time()
    for temp in temperature_array:
        explicit_one_by_one.append(borehole.calculate_Rb(100, 1, 0.075, 2, use_explicit_models=True, temperature=temp))
    end_explicit_obo = time.time()

    # 3. with interpolation array
    start_interpolation_array = time.time()
    interpolation_array = borehole.calculate_Rb(100, 1, 0.075, 2, use_explicit_models=False,
                                                temperature=temperature_array)
    end_interpolation_array = time.time()

    # 4. with interpolation array
    start_explicit_array = time.time()
    explicit_array = borehole.calculate_Rb(100, 1, 0.075, 2, use_explicit_models=True, temperature=temperature_array)
    end_explicit_array = time.time()

    # convert to numpy arrays once
    pyg_arr = np.array(pygfunction)
    explicit_obo_arr = np.array(explicit_one_by_one)
    interp_arr = np.array(interpolation_array)
    explicit_arr = np.array(explicit_array)

    # relative differences in percent
    rel_diff_explicit_obo = (explicit_obo_arr - pyg_arr) / pyg_arr * 100
    rel_diff_interp = (interp_arr - pyg_arr) / pyg_arr * 100
    rel_diff_explicit_array = (explicit_arr - pyg_arr) / pyg_arr * 100

    # simulation times
    time_pyg = end_py - start_pyg
    time_explicit_obo = end_explicit_obo - start_explicit_obo
    time_interp = end_interpolation_array - start_interpolation_array
    time_explicit_array = end_explicit_array - start_explicit_array

    print(
        f"explicit pygfunction | "
        f"time [s] = {time_pyg:.4f}"
    )

    print(
        f"explicit one by one | "
        f"time [s] = {time_explicit_obo:.4f} | "
        f"mean error [%] = {np.mean(np.abs(rel_diff_explicit_obo)):.6e} | "
        f"max error [%] = {np.max(np.abs(rel_diff_explicit_obo)):.6e}"
    )

    print(
        f"interpolation array | "
        f"time [s] = {time_interp:.4f} | "
        f"mean error [%] = {np.mean(np.abs(rel_diff_interp)):.6e} | "
        f"max error [%] = {np.max(np.abs(rel_diff_interp)):.6e}"
    )

    print(
        f"explicit array | "
        f"time [s] = {time_explicit_array:.4f} | "
        f"mean error [%] = {np.mean(np.abs(rel_diff_explicit_array)):.6e} | "
        f"max error [%] = {np.max(np.abs(rel_diff_explicit_array)):.6e}"
    )

    plt.figure()
    plt.plot(temperature_array, pygfunction, label='pygfunction')
    plt.plot(temperature_array, explicit_one_by_one, label='explicit one by one')
    plt.plot(temperature_array, interpolation_array, label='interpolation array')
    plt.plot(temperature_array, explicit_array, label='explicit array')
    plt.xlabel("Temperature [°C]")
    plt.ylabel("Effective borehole thermal resistance [%]")
    plt.legend()

    plt.figure()
    plt.plot(temperature_array, rel_diff_explicit_obo, label="explicit one by one")
    plt.plot(temperature_array, rel_diff_interp, label="interpolation array")
    plt.plot(temperature_array, rel_diff_explicit_array, label="explicit array")
    plt.xlabel("Temperature [°C]")
    plt.ylabel("Relative difference [%]")
    plt.legend()

    plt.show()


def explicit_coaxial():
    """
    This function compares the implementation of the explicit coaxial model with the one in pygfunction.
    There is excellent overlap.

    Returns
    -------
    None
    """
    r_in_in = 0.0221
    r_in_out = 0.025
    r_out_in = 0.0487
    r_out_out = 0.055

    fluid_data = TemperatureDependentFluidData('MPG', 25).create_constant(3)
    pipe = CoaxialPipe(r_in_in, r_in_out, r_out_in, r_out_out, 0.4, 1)

    pyg = []
    explicit_1 = []

    flow_range = np.linspace(0.1, 3, 41)

    for flow in flow_range:
        borehole = Borehole(fluid_data, pipe, ConstantFlowRate(mfr=flow))
        pyg.append(borehole.calculate_Rb(100, 4, 0.075, 2, use_explicit_models=False))
        explicit_1.append(borehole.calculate_Rb(100, 4, 0.075, 2, use_explicit_models=True, order=1))

    plt.figure()
    plt.plot(flow_range, pyg, label="pygfunction")
    plt.plot(flow_range, explicit_1, label="explicit (first order)")

    plt.legend()
    plt.xlabel('Mass flow rate per borehole [kg/s]')
    plt.ylabel('Borehole effective thermal resistance [mK/W]')

    plt.figure()
    plt.plot(flow_range, (np.array(explicit_1) - np.array(pyg)) / np.array(pyg) * 100,
             label="explicit (first order)")
    plt.legend()
    plt.xlabel('Mass flow rate per borehole [kg/s]')
    plt.ylabel('Borehole effective thermal resistance [%]')
    plt.show()

    assert np.allclose(np.array(explicit_1) - np.array(pyg), 0)


if __name__ == "__main__":
    validate_convective_resistance()
    explicit_double_U()
    explicit_single_U()
    compare_multiple_resistances()
    explicit_coaxial()
