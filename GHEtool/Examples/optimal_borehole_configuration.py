from GHEtool import *
from GHEtool.Methods import optimise_borefield_configuration, brute_force_config
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

# run optimisation with neural network
borefield.calculation_setup(use_neural_network=True)
import time

start = time.time()
borefield_ann_opt = optimise_borefield_configuration(borefield, 40, 40, 4, 6, 0.5, 50, 200)
time_ann_opt = time.time() - start
start = time.time()
borefield_ann_brute_force = brute_force_config(borefield, 40, 40, 4, 6, 0.5, 50, 200)
time_ann_bf = time.time() - start
start = time.time()

# run optimisation without neural network
borefield.calculation_setup(use_neural_network=False)
borefield_reg_opt = optimise_borefield_configuration(borefield, 40, 40, 4, 6, 0.5, 50, 200)
time_reg_opt = time.time() - start
start = time.time()
borefield_reg_brute_force = brute_force_config(borefield, 40, 40, 4, 6, 0.5, 50, 200)
time_reg_bf = time.time() - start
print(
    f'Total borehole length ANN optimisation {(borefield_ann_opt.nBoreholes * borefield_ann_opt.H[0]):.2f} m on {time_ann_opt}s')
print(
    f'Total borehole length ANN BF {(borefield_ann_brute_force.nBoreholes * borefield_ann_brute_force.H[0]):.2f} mon {time_ann_bf}s')
print(
    f'Total borehole length reg optimisation {(borefield_reg_opt.nBoreholes * borefield_reg_opt.H[0]):.2f} mon {time_reg_opt}s')
print(
    f'Total borehole length reg BF {(borefield_reg_brute_force.nBoreholes * borefield_reg_brute_force.H[0]):.2f} mon {time_reg_bf}s')

borefield_reg_opt.print_temperature_profile()
