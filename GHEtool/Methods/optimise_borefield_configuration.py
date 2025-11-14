import numpy as np

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
        h_max: float,
        nb_of_trials: int = 100):
    def f(n_1, n_2, b_1, b_2, h_min, h_max, max_value):
        borefield.create_rectangular_borefield(n_1, n_2, b_1, b_2, 100, borefield.D, borefield.r_b)
        try:
            depth = borefield.size_L3()
            if h_min <= depth <= h_max:
                return depth * borefield.number_of_boreholes
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
    study.optimize(objective, n_trials=nb_of_trials)
    params, total_borehole_length = study.best_trials[0].params, study.best_trials[0].value
    return gt.borefield.Borefield.rectangle_field(params['n_1'], params['n_2'], params['b_1'], params['b_2'],
                                                  total_borehole_length / params['n_1'] / params['n_2'], borefield.D,
                                                  borefield.r_b)


def optimise_borefield_configuration_config(
        borefield: Borefield,
        l_1_max: float,
        l_2_max: float,
        b_min: float,
        b_max: float,
        b_step: float,
        h_min: float,
        h_max: float,
        nb_of_trials: int = 100,
        types: list = [0, 1, 2, 3, 4]):
    def f(n_1, n_2, b_1, b_2, h_min, h_max, max_value, shape):

        if shape < 1:
            borefield.borefield = gt.borefield.Borefield.L_shaped_field(n_1, n_2, b_1, b_2, 100, borefield.D,
                                                                        borefield.r_b)
        elif shape < 2:
            borefield.borefield = gt.borefield.Borefield.U_shaped_field(n_1, n_2, b_1, b_2, 100, borefield.D,
                                                                        borefield.r_b)
        elif shape < 3:
            borefield.borefield = gt.borefield.Borefield.box_shaped_field(n_1, n_2, b_1, b_2, 100, borefield.D,
                                                                          borefield.r_b)
        elif shape < 4:
            borefield.borefield = gt.borefield.Borefield.rectangle_field(n_1, n_2, b_1, b_2, 100, borefield.D,
                                                                         borefield.r_b)
        else:
            borefield.borefield = gt.borefield.Borefield.staggered_rectangle_field(n_1, n_2, b_1, b_2, 100, borefield.D,
                                                                                   borefield.r_b, False)
        try:
            depth = borefield.size_L3()
            if h_min <= depth <= h_max:
                return depth * borefield.number_of_boreholes
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

        return f(n_1, n_2, b_1, b_2, h_min, h_max, max_value, shape)

    params_shape = {}
    for shape in types:
        study = optuna.create_study()
        study.optimize(objective, n_trials=nb_of_trials)
        params, total_borehole_length = study.best_trials[0].params, study.best_trials[0].value
        params_shape[shape] = (params, total_borehole_length)
    print(params_shape)
    # return optimised field
    # if params['shape'] < 1:
    #     return gt.borefield.Borefield.L_shaped_field(params['n_1'], params['n_2'], params['b_1'], params['b_2'],
    #                                                  total_borehole_length / params['n_1'] / params['n_2'], borefield.D,
    #                                                  borefield.r_b)
    # elif params['shape'] < 2:
    #     return gt.borefield.Borefield.U_shaped_field(params['n_1'], params['n_2'], params['b_1'], params['b_2'],
    #                                                  total_borehole_length / params['n_1'] / params['n_2'], borefield.D,
    #                                                  borefield.r_b)
    # elif params['shape'] < 3:
    #     return gt.borefield.Borefield.box_shaped_field(params['n_1'], params['n_2'], params['b_1'], params['b_2'],
    #                                                    total_borehole_length / params['n_1'] / params['n_2'],
    #                                                    borefield.D, borefield.r_b)
    # elif params['shape'] < 4:
    #     return gt.borefield.Borefield.rectangle_field(params['n_1'], params['n_2'], params['b_1'], params['b_2'],
    #                                                   total_borehole_length / params['n_1'] / params['n_2'],
    #                                                   borefield.D, borefield.r_b)
    # else:
    #     return gt.borefield.Borefield.staggered_rectangle_field(params['n_1'], params['n_2'], params['b_1'],
    #                                                             params['b_2'],
    #                                                             total_borehole_length / params['n_1'] / params['n_2'],
    #                                                             borefield.D, borefield.r_b, False)


def optimise_borefield_configuration_config_all_in_once(
        borefield: Borefield,
        l_1_max: float,
        l_2_max: float,
        b_min: float,
        b_max: float,
        b_step: float,
        h_min: float,
        h_max: float,
        nb_of_trials: int = 100,
        types: list = [0, 1, 2, 3, 4]):
    def f(n_1, n_2, b_1, b_2, h_min, h_max, max_value, shape):

        if shape < 1:
            borefield.borefield = gt.borefield.Borefield.L_shaped_field(n_1, n_2, b_1, b_2, 100, borefield.D,
                                                                        borefield.r_b)
        elif shape < 2:
            borefield.borefield = gt.borefield.Borefield.U_shaped_field(n_1, n_2, b_1, b_2, 100, borefield.D,
                                                                        borefield.r_b)
        elif shape < 3:
            borefield.borefield = gt.borefield.Borefield.box_shaped_field(n_1, n_2, b_1, b_2, 100, borefield.D,
                                                                          borefield.r_b)
        elif shape < 4:
            borefield.borefield = gt.borefield.Borefield.rectangle_field(n_1, n_2, b_1, b_2, 100, borefield.D,
                                                                         borefield.r_b)
        else:
            borefield.borefield = gt.borefield.Borefield.staggered_rectangle_field(n_1, n_2, b_1, b_2, 100, borefield.D,
                                                                                   borefield.r_b, False)
        try:
            depth = borefield.size_L3()
            if h_min <= depth <= h_max:
                return depth * borefield.number_of_boreholes
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
        shape = trial.suggest_categorical('shape', types)
        return f(n_1, n_2, b_1, b_2, h_min, h_max, max_value, shape)

    study = optuna.create_study()
    study.optimize(objective, n_trials=nb_of_trials)
    params, total_borehole_length = study.best_trials[0].params, study.best_trials[0].value
    results = []

    seen_params = set()
    seen_values = set()

    for trial in study.trials:
        if trial.values is None:
            continue

        val = trial.values[0]
        params = trial.params

        # make hashable, order independent
        params_key = tuple(sorted(params.items()))

        # keep only if both value and params are new
        if params_key not in seen_params and val not in seen_values:
            seen_params.add(params_key)
            seen_values.add(val)
            results.append((val, params))

    # Optional: sort by objective value
    results.sort(key=lambda x: x[0])

    def find_borefield(params):
        # return optimised field
        if params['shape'] < 1:
            return gt.borefield.Borefield.L_shaped_field(params['n_1'], params['n_2'], params['b_1'], params['b_2'],
                                                         total_borehole_length / params['n_1'] / params['n_2'],
                                                         borefield.D,
                                                         borefield.r_b)
        elif params['shape'] < 2:
            return gt.borefield.Borefield.U_shaped_field(params['n_1'], params['n_2'], params['b_1'], params['b_2'],
                                                         total_borehole_length / params['n_1'] / params['n_2'],
                                                         borefield.D,
                                                         borefield.r_b)
        elif params['shape'] < 3:
            return gt.borefield.Borefield.box_shaped_field(params['n_1'], params['n_2'], params['b_1'], params['b_2'],
                                                           total_borehole_length / params['n_1'] / params['n_2'],
                                                           borefield.D, borefield.r_b)
        elif params['shape'] < 4:
            return gt.borefield.Borefield.rectangle_field(params['n_1'], params['n_2'], params['b_1'], params['b_2'],
                                                          total_borehole_length / params['n_1'] / params['n_2'],
                                                          borefield.D, borefield.r_b)
        else:
            return gt.borefield.Borefield.staggered_rectangle_field(params['n_1'], params['n_2'], params['b_1'],
                                                                    params['b_2'],
                                                                    total_borehole_length / params['n_1'] / params[
                                                                        'n_2'],
                                                                    borefield.D, borefield.r_b, False)

    return [(i[0], i[1], find_borefield(i[1])) for i in results]


def brute_force_config(
        borefield: Borefield,
        l_1_max: float,
        l_2_max: float,
        b_min: float,
        b_max: float,
        b_step: float,
        h_min: float,
        h_max: float
):
    length = 10 ** 8
    data = []
    for b_1 in np.arange(b_min, b_max + 0.1, b_step):
        for b_2 in np.arange(b_min, b_max + 0.1, b_step):
            for n_1 in range(1, int(l_1_max / b_1) + 1):
                for n_2 in range(1, int(l_2_max / b_2) + 1):
                    print(n_1, n_2, b_1, b_2)

                    try:
                        borefield.create_rectangular_borefield(n_1, n_2, b_1, b_2, 100, borefield.D, borefield.r_b)
                        depth = borefield.size_L3()
                        if h_min <= depth <= h_max:
                            length = min(depth * n_1 * n_2, length)
                            if length == depth * n_1 * n_2:
                                data = [n_1, n_2, b_1, b_2, depth]
                        # else:
                        #     print(n_1, n_2, b_1, b_2, depth)
                    except:
                        pass
                        # print(n_1, n_2, b_1, b_2)
    return gt.borefield.Borefield.rectangle_field(*data, borefield.D, borefield.r_b)
