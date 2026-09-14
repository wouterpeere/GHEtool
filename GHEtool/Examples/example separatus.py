from GHEtool import *
import numpy as np
import matplotlib.pyplot as plt

from GHEtool.VariableClasses.PipeData.Separatus import SeparatusNew


def borehole_resistance_ifo_reynolds():
    """
    This function validates the explicit multipole model for the single U (zeroth, first and second order).
    Returns
    -------
    None
    """
    fluid_data = TemperatureDependentFluidData('MEG', 25, mass_percentage=False).create_constant(0)
    pipe = Separatus(2)
    pipe_new = SeparatusNew(2)
    separatus_single_u = SingleUTube(
        k_g=1.5,
        r_in=(35.74 / 2 - 3) * 0.001,
        r_out=(35.74 / 2) * 0.001,
        k_p=0.44,
        D_s=36 / 2 * 0.001
    )
    original_model = []
    new_model = []
    new_model_2 = []
    separatus_single_u_model = []

    flow_range = np.arange(0.1, 1, 0.0001) * 3.6
    depth = 100

    for flow in flow_range:
        borehole = Borehole(fluid_data, pipe, ConstantFlowRate(vfr=flow / 3.6))
        original_model.append(borehole.calculate_Rb(depth, 0, 0.045, 2, use_explicit_models=True))
        borehole = Borehole(fluid_data, pipe_new, ConstantFlowRate(vfr=flow / 3.6))
        new_model.append(borehole.calculate_Rb(depth, 0, 0.045, 2, use_explicit_models=True))
        borehole = Borehole(fluid_data, pipe_new, ConstantFlowRate(vfr=flow / 3.6))
        # new_model_2.append(borehole.calculate_Rb(depth, 0, 0.045, 2, use_explicit_models=True))
        borehole = Borehole(fluid_data, separatus_single_u, ConstantFlowRate(vfr=flow / 3.6))
        separatus_single_u_model.append(borehole.calculate_Rb(depth, 0, 0.045, 2, use_explicit_models=True))

    plt.figure()
    plt.plot(flow_range, original_model, label="separatus SU")
    plt.plot(flow_range, new_model, label="separatus BEM 2026")
    plt.legend()
    plt.xlabel('Flow rate per borehole [m³/h]')
    plt.ylabel('Borehole effective thermal resistance [mK/W]')
    plt.title(f'Borehole resistance for MEG 25v/v% @ 0°C')

    plt.figure()
    plt.plot([separatus_single_u.Re(fluid_data, ConstantFlowRate(vfr=flow / 3.6)) for flow in flow_range],
             original_model,
             label="separatus SU")
    plt.plot([pipe_new.Re(fluid_data, ConstantFlowRate(vfr=flow / 3.6)) for flow in flow_range], new_model,
             label="separatus BEM 2026")
    # plt.plot(flow_range, new_model_2, label="BEM model (different cross-section)")
    # plt.plot(flow_range, original_model, label="single-U model")

    plt.legend()
    plt.xlabel('Reynolds number [-]')
    plt.ylabel('Borehole effective thermal resistance [mK/W]')
    plt.title(f'Borehole resistance for MEG 25v/v% @ 0°C')

    plt.show()


def numerical():
    fluid = TemperatureDependentFluidData('MPG', 30, mass_percentage=False)
    flow = ConstantFlowRate(vfr=0.23)
    separatus_old = Separatus(1.5)
    separatus_new = SeparatusNew(1.5)
    borehole_old = Borehole(fluid, separatus_old, flow)
    borehole_new = Borehole(fluid, separatus_new, flow)
    print(borehole_old.calculate_Rb(100, 1, 0.07, 2, temperature=2, use_explicit_models=True))
    print(borehole_new.calculate_Rb(100, 1, 0.07, 2, temperature=2, use_explicit_models=True))
    print(borehole_old.Re(temperature=2))
    print(borehole_new.Re(temperature=2))


def figure_Re():
    fluid = TemperatureDependentFluidData('MEG', 25, mass_percentage=False).create_constant(0)
    separatus_old = Separatus(1.5)
    separatus_new = SeparatusNew(1.5)
    separatus_single_u = SingleUTube(
        k_g=1.5,
        r_in=(35.74 / 2 - 3) * 0.001,
        r_out=(35.74 / 2) * 0.001,
        k_p=0.44,
        D_s=36 / 2 * 0.001
    )

    list_re_old = []
    list_re_new = []
    list_re_single = []

    flow_rates = np.arange(0.1, 0.5, 0.01) * 3.6

    for val in flow_rates:
        flow = ConstantFlowRate(vfr=val / 3.6)
        list_re_old.append(separatus_old.Re(fluid, flow))
        list_re_new.append(separatus_new.Re(fluid, flow))
        list_re_single.append(separatus_single_u.Re(fluid, flow))

    fig, ax = plt.subplots()

    # line1, = ax.plot(flow_rates, list_re_old, label='Re (2025)')
    line3, = ax.plot(flow_rates, list_re_single, label='separatus SU')
    line2, = ax.plot(flow_rates, list_re_new, label='separatus BEM 2026')

    target_re = 2300

    for line, re_values in zip([line3, line2, ], [list_re_single, list_re_new]):
        re_values = np.asarray(re_values)

        if re_values.min() <= target_re <= re_values.max():
            x_cross = np.interp(target_re, re_values, flow_rates)
            print(x_cross)
            ax.vlines(x_cross, ymin=0, ymax=target_re, colors=line.get_color(), linestyles=':', linewidth=1.5)

    ax.legend()
    ax.set_ylim(bottom=0)

    ax.set_xlabel('Flow rate [m³/h]')
    ax.set_ylabel('Reynolds number')
    ax.set_title('Reynolds number for MEG 25 v/v% @ 0°C')

    plt.show()


def figure_1():
    single_smooth = SingleUTube(1, 0.013, 0.016, 0.4, 0.03)

    double_smooth = DoubleUTube(1, 0.013, 0.016, 0.4, 0.03)

    single_turbo = SeparatusNew(2)
    double_turbo = Turbocollector(1.5, 0.013, 0.016, 0.035, 2)

    fluid = TemperatureDependentFluidData('MPG', 25, mass_percentage=False)

    flow_rates = np.arange(0.1, 0.8, 0.01)

    list_rb_single_turbo, list_rb_single_smooth, list_rb_double_turbo, list_rb_double_smooth = [], [], [], []
    list_dp_single_turbo, list_dp_single_smooth, list_dp_double_turbo, list_dp_double_smooth = [], [], [], []

    for val in flow_rates:
        flow = ConstantFlowRate(vfr=val)

        borehole_single_smooth = Borehole(fluid, single_smooth, flow)
        borehole_double_smooth = Borehole(fluid, double_smooth, flow)
        borehole_single_turbo = Borehole(fluid, single_turbo, flow)
        borehole_double_turbo = Borehole(fluid, double_turbo, flow)

        list_rb_single_smooth.append(
            borehole_single_smooth.calculate_Rb(100, 0.7, 0.06, 2, temperature=5, use_explicit_models=True))
        list_rb_double_smooth.append(
            borehole_double_smooth.calculate_Rb(100, 0.7, 0.06, 2, temperature=5, use_explicit_models=True))
        list_rb_single_turbo.append(
            borehole_single_turbo.calculate_Rb(100, 0.7, 0.045, 2, temperature=5, use_explicit_models=True))
        list_rb_double_turbo.append(
            borehole_double_turbo.calculate_Rb(100, 0.7, 0.07, 2, temperature=5, use_explicit_models=True))

        list_dp_single_smooth.append(single_smooth.pressure_drop(fluid, flow, 100 - 0.7, temperature=5))
        list_dp_double_smooth.append(double_smooth.pressure_drop(fluid, flow, 100 - 0.7, temperature=5))
        list_dp_single_turbo.append(single_turbo.pressure_drop(fluid, flow, 100 - 0.7, temperature=5))
        list_dp_double_turbo.append(double_turbo.pressure_drop(fluid, flow, 100 - 0.7, temperature=5))

    plt.figure()
    plt.plot(flow_rates, list_rb_single_smooth, label="Single DN32 (d=120mm, kg=1W/(mK)")
    plt.plot(flow_rates, list_rb_double_smooth, label="Double DN32 (d=120mm, kg=1W/(mK)")
    plt.plot(flow_rates, list_rb_single_turbo, label="Separatus (d=90mm, kg=2W/(mK))")
    # plt.plot(flow_rates, list_rb_double_turbo, label="Double TurboCollector")

    plt.title(f'Borehole thermal resistance for MPG (25% @ 5°C)')
    plt.ylabel('Effective borehole thermal resistance [mK/W]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.figure()

    plt.plot(flow_rates, list_dp_single_smooth, label="Single DN32 (d=120mm, kg=1W/(mK)")
    plt.plot(flow_rates, list_dp_double_smooth, label="Double DN32 (d=120mm, kg=1W/(mK)")
    plt.plot(flow_rates, list_dp_single_turbo, label="Separatus (d=90mm, kg=2W/(mK))")
    # plt.plot(flow_rates, list_dp_double_turbo, label="Double TurboCollector")
    plt.title(f'Pressure drop for MPG (25% @ 5°C)')
    plt.ylabel('Pressure drop [kPa]')
    plt.xlabel('Flow rate [l/s]')
    plt.legend()
    plt.show()


def subresistances():
    """
    This function validates the explicit multipole model for the single U (zeroth, first and second order).
    Returns
    -------
    None
    """
    fluid_data = TemperatureDependentFluidData('MPG', 30, mass_percentage=False).create_constant(2)
    pipe = Separatus(2)
    pipe_new = SeparatusNew(2)
    coax = CoaxialPipe(0.013, 0.016, 0.0519 / 2 - 0.00305, 0.0519 / 2, 0.4, 2)

    original_model = []
    new_model = []
    new_model_2 = []
    double_model = []

    double = DoubleUTube(1, 0.013, 0.014, 0.4, 0.03)
    # print(double.explicit_model_borehole_resistance(fluid_data, ConstantFlowRate(vfr=0.3), 2,
    #                                                 gt.boreholes.Borehole(120, 1, 0.07, 0, 0)))
    # print(pipe_new.explicit_model_borehole_resistance(fluid_data, ConstantFlowRate(vfr=0.3), 2,
    #                                                   gt.boreholes.Borehole(120, 1, 0.07, 0, 0)))
    # print(pipe.explicit_model_borehole_resistance(fluid_data, ConstantFlowRate(vfr=0.3), 2,
    #                                               gt.boreholes.Borehole(120, 1, 0.07, 0, 0)))
    flow_range = np.linspace(0.05, 5, 200)
    depth = 100

    for flow in flow_range:
        borehole = Borehole(fluid_data, pipe_new, ConstantFlowRate(mfr=flow))
        borehole.calculate_Rb(depth, 0, 0.045, 2, use_explicit_models=True, new=True)
        original_model.append(borehole.pipe_data._Rb)

        borehole = Borehole(fluid_data, pipe_new, ConstantFlowRate(mfr=flow))
        borehole.calculate_Rb(depth, 0, 0.045, 2, use_explicit_models=True, new=True)
        new_model.append(borehole.pipe_data._Ra)

        borehole = Borehole(fluid_data, coax, ConstantFlowRate(mfr=flow))
        borehole.calculate_Rb(depth, 0, 0.045, 2, use_explicit_models=True, new=True)
        new_model_2.append(borehole.pipe_data._Rb)

        borehole = Borehole(fluid_data, coax, ConstantFlowRate(mfr=flow))
        borehole.calculate_Rb(depth, 0, 0.045, 2, use_explicit_models=True, new=True)
        double_model.append(borehole.pipe_data._Ra)

    plt.figure()
    plt.plot(flow_range, original_model, label="sep Rb")
    plt.plot(flow_range, new_model, label="sep Ra")
    plt.plot(flow_range, new_model_2, label="coax Rb")
    plt.plot(flow_range, double_model, label="coax Ra")

    plt.legend()
    plt.xlabel('Mass flow rate per borehole [kg/s]')
    plt.ylabel('Borehole effective thermal resistance [mK/W]')
    plt.title(f'Borehole depth: {depth}m')
    # plt.figure()
    # plt.plot(flow_range, (np.array(original_model) - np.array(new_model)) / np.array(original_model) * 100,
    #          label="diff %")
    # plt.xlabel('Mass flow rate per borehole [kg/s]')
    # plt.ylabel('Difference in borehole effective thermal resistance [%]')
    plt.show()


def explicit_single_U():
    """
    This function validates the explicit multipole model for the single U (zeroth, first and second order).
    Returns
    -------
    None
    """
    fluid_data = TemperatureDependentFluidData('MEG', 25, mass_percentage=False).create_constant(0)
    print(fluid_data)
    pipe = Separatus(2)
    pipe_new = SeparatusNew(2)
    coax = CoaxialPipe(0.013, 0.016, 0.022, 0.025, 0.4, 2)

    original_model = []
    new_model = []
    new_model_2 = []
    double_model = []

    double = DoubleUTube(1, 0.013, 0.016, 0.4, 0.035)
    # print(double.explicit_model_borehole_resistance(fluid_data, ConstantFlowRate(vfr=0.3), 2,
    #                                                 gt.boreholes.Borehole(120, 1, 0.07, 0, 0)))
    # print(pipe_new.explicit_model_borehole_resistance(fluid_data, ConstantFlowRate(vfr=0.3), 2,
    #                                                   gt.boreholes.Borehole(120, 1, 0.07, 0, 0)))
    # print(pipe.explicit_model_borehole_resistance(fluid_data, ConstantFlowRate(vfr=0.3), 2,
    #                                               gt.boreholes.Borehole(120, 1, 0.07, 0, 0)))
    flow_range = np.arange(0.1, 1, 0.0001) * 3.6

    depth = 100

    for flow in flow_range:
        borehole = Borehole(fluid_data, pipe, ConstantFlowRate(vfr=flow / 3.6))
        original_model.append(borehole.calculate_Rb(depth, 0, 0.045, 2, use_explicit_models=True))
        borehole = Borehole(fluid_data, pipe_new, ConstantFlowRate(vfr=flow / 3.6))
        new_model.append(borehole.calculate_Rb(depth, 0, 0.045, 2, use_explicit_models=True))
        borehole = Borehole(fluid_data, pipe_new, ConstantFlowRate(vfr=flow / 3.6))
        new_model_2.append(borehole.calculate_Rb(depth, 0, 0.07, 2, use_explicit_models=True, new=True))
        borehole = Borehole(fluid_data, double, ConstantFlowRate(vfr=flow / 3.6))
        double_model.append(borehole.calculate_Rb(depth, 0, 0.07, 2, use_explicit_models=True))

    plt.figure()
    # plt.plot(flow_range, original_model, label="Separatus SU (d=90mm)")
    plt.plot(flow_range, new_model_2, label="Separatus (d=140mm)")
    plt.plot(flow_range, double_model, label="Double DN32 (d=140mm)")
    plt.plot(flow_range, new_model, label="Separatus (d=90mm)")
    # plt.plot(flow_range, new_model_2, label="coax")

    plt.legend()
    plt.xlabel('Flow rate per borehole [m³/h]')
    plt.ylabel('Borehole effective thermal resistance [mK/W]')
    plt.title(f'Borehole resistance for MEG 25 v/v% @ 0°C')
    # plt.figure()
    # plt.plot(flow_range, (np.array(original_model) - np.array(new_model)) / np.array(original_model) * 100,
    #          label="diff %")
    # plt.xlabel('Mass flow rate per borehole [kg/s]')
    # plt.ylabel('Difference in borehole effective thermal resistance [%]')
    plt.show()


def explicit_single_U_2():
    """
    This function validates the explicit multipole model for the single U (zeroth, first and second order).
    Returns
    -------
    None
    """
    fluid_data = TemperatureDependentFluidData('MEG', 25).create_constant(0)
    pipe_new = SeparatusNew(2)
    single_u_pipe = SingleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    double_u_pipe = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)

    single_u = []
    double_u = []
    separatus_140 = []
    separatus_90 = []
    depth = 70
    flow_range = np.arange(0.1, 1, 0.0001) * 3.6

    for flow in flow_range:
        borehole = Borehole(fluid_data, single_u_pipe, ConstantFlowRate(vfr=flow / 3.6))
        single_u.append(borehole.calculate_Rb(depth, 1, 0.06, 2, use_explicit_models=True))
        borehole = Borehole(fluid_data, double_u_pipe, ConstantFlowRate(vfr=flow / 3.6))
        double_u.append(borehole.calculate_Rb(depth, 1, 0.06, 2, use_explicit_models=True))
        borehole = Borehole(fluid_data, pipe_new, ConstantFlowRate(vfr=flow / 3.6))
        separatus_140.append(borehole.calculate_Rb(depth, 1, 0.06, 2, use_explicit_models=True))
        borehole = Borehole(fluid_data, pipe_new, ConstantFlowRate(vfr=flow / 3.6))
        separatus_90.append(borehole.calculate_Rb(depth, 1, 0.045, 2, use_explicit_models=True))

    plt.figure()
    plt.plot(flow_range, single_u, label="Single DN32 (120mm)")
    plt.plot(flow_range, double_u, label="Double DN32 (120mm)")
    plt.plot(flow_range, separatus_140, label="Separatus (120 mm)")
    plt.plot(flow_range, separatus_90, label="Separatus (90 mm)")

    plt.legend()
    plt.xlabel('Mass flow rate per borehole [kg/s]')
    plt.ylabel('Borehole effective thermal resistance [mK/W] (MPG 25 v/v% @ 5°C)')

    # plt.figure()
    # plt.plot(flow_range, (np.array(original_model) - np.array(new_model)) / np.array(original_model) * 100,
    #          label="diff %")
    # plt.xlabel('Mass flow rate per borehole [kg/s]')
    # plt.ylabel('Difference in borehole effective thermal resistance [%]')
    plt.show()


def depth():
    """
    This function validates the explicit multipole model for the single U (zeroth, first and second order).
    Returns
    -------
    None
    """
    fluid_data = TemperatureDependentFluidData('MEG', 25).create_constant(0)
    pipe = Separatus(2)
    pipe_new = SeparatusNew(2)
    original_model = []
    new_model = []
    double_model_120 = []
    double_model_140 = []
    double = DoubleUTube(1, 0.013, 0.016, 0.4, 0.035)

    flow = ConstantFlowRate(vfr=0.25)

    depth_range = np.linspace(40, 150, 100)

    for depth in depth_range:
        borehole = Borehole(fluid_data, pipe, flow)
        original_model.append(borehole.calculate_Rb(depth, 4, 0.045, 2, use_explicit_models=True))
        borehole = Borehole(fluid_data, pipe_new, flow)
        new_model.append(borehole.calculate_Rb(depth, 4, 0.045, 2, use_explicit_models=True))
        borehole = Borehole(fluid_data, double, flow)
        double_model_120.append(borehole.calculate_Rb(depth, 4, 0.06, 2, use_explicit_models=True))
        double_model_140.append(borehole.calculate_Rb(depth, 4, 0.07, 2, use_explicit_models=True))
    plt.figure()
    # plt.plot(depth_range, original_model, label="old model (90 mm)")
    plt.plot(depth_range, new_model, label="new model (90 mm)")
    plt.plot(depth_range, double_model_120, label="double (120 mm)")
    plt.plot(depth_range, double_model_140, label="double (140 mm)")

    plt.legend()
    plt.xlabel('Borehole depth (m)')
    plt.ylabel('Borehole effective thermal resistance [mK/W]')
    plt.show()


def TRT_brudrill():
    """
    Grout: 2 W/(mK)?
    Debiet?

    """
    fluid_data = TemperatureDependentFluidData('MPG', 0).create_constant(15)
    pipe = Separatus(2)
    pipe_new = SeparatusNew(2)
    original_model = []
    new_model = []

    flow_range = np.linspace(0.05, 2, 41)

    for flow in flow_range:
        borehole = Borehole(fluid_data, pipe, ConstantFlowRate(mfr=flow))
        original_model.append(borehole.calculate_Rb(98, 1, 0.089 / 2, 1.89, use_explicit_models=True))
        borehole = Borehole(fluid_data, pipe_new, ConstantFlowRate(mfr=flow))
        new_model.append(borehole.calculate_Rb(98, 1, 0.089 / 2, 1.89, use_explicit_models=True))
    estimated_flow = ConstantDeltaTFlowRate(delta_temp_extraction=4, delta_temp_injection=4)
    plt.figure()
    plt.plot(flow_range, original_model, label="Separatus (old)")
    plt.plot(flow_range, new_model, label="Separatus (new)")
    plt.plot(flow_range, np.full(flow_range.shape, 0.137), label="TRT Brudrill")
    plt.vlines(estimated_flow.vfr_borefield(fluid_data, power=5), min(original_model), max(new_model),
               color="black")

    plt.legend()
    plt.xlabel('Mass flow rate per borehole [kg/s]')
    plt.ylabel('Borehole effective thermal resistance [mK/W]')
    plt.show()


def TRT_davos():
    """
    Estimate grout to be 1.5 W/(mK)
    Estimate fluid water
    """
    fluid_data = TemperatureDependentFluidData('MEG', 0).create_constant(10)
    pipe = Separatus(1.5)
    pipe_new = SeparatusNew(1.5)
    original_model = []
    new_model = []

    flow_range = np.linspace(0.05, 2, 41)

    for flow in flow_range:
        borehole = Borehole(fluid_data, pipe, ConstantFlowRate(mfr=flow))
        original_model.append(borehole.calculate_Rb(38, 0, 0.132 / 2, 2.0, use_explicit_models=True))
        borehole = Borehole(fluid_data, pipe_new, ConstantFlowRate(mfr=flow))
        new_model.append(borehole.calculate_Rb(38, 0, 0.132 / 2, 2.0, use_explicit_models=True))

    plt.figure()
    plt.plot(flow_range, original_model, label="Separatus (old)")
    plt.plot(flow_range, new_model, label="Separatus (new)")
    plt.plot(flow_range, np.full(flow_range.shape, 0.19), label="TRT Davos")

    plt.vlines(617 / fluid_data.rho() * 1000 / 3600, min(original_model), max(new_model), color="black")  # 617 l/h

    plt.legend()
    plt.xlabel('Mass flow rate per borehole [kg/s]')
    plt.ylabel('Borehole effective thermal resistance [mK/W]')
    plt.show()


def alge():
    print('------------------\n Case Alge\n------------------\n')

    fluid_data = TemperatureDependentFluidData('MEG', 25).create_constant(3)
    pipe = DoubleUTube(1, 0.013, 0.016, 0.4, 0.035)
    pipe_new = SeparatusNew(2)
    # borehole = Borehole(fluid_data, pipe, ConstantFlowRate(vfr=1119.15 / 3600))
    # print('double', borehole.calculate_Rb(90, 1, (152e-3) / 2, 1.5, use_explicit_models=True))
    # borehole = Borehole(fluid_data, pipe_new, ConstantFlowRate(vfr=1119.15 / 3600))
    # print('sep (new)', borehole.calculate_Rb(90, 1, (152e-3) / 2, 1.5, use_explicit_models=True))
    # borehole.pipe_data = Separatus(2)
    # print('sep (old)', borehole.calculate_Rb(90, 1, (152e-3) / 2, 1.5, use_explicit_models=True))

    # line 998, 195 min
    borehole_length = 90

    borehole = Borehole(fluid_data, pipe, ConstantFlowRate(vfr=1098 / 3600))
    rb_double = borehole.calculate_Rb(borehole_length, 1, (152e-3) / 2, 1.5, use_explicit_models=True)
    borehole = Borehole(fluid_data, pipe_new, ConstantFlowRate(vfr=1098 / 3600))
    rb_sep_new = borehole.calculate_Rb(borehole_length, 1, (152e-3) / 2, 1.5, use_explicit_models=True)
    borehole.pipe_data = Separatus(2)
    rb_sep_old = borehole.calculate_Rb(borehole_length, 1, (152e-3) / 2, 1.5, use_explicit_models=True)

    print(f'Rb double: {rb_double:.4f}')
    print(f'Rb separatus (old): {rb_sep_old:.4f}', )
    print(f'Rb separatus (new): {rb_sep_new:.4f}', )

    # power
    power_sep = 1997.2
    power_double = 1809.28
    # separatus slightly worse --> greater difference between borehole wall and fluid
    # temperature identical with double U --> double U already somewhat colder --> ok!

    temp_diff_double = power_double * rb_double / 90
    temp_diff_sep_old = power_sep * rb_sep_old / 90
    temp_diff_sep_new = power_sep * rb_sep_new / 90
    print(f'Temperature difference fluid-ground double: {temp_diff_double:.2f}°C')
    print(f'Temperature difference fluid-ground separatus (old): {temp_diff_sep_old:.2f}°C')
    print(f'Temperature difference fluid-ground separatus (new): {temp_diff_sep_new:.2f}°C')

    T_inlet = 1.91
    T_out_sep = 3.53
    T_out_double = 3.31
    T_sep_avg = 0.5 * (T_inlet + T_out_sep)
    T_double_avg = 0.5 * (T_inlet + T_out_double)

    print(f'Estimated ground temperature double: {temp_diff_double + T_double_avg:.2f}°C')
    print(f'Estimated ground temperature separatus (old): {temp_diff_sep_old + T_sep_avg:.2f}°C')
    print(f'Estimated ground temperature separatus (new): {temp_diff_sep_new + T_sep_avg:.2f}°C')

    # New ground temperature is slightly higher than existing one (about 0.38°C), which seems reasonable.
    # Old separatus model gives temperature that is lower than a borehole that has been in use for a couple of years.

    sep_in = 1.91
    double_in = 1.91
    delta_t_sep = 3.53 - 1.91
    delta_t_double = 3.31 - 1.91
    t_sep_avg = 0.5 * (sep_in + sep_in - delta_t_sep)
    t_double_avg = 0.5 * (double_in + double_in - delta_t_double)
    ratio = power_double / power_sep
    print('Measurement data\n----------------------')
    print(f'Average temperature separatus: {t_sep_avg:.2f}°C')
    print(f'Average temperature double: {t_double_avg:.2f}°C')
    print(f'Difference in average temperature: {t_double_avg - t_sep_avg:.2f}°C')
    print(f'Power separatus: {power_sep:.2f}W')
    print(f'Power double U: {power_double:.2f}W')
    print(f'Power ratio: {power_double / power_sep:.2f}')

    # Q_s*Rb_s = DT_s
    # Q_u*Rb_u = DT_u
    # r*Q_s=Q_u--> Q_s(Rb_s-r*Rb_u) = DT_s - DT_u
    # We can assume the same ground temperature since the boreholes were started at the same time

    difference_in_rb = (t_sep_avg - t_double_avg) / power_sep * borehole_length
    expected_value = (ratio * rb_double + difference_in_rb)
    print(f'\nDifference in Rb*: {difference_in_rb:.4f}mK/W')
    print(f'Calculated Rb double: {rb_double:.4f}mK/W')
    print(f'Expected Rb separatus: {expected_value:.4f}mK/W')

    print('\nModels\n----------------------')
    print(
        f'Rb separatus (old): {rb_sep_old:.4f} (difference: {(rb_sep_old - expected_value) / expected_value * 100:.2f}%)', )
    print(
        f'Rb separatus (new): {rb_sep_new:.4f} (difference: {(rb_sep_new - expected_value) / expected_value * 100:.2f}%)', )


def jeroen():
    print('------------------\n Case Jeroen\n------------------\n')

    # TODO WHAT IS THE GROUT?
    fluid_data = TemperatureDependentFluidData('MEG', 20).create_constant(8)
    grout = 1.4
    pipe = DoubleUTube(grout, 0.013, 0.016, 0.4, 0.035)
    pipe_new = SeparatusNew(grout)
    borehole_length = 100

    # line 842, first continuous run period
    T_inlet_double = 10.6
    T_outlet_double = 10
    T_inlet_sep = 10.1
    T_outlet_sep = 9.8
    T_avg_double = 0.5 * (T_inlet_double + T_outlet_double)
    T_avg_sep = 0.5 * (T_inlet_sep + T_outlet_sep)

    fluid_double = TemperatureDependentFluidData('MEG', 20).create_constant(T_avg_double)
    fluid_sep = TemperatureDependentFluidData('MEG', 20).create_constant(T_avg_sep)

    flow_double = 1085
    flow_sep = 956

    power_double = fluid_double.cp() * ConstantFlowRate(vfr=flow_double / 3600).mfr(fluid_data=fluid_double) * (
            T_inlet_double - T_outlet_double)
    print(f'Power double {power_double:.2f}W')
    power_sep = fluid_sep.cp() * ConstantFlowRate(vfr=flow_sep / 3600).mfr(fluid_data=fluid_sep) * (
            T_inlet_sep - T_outlet_sep)
    print(f'Power separatus {power_sep:.2f}W')

    borehole = Borehole(fluid_data, pipe, ConstantFlowRate(vfr=flow_double / 3600))
    rb_double = borehole.calculate_Rb(borehole_length, 1, (152e-3) / 2, 2, use_explicit_models=True)
    borehole = Borehole(fluid_data, pipe_new, ConstantFlowRate(vfr=flow_sep / 3600))
    rb_sep_new = borehole.calculate_Rb(borehole_length, 1, (152e-3) / 2, 2, use_explicit_models=True)
    borehole.pipe_data = Separatus(grout)
    rb_sep_old = borehole.calculate_Rb(borehole_length, 1, (152e-3) / 2, 2, use_explicit_models=True)

    print(f'Rb double: {rb_double:.4f} (difference: 0%)')
    print(f'Rb separatus (old): {rb_sep_old:.4f} (difference: {(-rb_sep_old + rb_double) / rb_double * 100:.2f}%)', )
    print(f'Rb separatus (new): {rb_sep_new:.4f} (difference: {(-rb_sep_new + rb_double) / rb_double * 100:.2f}%)', )

    print(f'Ground temperature according to double U: {T_avg_double - power_double * rb_double / 100:.2f}°C')
    print(f'Ground temperature according to separatus (old): {T_avg_sep - power_sep * rb_sep_old / 100:.2f}°C')
    print(f'Ground temperature according to separatus (new): {T_avg_sep - power_sep * rb_sep_new / 100:.2f}°C')

    sep_in = 10.1
    double_in = 10.6
    delta_t_sep = 10.1 - 9.8
    delta_t_double = 10.6 - 10.0
    t_sep_avg = 0.5 * (sep_in + sep_in - delta_t_sep)
    t_double_avg = 0.5 * (double_in + double_in - delta_t_double)
    ratio = power_double / power_sep
    print('Measurement data\n----------------------')
    print(f'Average temperature separatus: {t_sep_avg:.2f}°C')
    print(f'Average temperature double: {t_double_avg:.2f}°C')
    print(f'Difference in average temperature: {t_double_avg - t_sep_avg:.2f}°C')
    print(f'Power separatus: {power_sep:.2f}W')
    print(f'Power double U: {power_double:.2f}W')
    print(f'Power ratio: {power_double / power_sep:.2f}')

    # Q_s*Rb_s = DT_s
    # Q_u*Rb_u = DT_u
    # r*Q_s=Q_u--> Q_u(r*Rb_s-Rb_u) = DT_s - DT_u
    # We can assume the same ground temperature since the boreholes were started at the same time

    difference_in_rb = (t_sep_avg - t_double_avg) / power_sep * borehole_length
    expected_value = (rb_double * ratio + difference_in_rb)
    print(f'\nDifference in Rb*: {difference_in_rb:.4f}mK/W')
    print(f'Calculated Rb double: {rb_double:.4f}mK/W')
    print(f'Expected Rb separatus: {expected_value:.4f}mK/W')

    print('\nModels\n----------------------')
    print(
        f'Rb separatus (old): {rb_sep_old:.4f} (difference: {(rb_sep_old - expected_value) / expected_value * 100:.2f}%)', )
    print(
        f'Rb separatus (new): {rb_sep_new:.4f} (difference: {(rb_sep_new - expected_value) / expected_value * 100:.2f}%)', )

    # line 1920
    T_inlet_double = 9.1
    T_outlet_double = 7.4
    T_inlet_sep = 8.6
    T_outlet_sep = 7.4
    T_avg_double = 7.45
    T_avg_sep = 7.3

    fluid_double = TemperatureDependentFluidData('MEG', 20).create_constant(T_avg_double)
    fluid_sep = TemperatureDependentFluidData('MEG', 20).create_constant(T_avg_sep)

    flow_double = 1025
    flow_sep = 1015

    power_double = fluid_double.cp() * ConstantFlowRate(vfr=flow_double / 3600).mfr(fluid_data=fluid_double) * (
        1.3)
    print(f'Power double {power_double:.2f}W')
    power_sep = fluid_sep.cp() * ConstantFlowRate(vfr=flow_sep / 3600).mfr(fluid_data=fluid_sep) * (
        1)
    print(f'Power separatus {power_sep:.2f}W')

    borehole = Borehole(fluid_data, pipe, ConstantFlowRate(vfr=flow_double / 3600))
    rb_double = borehole.calculate_Rb(100, 1, (152e-3) / 2, 2, use_explicit_models=True)
    borehole = Borehole(fluid_data, pipe_new, ConstantFlowRate(vfr=flow_sep / 3600))
    rb_sep_new = borehole.calculate_Rb(100, 1, (152e-3) / 2, 2, use_explicit_models=True)
    borehole.pipe_data = Separatus(2)
    rb_sep_old = borehole.calculate_Rb(100, 1, (152e-3) / 2, 2, use_explicit_models=True)

    print(f'Rb double: {rb_double:.4f} (difference: 0%)')
    print(f'Rb separatus (old): {rb_sep_old:.4f} (difference: {(-rb_sep_old + rb_double) / rb_double * 100:.2f}%)', )
    print(f'Rb separatus (new): {rb_sep_new:.4f} (difference: {(-rb_sep_new + rb_double) / rb_double * 100:.2f}%)', )

    print(f'Ground temperature according to double U: {T_avg_double - power_double * rb_double / 100:.2f}°C')
    print(f'Ground temperature according to separatus (old): {T_avg_sep - power_sep * rb_sep_old / 100:.2f}°C')
    print(f'Ground temperature according to separatus (new): {T_avg_sep - power_sep * rb_sep_new / 100:.2f}°C')

    sep_in = 8.6
    double_in = 9.1
    delta_t_sep = 8.6 - 7.4
    delta_t_double = 9.1 - 7.4
    t_sep_avg = 0.5 * (sep_in + sep_in - delta_t_sep)
    t_double_avg = 0.5 * (double_in + double_in - delta_t_double)
    ratio = power_double / power_sep
    print('Measurement data\n----------------------')
    print(f'Average temperature separatus: {t_sep_avg:.2f}°C')
    print(f'Average temperature double: {t_double_avg:.2f}°C')
    print(f'Difference in average temperature: {t_double_avg - t_sep_avg:.2f}°C')
    print(f'Power separatus: {power_sep:.2f}W')
    print(f'Power double U: {power_double:.2f}W')
    print(f'Power ratio: {power_double / power_sep:.2f}')

    # Q_s*Rb_s = DT_s
    # Q_u*Rb_u = DT_u
    # r*Q_s=Q_u--> Q_u(r*Rb_s-Rb_u) = DT_s - DT_u
    # We can assume the same ground temperature since the boreholes were started at the same time

    difference_in_rb = (t_sep_avg - t_double_avg) / power_sep * borehole_length
    expected_value = (rb_double * ratio + difference_in_rb)
    print(f'\nDifference in Rb*: {difference_in_rb:.4f}mK/W')
    print(f'Calculated Rb double: {rb_double:.4f}mK/W')
    print(f'Expected Rb separatus: {expected_value:.4f}mK/W')

    print('\nModels\n----------------------')
    print(
        f'Rb separatus (old): {rb_sep_old:.4f} (difference: {(rb_sep_old - expected_value) / expected_value * 100:.2f}%)', )
    print(
        f'Rb separatus (new): {rb_sep_new:.4f} (difference: {(rb_sep_new - expected_value) / expected_value * 100:.2f}%)', )


def pertner():
    print('------------------\n Case Pertner\n------------------\n')

    fluid_data = TemperatureDependentFluidData('MEG', 25).create_constant(3)
    pipe = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    pipe_new = SeparatusNew(1.5)

    # # line 674,95 min
    # borehole = Borehole(fluid_data, pipe, ConstantFlowRate(vfr=0.19))
    # rb_double = borehole.calculate_Rb(70, 1, (130e-3) / 2, 1.5, use_explicit_models=True)
    # borehole = Borehole(fluid_data, pipe_new, ConstantFlowRate(vfr=0.195))
    # rb_sep_new = borehole.calculate_Rb(70, 1, (130e-3) / 2, 1.5, use_explicit_models=True)
    # borehole.pipe_data = Separatus(2)
    # rb_sep_old = borehole.calculate_Rb(70, 1, (130e-3) / 2, 1.5, use_explicit_models=True)
    #
    # print(f'Rb double: {rb_double:.4f}')
    # print(f'Rb separatus (old): {rb_sep_old:.4f}', )
    # print(f'Rb separatus (new): {rb_sep_new:.4f}', )
    #
    # # power
    # power_sep = 993
    # power_double = 1396
    # # separatus slightly worse --> greater difference between borehole wall and fluid
    # # temperature identical with double U --> double U already somewhat colder --> ok!
    #
    # temp_diff_double = power_double * rb_double / 70
    # temp_diff_sep_old = power_sep * rb_sep_old / 70
    # temp_diff_sep_new = power_sep * rb_sep_new / 70
    # print(f'Temperature difference fluid-ground double: {temp_diff_double:.2f}°C')
    # print(f'Temperature difference fluid-ground separatus (old): {temp_diff_sep_old:.2f}°C')
    # print(f'Temperature difference fluid-ground separatus (new): {temp_diff_sep_new:.2f}°C')
    #
    # T_inlet = 1.91
    # T_out_sep = 3.53
    # T_out_double = 3.31
    # T_sep_avg = 0.5 * (276.5392 + 277.8393) - 273.15
    # T_double_avg = 0.5 * (276.4848 + 278.3507) - 273.15
    # estimated_ground_double = temp_diff_double - T_double_avg
    #
    # print(f'Estimated ground temperature double: {temp_diff_double - T_double_avg:.2f}°C')
    # print(f'Estimated ground temperature separatus (old): {temp_diff_sep_old - T_sep_avg:.2f}°C')
    # print(f'Estimated ground temperature separatus (new): {temp_diff_sep_new - T_sep_avg:.2f}°C')
    # print(f'Estimated borehole resistance based on power {power_double / power_sep * rb_double:.4f}mK/W')

    borehole_length = 70

    borehole = Borehole(fluid_data, pipe, ConstantFlowRate(vfr=550 / 3600))
    rb_double = borehole.calculate_Rb(borehole_length, 1, (130e-3) / 2, 1.5, use_explicit_models=True)
    borehole = Borehole(fluid_data, pipe_new, ConstantFlowRate(vfr=1400 / 3600))
    rb_sep_new = borehole.calculate_Rb(borehole_length, 1, (130e-3) / 2, 1.5, use_explicit_models=True)
    borehole.pipe_data = Separatus(2)
    rb_sep_old = borehole.calculate_Rb(borehole_length, 1, (130e-3) / 2, 1.5, use_explicit_models=True)

    # from slide, data 2024-01-25 02:00-05:00
    sep_in = 4
    double_in = 5.5
    delta_t_sep = 1
    delta_t_double = 2.3
    t_sep_avg = 0.5 * (sep_in + sep_in - delta_t_sep)
    t_double_avg = 0.5 * (double_in + double_in - delta_t_double)
    power = 1500
    print('Measurement data\n----------------------')
    print(f'Average temperature separatus: {t_sep_avg:.2f}°C')
    print(f'Average temperature double: {t_double_avg:.2f}°C')
    print(f'Difference in average temperature: {t_double_avg - t_sep_avg:.2f}°C')
    print(f'Power: {power:.0f}W')

    # Q_s*Rb_s = DT_s
    # Q_u*Rb_u = DT_u
    # Q_s=Q_u--> Q_s(Rb_s-Rb_u) = DT_s - DT_u
    # We can assume the same ground temperature since the boreholes were started at the same time

    difference_in_rb = (t_double_avg - t_sep_avg) / power * borehole_length
    expected_value = rb_double + difference_in_rb
    print(f'\nDifference in Rb*: {difference_in_rb:.4f}mK/W')
    print(f'Calculated Rb double: {rb_double:.4f}mK/W')
    print(f'Expected Rb separatus: {expected_value:.4f}mK/W')

    print('\nModels\n----------------------')
    print(
        f'Rb separatus (old): {rb_sep_old:.4f} (difference: {(rb_sep_old - expected_value) / expected_value * 100:.2f}%)', )
    print(
        f'Rb separatus (new): {rb_sep_new:.4f} (difference: {(rb_sep_new - expected_value) / expected_value * 100:.2f}%)', )

    # Fitted the wrong model, assumed that Q_s*Rb_s = Q_u*Rb_u, which is not the case.
    # The ground temperature is identical, the others not


if __name__ == "__main__":
    # borehole_resistance_ifo_reynolds()
    # subresistances()
    # figure_Re()
    # numerical()
    # figure_1()
    # depth()
    explicit_single_U()
    # TRT_brudrill()  # finished
    # TRT_davos()  # finished
    # alge()  # not finished
    # jeroen()  # not up to date with powerpoint
    # pertner()  # finished
