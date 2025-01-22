from GHEtool import *
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
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\office.csv"), header=True, separator=";",
                                col_injection=0, col_extraction=1)
borefield.load = hourly_load


def f(n_1, n_2, b):
    MAX_VALUE = 20 * 20 * 1000
    borefield.create_rectangular_borefield(n_1, n_2, b, b, 100, 0.75, 0.7)
    try:
        depth = borefield.size_L2()
        if 50 <= depth <= 150:
            return depth * n_1 * n_2
        return MAX_VALUE
    except:
        return MAX_VALUE


def objective(trial: optuna.Trial):
    n_1 = trial.suggest_int('n_1', 1, 12)
    n_2 = trial.suggest_int('n_2', 1, 12)
    b = trial.suggest_float('b_1', 2, 10, step=0.5)
    # length = trial.suggest_float('length', 50, 150)
    return f(n_1, n_2, b)


study = optuna.create_study()
study.optimize(objective, n_trials=1000)
