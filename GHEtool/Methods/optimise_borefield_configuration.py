import numpy as np

from GHEtool import Borefield
from GHEtool.VariableClasses.BaseClass import UnsolvableOptimalFieldError
import pygfunction as gt
import optuna

optuna.logging.disable_default_handler()


def optimise_borefield_configuration_config(
        borefield: Borefield,
        l_1_max: float,
        l_2_max: float,
        b_min: float,
        b_max: float,
        b_step: float,
        h_min: float,
        h_max: float,
        nb_min: int = 1,
        nb_max: int = 999,
        nb_of_trials: int = 100,
        types: list = [0, 1, 2, 3, 4],
        size_L3: bool = True):
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
            if size_L3:
                depth = borefield.size_L3()
            else:
                depth = borefield.size_L4()
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
        nb_min: int = 1,
        nb_max: int = 999,
        nb_of_trials: int = 100,
        types: list = [0, 1, 2, 3, 4],
        size_L3: bool = True,
        optimise: str = 'length'):
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
            if borefield.number_of_boreholes < nb_min or borefield.number_of_boreholes > nb_max:
                return max_value * 2, max_value * 2
            if size_L3:
                depth = borefield.size_L3()
            else:
                depth = borefield.size_L4()
            if h_min <= depth <= h_max:
                return depth * borefield.number_of_boreholes, borefield.number_of_boreholes
            return max_value * 2, max_value * 2
        except:
            return max_value * 2, max_value * 2

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

        total_length, number = f(n_1, n_2, b_1, b_2, h_min, h_max, max_value, shape)
        trial.set_user_attr("n_boreholes", number)
        trial.set_user_attr("total_length", total_length)
        return total_length if optimise == 'length' else number

    study = optuna.create_study()
    study.optimize(objective, n_trials=nb_of_trials)
    results = []

    seen_params = set()
    seen_values = set()

    for trial in study.trials:
        if trial.values is None:
            continue

        val = trial.values[0]
        params = trial.params
        total_length = trial.user_attrs.get('total_length')
        n_boreholes = trial.user_attrs.get('n_boreholes')

        # make hashable, order independent
        params_key = tuple(sorted(params.items()))

        # keep only if both value and params are new
        if params_key not in seen_params and (n_boreholes, total_length) not in seen_values:
            seen_params.add(params_key)
            seen_values.add((n_boreholes, total_length))
            results.append((total_length, params, n_boreholes if n_boreholes is not None else n_boreholes))

    if optimise == 'length':
        # x = (objective_value, params, total_length, n_boreholes)
        results.sort(key=lambda x: (x[0], x[2]))
    else:
        results.sort(key=lambda x: (x[2], x[0]))

    def find_borefield(params, total_borehole_length):
        # return optimised field
        if params['shape'] < 1:
            temp = gt.borefield.Borefield.L_shaped_field(params['n_1'], params['n_2'], params['b_1'], params['b_2'],
                                                         total_borehole_length, borefield.D, borefield.r_b)
            temp.H = total_borehole_length / temp.nBoreholes
            return temp
        elif params['shape'] < 2:
            temp = gt.borefield.Borefield.U_shaped_field(params['n_1'], params['n_2'], params['b_1'], params['b_2'],
                                                         total_borehole_length, borefield.D, borefield.r_b)
            temp.H = total_borehole_length / temp.nBoreholes
            return temp
        elif params['shape'] < 3:
            temp = gt.borefield.Borefield.box_shaped_field(params['n_1'], params['n_2'], params['b_1'], params['b_2'],
                                                           total_borehole_length, borefield.D, borefield.r_b)
            temp.H = total_borehole_length / temp.nBoreholes
            return temp
        elif params['shape'] < 4:
            temp = gt.borefield.Borefield.rectangle_field(params['n_1'], params['n_2'], params['b_1'], params['b_2'],
                                                          total_borehole_length, borefield.D, borefield.r_b)
            temp.H = total_borehole_length / temp.nBoreholes
            return temp
        else:
            temp = gt.borefield.Borefield.staggered_rectangle_field(params['n_1'], params['n_2'], params['b_1'],
                                                                    params['b_2'], total_borehole_length, borefield.D,
                                                                    borefield.r_b, False)
            temp.H = total_borehole_length / temp.nBoreholes
            return temp

    max_value = int(l_1_max / b_min) * int(l_2_max / b_min) * h_max
    if results[0][0] == max_value * 2:
        # no solution is found
        raise UnsolvableOptimalFieldError

    return [(i[0], i[1], i[2], find_borefield(i[1], i[0])) for i in results]


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
