from GHEtool import Borefield
import pygfunction as gt
import optuna


def optimise_borefield_configuration(
        borefield: Borefield,
        l_1_max: float,
        l_2_max: float,
        b_min: float,
        b_max: float,
        b_step: float,
        h_min: float,
        h_max: float):
    def f(n_1, n_2, b_1, b_2, h_min, h_max, max_value):
        borefield.create_rectangular_borefield(n_1, n_2, b_1, b_2, 100, borefield.D, borefield.r_b)
        try:
            depth = borefield.size_L3()
            if h_min <= depth <= h_max:
                return depth * n_1 * n_2
            return max_value * 2
        except:
            return max_value * 2

    def objective(trial: optuna.Trial):
        max_value = int(l_1_max / b_min) * int(l_2_max / b_min) * h_max

        # Suggest b_1 first and calculate the max possible n_1 value
        b_1 = trial.suggest_float('b_1', b_min, b_max, step=b_step)
        max_n_1 = int(l_1_max / b_1)  # Ensure n_1 * b_1 < l_1_max
        n_1 = trial.suggest_int('n_1', 1, max_n_1)

        # Suggest parameters for n_2 and b_2 similarly
        b_2 = trial.suggest_float('b_2', b_min, b_max, step=b_step)
        max_n_2 = int(l_2_max / b_2)  # Ensure n_2 * b_2 < l_2_max
        n_2 = trial.suggest_int('n_2', 1, max_n_2)

        return f(n_1, n_2, b_1, b_2, h_min, h_max, max_value)

    study = optuna.create_study()
    study.optimize(objective, n_trials=100)
    params, total_borehole_length = study.best_trials[0].params, study.best_trials[0].value
    return gt.borefield.Borefield.rectangle_field(params['n_1'], params['n_2'], params['b_1'], params['b_2'],
                                                  total_borehole_length / params['n_1'] / params['n_2'], borefield.D,
                                                  borefield.r_b)
