from GHEtool import *
from GHEtool.Methods import optimise_borefield_configuration
from GHEtool.Validation.cases import load_case

ground_data = GroundFluxTemperature(2.5, 10)
fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)

borefield = Borefield()
borefield.create_rectangular_borefield(5, 4, 6, 6, 110, 0.7, 0.075)
borefield.ground_data = ground_data
borefield.fluid_data = fluid_data
borefield.pipe_data = pipe_data
borefield.calculation_setup(use_constant_Rb=False)
borefield.set_max_avg_fluid_temperature(17)
borefield.set_min_avg_fluid_temperature(3)
borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(1))
borefield.calculation_setup(use_neural_network=True)
optimal_configuration = optimise_borefield_configuration(borefield, 40, 40, 4, 6, 0.5, 50, 200)
borefield.borefield = optimal_configuration
borefield.calculation_setup(use_neural_network=False)

borefield.print_temperature_profile()
