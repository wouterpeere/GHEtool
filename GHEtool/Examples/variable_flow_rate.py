import copy

from GHEtool import *

ground_data = GroundFluxTemperature(2.1, 10, flux=0.06)
pipe = SingleUTube(2, 0.013, 0.016, 0.4, 0.035)
fluid = TemperatureDependentFluidData('MPG', 25)
flow_constant = ConstantFlowRate(mfr=536 / 16, flow_per_borehole=False)
flow_var = ConstantDeltaTFlowRate(delta_temp_extraction=4, injection_time=4)
load = HourlyBuildingLoad(efficiency_heating=5, efficiency_cooling=20)
load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\hourly_profile.csv"), header=True,
                         separator=";", col_cooling=1, col_heating=0)
borefield_constant_flow = Borefield(load=load, ground_data=ground_data, fluid_data=fluid, flow_data=flow_constant,
                                    pipe_data=pipe)

borefield_constant_flow.set_min_fluid_temperature(3)
borefield_constant_flow.set_max_fluid_temperature(18)
borefield_constant_flow.create_rectangular_borefield(12, 20, 6, 6, 150, 1)
print(borefield_constant_flow.size_L4())
# borefield_constant_flow.print_temperature_profile(plot_hourly=True)

borefield_variable_flow = copy.deepcopy(borefield_constant_flow)
borefield_variable_flow.flow_data = flow_var
print(borefield_variable_flow.size_L4())

rb_constant_flow = borefield_constant_flow.borehole.get_Rb(150, 1, 0.075, 2.1,
                                                           temperature=borefield_constant_flow.results.peak_injection,
                                                           use_explicit_models=True,
                                                           nb_of_boreholes=200)
rb_variable_flow = borefield_variable_flow.borehole.get_Rb(150, 1, 0.075, 2.1,
                                                           temperature=borefield_variable_flow.results.peak_injection,
                                                           power=load.hourly_net_resulting_injection_power,
                                                           nb_of_boreholes=200,
                                                           use_explicit_models=True)
plt.figure()
plt.plot(borefield_variable_flow.results.peak_injection, label='variable flow')
plt.plot(borefield_constant_flow.results.peak_injection, label='constant flow')

plt.legend()
plt.show()
plt.figure()
plt.plot(flow_var.mfr_borefield(fluid, power=load.hourly_net_resulting_injection_power,
                                temperature=borefield_constant_flow.results.peak_injection))
plt.figure()
plt.plot(rb_variable_flow, label='variable flow')
plt.plot(rb_constant_flow, label='constant flow')

plt.legend()
plt.show()
