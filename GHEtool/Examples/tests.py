from GHEtool import *

fluid = TemperatureDependentFluidData('MPG', 25, mass_percentage=False).create_constant(3)
flow = ConstantFlowRate(mfr=0.4)
print(fluid.rho(), fluid.cp(), flow.vfr(fluid))

dn40 = SingleUTube(1, 0.0163, 0.02, 0.4, 0.035)

borehole = Borehole(fluid, dn40, flow)
print(dn40.calculate_convective_resistance(flow, fluid), dn40.calculate_conductive_resistance(), dn40.Re(fluid, flow))
dn16 = SingleUTube(1, 0.016 / 2 - 1.5e-3, 0.016 / 2, 0.4, 0.035)
print(dn16.calculate_convective_resistance(ConstantFlowRate(mfr=0.4 / 10), fluid),
      dn16.calculate_conductive_resistance(), dn16.Re(fluid, ConstantFlowRate(mfr=0.4 / 10)))

ground_data = GroundFluxTemperature(3, 10)
fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
flow_data = ConstantFlowRate(mfr=0.2)
pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
borefield = Borefield()
borefield.create_rectangular_borefield(5, 4, 6, 6, 110, 4, 0.075)
borefield.ground_data = ground_data
borefield.fluid_data = fluid_data
borefield.flow_data = flow_data
borefield.pipe_data = pipe_data
borefield.calculation_setup(use_constant_Rb=False)
borefield.set_max_fluid_temperature(17)
borefield.set_min_fluid_temperature(3)
hourly_load = HourlyGeothermalLoad()

hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True, separator=";",
                                col_injection=0, col_extraction=1)
borefield.load = hourly_load

borefield.set_max_fluid_temperature(19)
borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)

borefield.fluid_data = TemperatureDependentFluidData('MPG', 25)
borefield.flow_data = VariableHourlyFlowRate(mfr=np.full(8760, 0.2))
borefield.size_L4()
borefield.print_temperature_profile(plot_hourly=True)
