from GHEtool import *

from GHEtool.Validation.cases import load_case

# load data
fluid_data = TemperatureDependentFluidData('MPG', 25)
flow_data = ConstantFlowRate(vfr=0.3)
pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
ground_data = GroundFluxTemperature(2, 9.8)

borefield = Borefield(
    ground_data=ground_data,
    flow_data=flow_data,
    fluid_data=fluid_data,
    pipe_data=pipe_data,
    load=MonthlyBuildingLoadAbsolute(*load_case(4))
)

borefield.set_min_avg_fluid_temperature(2)
borefield.set_max_avg_fluid_temperature(17)

borefield.create_rectangular_borefield(12, 5, 6, 6, 150)

# calculate required size with variable temperature
size_variable = borefield.size_L3()

# calculate required size with fixed temperature
borefield.fluid_data = fluid_data.create_constant(2)
size_fixed = borefield.size_L3()

borefield.print_temperature_profile()
