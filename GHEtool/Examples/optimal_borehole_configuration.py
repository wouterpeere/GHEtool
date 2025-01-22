from GHEtool import *
from GHEtool.Methods import optimise_borefield_configuration
import optuna

ground_data = GroundFluxTemperature(3, 10)
fluid_data = FluidData(0.2, 0.568, 998, 4180, 1e-3)
pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)

borefield = Borefield()
borefield.create_rectangular_borefield(5, 4, 6, 6, 110, 4, 0.075)
borefield.set_ground_parameters(ground_data)
borefield.set_fluid_parameters(fluid_data)
borefield.set_pipe_parameters(pipe_data)
borefield.calculation_setup(use_constant_Rb=False)
borefield.set_max_avg_fluid_temperature(17)
borefield.set_min_avg_fluid_temperature(3)
hourly_load = HourlyGeothermalLoad()
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\swimming_pool.csv"), header=True,
                                separator=";",
                                col_injection=0, col_extraction=1)
borefield.load = hourly_load

optimal_configuration = optimise_borefield_configuration(borefield, 200, 200, 2, 10, 0.5, 50, 350)
borefield.borefield = optimal_configuration

borefield.print_temperature_profile()
