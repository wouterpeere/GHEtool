"""
This file contains the code for the optimisation function of the borefield configuration.
"""
import copy

import numpy as np

from GHEtool import Borefield
from GHEtool.VariableClasses.BaseClass import UnsolvableOptimalFieldError
from GHEtool.VariableClasses.FlowData import *
import pygfunction as gt
import optuna

optuna.logging.disable_default_handler()


def _find_borefield(borefield, n_1, n_2, b_1, b_2, shape) -> gt.borefield.Borefield:
    if shape < 1:
        return gt.borefield.Borefield.L_shaped_field(n_1, n_2, b_1, b_2, 100, borefield.D, borefield.r_b)
    elif shape < 2:
        return gt.borefield.Borefield.U_shaped_field(n_1, n_2, b_1, b_2, 100, borefield.D, borefield.r_b)
    elif shape < 3:
        return gt.borefield.Borefield.box_shaped_field(n_1, n_2, b_1, b_2, 100, borefield.D, borefield.r_b)
    elif shape < 4:
        return gt.borefield.Borefield.rectangle_field(n_1, n_2, b_1, b_2, 100, borefield.D, borefield.r_b)
    else:
        return gt.borefield.Borefield.staggered_rectangle_field(n_1, n_2, b_1, b_2, 100, borefield.D, borefield.r_b,
                                                                False)


def optimise_borefield_configuration(
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
        optimise: str = 'length',
        flow_field: ConstantFlowRate = None) -> list:
    """
    This function calculates the optimal borefield configuration within a certain area.
    This is done using the hyperparameter optimization framework optuna.

    Parameters
    ----------
    borefield
    l_1_max : float
        Maximum size in the length direction [m]
    l_2_max : float
        Maximum size in the width direction [m]
    b_min : float
        Minimum borehole spacing [m]
    b_max : float
        Maximum borehole spacing [m]
    b_step : float
        Step size borehole spacing [m]
    h_min : float
        Minimum borehole depth [m]
    h_max : float
        Maximum borehole depth [m]
    nb_min : int
        Minimum number of boreholes [-]
    nb_max : int
        Maximum number of boreholes [-]
    nb_of_trials : int
        Number of trials [-]
    types : list
        List with the shapes of the borefields that should be investigated, where type 0: L, type 1: U,
                type 2: box, type 3: rectangle, type 4: staggered
    size_L3 : bool
        True if L3 sizing should be used.
    optimise : str
        'Length' if the borefield should be optimised for the minimum borehole length, 'number' when the
        minimum number of boreholes should be selected.
    flow_field : ConstantFlowRate
        Contains the ConstantFlowRate object with the flow rate for the entire borefield. When this attribute is
        given, the flow rate gets adapted based on the number of boreholes in the system.

    Returns
    -------
    List
        List with found solutions, from optimal to less optimal. Each element in the list is a tuple which consists of
        the total borehole length, borefield configuration, number of boreholes and pygfunction borefield object.

    Raises
    ------
    UnsolvableOptimalFieldError
        When it is infeasible to find an optimal borefield size given the parameters
    """

    # set a theoretical maximum value of the total borehole length
    max_value = int(l_1_max / b_min) * int(l_2_max / b_min) * h_max

    # copy borefield
    borefield_temp = copy.deepcopy(borefield)

    def f(n_1: int, n_2: int, b_1: float, b_2: float, h_min: float, h_max: float, shape: int) -> tuple:
        """
        This function calculates the required borehole depth for a certain set of input parameters.

        Parameters
        ----------
        n_1 : int
            Number of boreholes in the length direction [-]
        n_2 : int
            Number of boreholes in the width direction [-]
        b_1 : float
            Borehole spacing in the length direction [-]
        b_2 : float
            Borehole spacing in the width direction [-]
        h_min : float
            Minimum borehole depth [m]
        h_max : float
            Maximum borehole depth [m]
        shape : int
            Shape of the borefield, where type 0: L, type 1: U, type 2: box, type 3: rectangle, type 4: staggered

        Returns
        -------
        tuple
            Total borehole length [m], number of boreholes [-]
        """
        borefield_temp.borefield = _find_borefield(borefield, n_1, n_2, b_1, b_2, shape)

        # correct flow rate
        if flow_field is not None:
            if flow_field._vfr is not None:
                borefield_temp.flow_data = ConstantFlowRate(vfr=flow_field.vfr() / borefield_temp.number_of_boreholes)
            else:
                borefield_temp.flow_data = ConstantFlowRate(mfr=flow_field.mfr() / borefield_temp.number_of_boreholes)
        try:
            if borefield_temp.number_of_boreholes < nb_min or borefield_temp.number_of_boreholes > nb_max:
                return max_value * 2, max_value * 2
            if size_L3:
                depth = borefield_temp.size_L3()
            else:
                depth = borefield_temp.size_L4()
            if h_min <= depth <= h_max:
                return depth * borefield_temp.number_of_boreholes, borefield_temp.number_of_boreholes
            return max_value * 2, max_value * 2
        except:
            return max_value * 2, max_value * 2

    def objective(trial: optuna.Trial):
        # Suggest b_1 first and calculate the max possible n_1 value
        b_1 = trial.suggest_float('b_1', b_min, b_max, step=b_step)
        max_n_1 = int(l_1_max / b_1)  # Ensure n_1 * b_1 < l_1_max
        n_1 = trial.suggest_int('n_1', 1, max_n_1)

        # Suggest parameters for n_2 and b_2 similarly
        b_2 = trial.suggest_float('b_2', b_min, b_max, step=b_step)
        max_n_2 = int(l_2_max / b_2)  # Ensure n_2 * b_2 < l_2_max
        n_2 = trial.suggest_int('n_2', 1, max_n_2)
        shape = trial.suggest_categorical('shape', types)

        total_length, number = f(n_1, n_2, b_1, b_2, h_min, h_max, shape)
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
            continue  # pragma: no cover

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

    def find_borefield(params: dict, total_borehole_length: float) -> gt.borefield.Borefield:
        """
        This function returns the pygfunction borefield objects for the given parameters.
        Parameters
        ----------
        params : dict
            Dictionary with the required borehole parameters (shape, n_1, n_2, b_1, b_2)
        total_borehole_length : float
            Total borehole length [m]

        Returns
        -------
        gt.borefield.Borefield
            pygfunction borefield object
        """
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

    if results[0][0] == max_value * 2:
        # no solution is found
        raise UnsolvableOptimalFieldError

    # (total borehole length, configuration, number of boreholes, pygfunction borefield)
    return [(i[0], i[1], i[2], find_borefield(i[1], i[0])) for i in results]


def brute_force_config(
        borefield: Borefield,
        l_1_max: float,
        l_2_max: float,
        b_min: float,
        b_max: float,
        b_step: float,
        h_min: float,
        h_max: float,
        types: list = [0, 1, 2, 3, 4],
        size_L3: bool = True,
        optimise: str = 'length'
):
    borefield_temp = copy.deepcopy(borefield)

    # set vars
    nb_of_boreholes = 999
    total_length = 1e9
    params = None

    for shape in types:
        for b_1 in np.arange(b_min, b_max + 0.1, b_step):
            for b_2 in np.arange(b_min, b_max + 0.1, b_step):
                for n_1 in range(1, int(l_1_max / b_1) + 1):
                    for n_2 in range(1, int(l_2_max / b_2) + 1):
                        borefield_temp.borefield = _find_borefield(borefield, n_1, n_2, b_1, b_2, shape)
                        try:
                            if size_L3:
                                depth = borefield_temp.size_L3()
                            else:  # pragma: no cover
                                depth = borefield_temp.size_L4()
                            if h_min <= depth <= h_max:

                                if optimise == 'length':
                                    if depth * borefield_temp.number_of_boreholes < total_length:
                                        total_length = depth * borefield_temp.number_of_boreholes
                                        nb_of_boreholes = borefield_temp.number_of_boreholes
                                        params = [n_1, n_2, b_1, b_2, shape]
                                else:
                                    if borefield_temp.number_of_boreholes < nb_of_boreholes:
                                        total_length = depth * borefield_temp.number_of_boreholes
                                        nb_of_boreholes = borefield_temp.number_of_boreholes
                                        params = [n_1, n_2, b_1, b_2, shape]
                        except:
                            pass
    borefield = _find_borefield(borefield, *params)
    borefield.H = total_length / nb_of_boreholes
    return (total_length, params, nb_of_boreholes, borefield)
