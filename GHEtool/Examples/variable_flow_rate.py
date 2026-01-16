import copy

from matplotlib import pyplot as plt

from GHEtool import *


def sizing():
    """
    This function compares the sizing (L2, L3 and L4) of a constant flow rate with a variable one.

    Returns
    -------
    None
    """
    # define params
    ground_data = GroundFluxTemperature(2.1, 10, flux=0.06)
    pipe = SingleUTube(2, 0.013, 0.016, 0.4, 0.035)
    fluid = TemperatureDependentFluidData('MPG', 25)

    load = HourlyBuildingLoad(efficiency_heating=5, efficiency_cooling=20)
    load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\office.csv"), header=True,
                             separator=";", col_cooling=0, col_heating=1)

    # define two flow rates
    flow_var = ConstantDeltaTFlowRate(delta_temp_extraction=4, injection_time=4)
    flow = flow_var.mfr_borefield(fluid, load.max_peak_injection, temperature=25)
    # set constant flow to the same maximum flow rate as the variable one
    flow_constant = ConstantFlowRate(mfr=flow, flow_per_borehole=False)

    # define borefield with constant flow
    borefield_constant_flow = Borefield(load=load, ground_data=ground_data, fluid_data=fluid, flow_data=flow_constant,
                                        pipe_data=pipe)
    borefield_constant_flow.set_min_fluid_temperature(2)
    borefield_constant_flow.set_max_fluid_temperature(25)
    borefield_constant_flow.create_rectangular_borefield(10, 8, 6, 6, 150, 1)

    # define borefield with variable flow
    borefield_variable_flow = copy.deepcopy(borefield_constant_flow)
    borefield_variable_flow.flow_data = flow_var

    # calculate required borefield size
    constant_depth_L4 = borefield_constant_flow.size_L4()
    variable_depth_L4 = borefield_variable_flow.size_L4()
    print(f'Required borehole depth for a constant flow: {constant_depth_L4:.2f} (L4)')
    print(f'Required borehole depth for a variable flow: {variable_depth_L4:.2f} (L4) '
          f'(difference of {(variable_depth_L4 - constant_depth_L4) / constant_depth_L4 * 100:.2f}%)')
    constant_depth_L3 = borefield_constant_flow.size_L3()
    variable_depth_L3 = borefield_variable_flow.size_L3()
    print(f'Required borehole depth for a constant flow: {constant_depth_L3:.2f} (L3)')
    print(f'Required borehole depth for a variable flow: {variable_depth_L3:.2f} (L3) '
          f'(difference of {(variable_depth_L3 - constant_depth_L3) / constant_depth_L3 * 100:.2f}%)')

    borefield_constant_flow.calculation_setup(size_based_on='outlet')
    borefield_variable_flow.calculation_setup(size_based_on='outlet')
    constant_depth_L3 = borefield_constant_flow.size_L3()
    variable_depth_L3 = borefield_variable_flow.size_L3()
    print(f'Required borehole depth for a constant flow: {constant_depth_L3:.2f} (L3)')
    print(f'Required borehole depth for a variable flow: {variable_depth_L3:.2f} (L3) '
          f'(difference of {(variable_depth_L3 - constant_depth_L3) / constant_depth_L3 * 100:.2f}%)')
    borefield_constant_flow.print_temperature_profile(plot_hourly=True)
    borefield_variable_flow.calculate_temperatures(hourly=True)

    rb_constant_flow = borefield_constant_flow.borehole.get_Rb(constant_depth_L4, 1, 0.075, 2.1,
                                                               temperature=borefield_constant_flow.results.peak_injection,
                                                               use_explicit_models=True,
                                                               nb_of_boreholes=borefield_constant_flow.number_of_boreholes)
    rb_variable_flow = borefield_variable_flow.borehole.get_Rb(variable_depth_L4, 1, 0.075, 2.1,
                                                               temperature=borefield_variable_flow.results.peak_injection,
                                                               power=load.hourly_net_resulting_injection_power,
                                                               nb_of_boreholes=borefield_constant_flow.number_of_boreholes,
                                                               use_explicit_models=True)

    time_array = borefield_variable_flow.load.time_L4 / 12 / 3600 / 730

    plt.figure()
    plt.plot(time_array, borefield_variable_flow.results.peak_injection, label='variable flow')
    plt.plot(time_array, borefield_constant_flow.results.peak_injection, label='constant flow')
    plt.legend()
    plt.ylabel('Average fluid temperature [°C]')
    plt.xlabel('Time [years]')

    plt.figure()
    plt.plot(time_array, rb_variable_flow, label='variable flow')
    plt.plot(time_array, rb_constant_flow, label='constant flow')
    plt.ylabel('Effective borehole thermal resistance [mK/W]')
    plt.xlabel('Time [years]')
    plt.legend()
    plt.show()


if __name__ == "__main__":
    sizing()
