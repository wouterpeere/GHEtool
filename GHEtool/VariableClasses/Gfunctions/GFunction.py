from __future__ import annotations

import warnings
from typing import List, Tuple, Union

import numpy as np
import pandas as pd
import pygfunction as gt
from numpy._typing import NDArray
from scipy import interpolate

from GHEtool.VariableClasses.Cylindrical_correction import update_pygfunction
from .CustomGFunction import _time_values

# add cylindrical correction to pygfunction
update_pygfunction()


class FIFO:
    """
    This class is a container with n elements. If the n+1th element is added, the first is removed
    """

    def __init__(self, length: int = 2):
        """

        Parameters
        ----------
        length : int
            Length of the fifo-array
        """
        self.length: int = length
        self.fifo_list: list = []

    def add(self, value: float) -> None:
        """
        This function adds the value to the fifo array.
        If the array is full, the first element is removed.

        Parameters
        ----------
        value : float
            Value to be added to the array

        Returns
        -------
        None
        """
        if len(self.fifo_list) >= self.length:
            self.fifo_list.pop(0)

        self.fifo_list.append(value)

    def in_fifo_list(self, value: float) -> bool:
        """
        This function checks whether the value is in the fifo list, but not the last element!

        Parameters
        ----------
        value : float
            Value potentially in the fifo list

        Returns
        -------
        bool
            True if the value is in the fifo list, false otherwise
        """

        return value in self.fifo_list and not self.fifo_list[-1] == value

    def clear(self) -> None:
        """
        This function clears the fifo_array.

        Returns
        -------
        None
        """
        self.fifo_list = []


class GFunction:
    """
    Class that contains the functionality to calculate gfunctions and to store
    previously calculated values that can potentially be used for interpolation to save time.
    This is done by storing previously calculated gvalues.
    """

    DEFAULT_TIMESTEPS: np.ndarray = _time_values()
    DEFAULT_NUMBER_OF_TIMESTEPS: int = DEFAULT_TIMESTEPS.size
    DEFAULT_STORE_PREVIOUS_VALUES: bool = True

    def __init__(self):
        self._store_previous_values: bool = GFunction.DEFAULT_STORE_PREVIOUS_VALUES
        self._store_previous_values_backup: bool = GFunction.DEFAULT_STORE_PREVIOUS_VALUES
        self.options: dict = {"method": "equivalent"}
        self.alpha: float = 0.0
        self.borefield: gt.borefield.Borefield = None
        self.borehole_length_array: np.ndarray = np.array([])
        self.time_array: np.ndarray = np.array([])
        self.previous_gfunctions: np.ndarray = np.array([])
        self.previous_borehole_length: float = 0.0
        self.use_cyl_correction_when_negative: bool = True
        self.use_neural_network: bool = False

        self.no_extrapolation: bool = True
        self.threshold_borehole_length_interpolation: float = 0.25  # %

        self.fifo_list: FIFO = FIFO(8)

        # initiate ANN
        self.normalize_vec = np.array((1 / 20, 1 / 20, 1 / 9, 1 / 9, 1 / 1000, 1 / 100, 1 / 0.4, 1 / (10 ** -6), 1 / 6))
        from GHEtool import FOLDER
        for file_path in FOLDER.joinpath(f"VariableClasses/GFunctions").rglob('*'):
            if file_path.is_file():
                print(file_path)
        self.model_weights = [
            pd.read_csv(FOLDER.joinpath(f"VariableClasses/GFunctions/layer_{i}_weights_diff_fields.csv"),
                        sep=";").values for i in range(6)]

    @property
    def store_previous_values(self) -> bool:
        """
        This returns the truth value of the store_previous_values attribute.

        Returns
        -------
        bool
            True if the previously calculated gfunction values should be saved.
        """
        return self._store_previous_values

    @store_previous_values.setter
    def store_previous_values(self, store: bool) -> None:
        """
        This function sets the store previous values attribute and also its backup.

        Parameters
        ----------
        store : bool
            True if the previous calculated g-function values should be stored.

        Returns
        -------
        None
        """
        self._store_previous_values = store
        self._store_previous_values_backup = store

    def calculate(self, time_value: Union[list, float, np.ndarray], borefield: gt.borefield.Borefield,
                  alpha: float, interpolate: bool = None, use_neural_network: bool = False, **kwargs):
        """
        This function returns the gvalues either by interpolation or by calculating them.
        It does so by calling the function gvalues which does this calculation.
        This calculation function also stores the previous calculated data and makes interpolations
        whenever the requested list of time_value are longer then DEFAULT_NUMBER_OF_TIMESTEPS.

        Parameters
        ----------
        time_value : list, float, np.ndarray
            Array with all the time values [s] for which gvalues should be calculated
        borefield : pygfunction.borefield.Borefield
            Borefield model for which the gvalues should be calculated
        alpha : float
            Thermal diffusivity of the ground [m2/s]
        interpolate : bool
            True if results should be interpolated when possible, False otherwise. If None, the default is chosen.
        use_neural_network : bool
            True if the neural network simplification should be used. This uses a NN trained on previous calculated
            gvalues.
        
        Returns
        -------
        gvalues : np.ndarray
            1D array with all the requested gvalues
        """

        def calculate_with_neural_network(alpha: float, borefield: gt.borefield.Borefield,
                                          borefield_description: dict) -> np.ndarray:
            """
            This function calculates the gfunctions using a trained ANN.
            (For more information, visit Blanke et al. ([#BlankeEtAl]_).

            References
            ----------
            .. [#BlankeEtAl] Blanke T., Pfeiffer F., Göttsche J., Döring B. (2024) Artificial neural networks use for the design of geothermal probe fields. In Proceedings of BauSim Conference 2024:  10th Conference of IBPSA-Germany and Austria. Vienna (Austria), 23-26 September 2024. https://doi.org/10.26868/29761662.2024.12

            Parameters
            ----------
            alpha : float
                Thermal diffusivity of the ground [m2/s]
            borefield : pygfunction.borefield.Borefield
                Pygfunction borefield object
            borefield_description : dict
                Description of the borefield with keys: {N_1, N_2, B_1, B_2, type}

            Returns
            -------
            gvalues : np.ndarray
                Array with the gvalues for the default timesteps
            """
            # parameters can be extracted from a random borehole since for the ANN model, all boreholes should be the same.
            H = borefield[0].H
            D = borefield[0].D
            r_b = borefield[0].r_b
            n_x = borefield_description["N_1"]
            n_y = borefield_description["N_2"]
            b_x = borefield_description["B_1"]
            b_y = borefield_description["B_2"]
            if H > 500:
                warnings.warn("Depth outside ANN limits!")
            if D > 5:
                warnings.warn("Burial depth outside ANN limits!")
            if n_x > 35:
                warnings.warn("N_1 outside ANN limits!")
            if n_y > 35:
                warnings.warn("N_2 outside ANN limits!")
            if b_x > 11:
                warnings.warn("B_1 outside ANN limits!")
            if b_y > 11:
                warnings.warn("B_2 outside ANN limits!")
            if r_b > 0.2:
                warnings.warn("r_b outside ANN limits!")
            if not (0.2 / 1000 < alpha < 3 / 1000):
                warnings.warn("alpha outside ANN limits!")
            if not (0 <= borefield_description["type"] < 6):
                warnings.warn("r_b outside ANN limits!")
            input_data = np.array([n_x, n_y, b_x, b_y, H, D, r_b, alpha, borefield_description["type"]])
            res = calc_network_using_numpy(input_data, self.model_weights, self.normalize_vec)
            return res

        def gvalues(
                time_values: np.ndarray,
                borefield: gt.borefield.Borefield,
                alpha: float,
                borehole_length: float,
                interpolate: bool = None,
                use_neural_network: bool = False,
                **kwargs,
        ) -> np.ndarray:
            """
            This function returns the gvalues either by interpolation or by calculating them.

            Parameters
            ----------
            time_values : np.ndarray
                Array with all the time values [s] for which gvalues should be calculated
            borefield : pygfunction.borefield.Borefield
                Borefield model for which the gvalues should be calculated
            alpha : float
                Thermal diffusivity of the ground [m2/s]
            borehole_length : float
                Borehole length [m]
            interpolate : bool
                True if results should be interpolated when possible, False otherwise. If None, the default is chosen.
            use_neural_network : bool
                True if the neural network simplification should be used. This uses a NN trained on previous calculated
                gvalues.

            Returns
            -------
            gvalues : np.ndarray
                1D array with all the requested gvalues
            """

            # use neural network
            if use_neural_network or self.use_neural_network:
                if not "borefield_description" in kwargs:
                    raise ValueError(
                        "You can only use the ANN when you have a regular configuration. Please use the "
                        "create_rectangle_borefield or similar methods in the Borefield class."
                    )
                return np.interp(GFunction.DEFAULT_TIMESTEPS, time_values,
                                 calculate_with_neural_network(alpha, borefield, **kwargs))

            # check if the value is in the fifo_list
            # if the value is in self.borehole_length_array, there is no problem, since the interpolation will be exact anyway
            if self.fifo_list.in_fifo_list(borehole_length) and borehole_length not in self.borehole_length_array:
                # chances are we are stuck in a loop, so calculate the gfunction and do not iterate

                # calculate the g-values for uniform borehole wall temperature
                gfunc_calculated = gt.gfunction.gFunction(borefield, alpha, time_values, options=self.options).gFunc

                # store the calculated g-values
                self.set_new_calculated_data(time_values, borehole_length, gfunc_calculated, borefield, alpha)

                self.fifo_list.add(borehole_length)

                return gfunc_calculated

            # store in fifo_list to make sure we are not stuck in iterations
            self.fifo_list.add(borehole_length)

            # check if previous borehole_length is close to current one
            # if so, returns previous gfunction data to speed up sizing convergence
            if np.abs(self.previous_borehole_length - borehole_length) < 1:
                borehole_length = self.previous_borehole_length
            else:
                self.previous_borehole_length = borehole_length
            # do interpolation
            interpolate = interpolate if interpolate is not None else self.store_previous_values
            gfunc_interpolated = self.interpolate_gfunctions(time_values, borehole_length, alpha,
                                                             borefield) if interpolate else np.array([])

            # if there are g-values calculated, return them
            if np.any(gfunc_interpolated):
                return gfunc_interpolated

            # calculate the g-values for uniform borehole wall temperature
            gfunc_calculated = gt.gfunction.gFunction(borefield, alpha, time_values, options=self.options,
                                                      method=self.options["method"]).gFunc
            if np.any(gfunc_calculated < 0):
                warnings.warn("There are negative g-values. This can be caused by a large borehole radius.")
                if self.use_cyl_correction_when_negative:
                    # there are negative gfunction values
                    warnings.warn(
                        "Cylindrical correction is used to correct this large borehole. "
                        "You can change this behaviour by setting the use_cyl_correction_when_negative variable "
                        "of the Gfunction class to False."
                    )

                    backup = self.options.get("Cylindrical_correction")

                    self.options["cylindrical_correction"] = True
                    gfunc_calculated = gt.gfunction.gFunction(borefield, alpha, time_values, options=self.options,
                                                              method=self.options["method"]).gFunc
                    self.options["cylindrical_correction"] = backup

            # store the calculated g-values
            self.set_new_calculated_data(time_values, borehole_length, gfunc_calculated, borefield, alpha)

            return gfunc_calculated

        # get borehole_length from borefield
        borehole_length = borefield[0].H

        # make numpy array from time_values
        if isinstance(time_value, (float, int)):
            time_value_np = np.array([time_value])
        else:
            time_value_np = np.array(time_value)

        if not isinstance(time_value, (float, int)) and time_value_np.size > GFunction.DEFAULT_NUMBER_OF_TIMESTEPS:
            # due to this many requested time values, the calculation will be slow.
            # there will be interpolation

            time_value_new = _time_values(t_max=time_value[-1])

            # calculate g-function values
            gfunc_uniform_T = gvalues(time_value_new, borefield, alpha, borehole_length, interpolate,
                                      use_neural_network, **kwargs)

            # return interpolated values
            return np.interp(time_value, time_value_new, gfunc_uniform_T)

        # check if there are double values
        if not isinstance(time_value, (float, int)) and time_value_np.size != np.unique(np.asarray(time_value)).size:
            # calculate g-function values
            gfunc_uniform_T = gvalues(np.unique(time_value_np), borefield, alpha, borehole_length, interpolate,
                                      use_neural_network, **kwargs)

            return np.interp(time_value, np.unique(time_value_np), gfunc_uniform_T)

        # calculate g-function values
        gfunc_uniform_T = gvalues(time_value_np, borefield, alpha, borehole_length, interpolate, use_neural_network,
                                  **kwargs)

        return gfunc_uniform_T

    def interpolate_gfunctions(self, time_value: Union[list, float, np.ndarray], borehole_length: float,
                               alpha: float, borefield: List[gt.boreholes.Borehole]) -> np.ndarray:
        """
        This function returns the gvalues by interpolation them. If interpolation is not possible, an emtpy
        array is returned.

        Parameters
        ----------
        time_value : list, float, np.ndarray
            Time value(s) [s] for which gvalues should be calculated
        borehole_length : float
            Borehole length [m]
        alpha : float
            Thermal diffusivity of the ground [m2/s]
        borefield : list[pygfunction.boreholes.Borehole]
            Borefield model for which the gvalues should be calculated

        Returns
        -------
        gvalues : np.ndarray
            1D array with all the requested gvalues
        """
        gvalues: np.ndarray = np.zeros(len(time_value))

        # check if interpolation is possible:
        if not (self._check_alpha(alpha) and self._check_borefield(borefield)):
            # the alpha and/or borefield is not in line with the precalculated data
            return gvalues

        # check if interpolation of all time values can be done based on the available time values
        if not self._check_time_values(time_value):
            return gvalues

        # find nearest borehole_length indices
        idx_prev, idx_next = self._get_nearest_borehole_length_index(borehole_length)

        if self.no_extrapolation:
            # no interpolation can be made since borehole length is not in between values in the borehole length array
            if idx_prev is None or idx_next is None:
                return gvalues

            # do interpolation
            if self.borehole_length_array.size == 1:
                gvalues = interpolate.interpn([self.time_array], self.previous_gfunctions, time_value)
            else:
                gvalues = interpolate.interpn(
                    (self.borehole_length_array, self.time_array), self.previous_gfunctions,
                    np.array([[borehole_length, t] for t in time_value])
                )

            return gvalues

        # when extrapolation is permitted
        # not yet implemented
        return gvalues

    @staticmethod
    def _nearest_value(array: np.ndarray, value: float) -> Tuple[int, int]:
        """
        This function searches the nearest value and index in an array.

        Parameters
        ----------
        array : np.ndarray
            Array in which the value should be searched
        value : float
            Value to be searched for

        Returns
        -------
        nearest_value, nearest_index : tuple(int, int)
        """
        if not np.any(array):
            return False
        idx = (np.abs(array - value)).argmin()
        return array[idx], idx

    def _get_nearest_borehole_length_index(self, borehole_length: float) -> Tuple[int, int]:
        """
        This function returns the nearest borehole length indices w.r.t. a specific borehole length.

        Parameters
        ----------
        borehole_length : float
            Borehole length for which the nearest indices in the borehole_length_array should be searched.

        Returns
        -------
        tuple(int, int)
            (None, None) if no indices exist that are closer than the threshold value
            (None, int) if the current borehole length is lower then the minimum in the borehole_length array, but closer then the
            threshold value
            (int, None) if the current borehole length is higher then the maximum in the borehole_length array, but closer then the
            threshold value
            (int, int) if the current borehole length is between two previous calculated borehole_lengths which are closer together
            then the threshold value

        Raises
        ------
        ValueError
            When the borehole length is smaller or equal to zero
        """
        # raise error when value is negative
        if borehole_length <= 0:
            raise ValueError(f"The borehole length {borehole_length} is smaller then zero!")

        # get nearest borehole_length index
        val_borehole_length, idx_borehole_length = self._nearest_value(self.borehole_length_array, borehole_length)

        # the exact borehole_length is in the previous calculated data
        # two times the same index is returned
        if val_borehole_length == borehole_length:
            return idx_borehole_length, idx_borehole_length

        if borehole_length > val_borehole_length:
            # the nearest index is the first in the array and the borehole length is smaller than the smallest value in the array
            # but the difference is smaller than the threshold for interpolation
            if (
                    idx_borehole_length == self.borehole_length_array.size - 1
                    and borehole_length - val_borehole_length < self.threshold_borehole_length_interpolation * borehole_length
            ):
                return idx_borehole_length, None
            elif idx_borehole_length != self.borehole_length_array.size - 1:
                idx_next = idx_borehole_length + 1
                if self.borehole_length_array[
                    idx_next] - val_borehole_length < self.threshold_borehole_length_interpolation * borehole_length:
                    return idx_borehole_length, idx_next
        else:
            # the nearest index is the last in the array and the borehole length is larger than the highest value in the array
            # but the difference is smaller than the threshold for interpolation
            if idx_borehole_length == 0 and val_borehole_length - borehole_length < self.threshold_borehole_length_interpolation * borehole_length:
                return None, idx_borehole_length
            elif idx_borehole_length != 0:
                idx_prev = idx_borehole_length - 1
                if val_borehole_length - self.borehole_length_array[
                    idx_prev] < self.threshold_borehole_length_interpolation * borehole_length:
                    return idx_prev, idx_borehole_length

        # no correct interpolation indices are found
        # None, None is returned
        return None, None

    def _check_time_values(self, time_array: np.ndarray) -> bool:
        """
        This function checks whether or not the time values are suitable for interpolation.
        This is done by two checks:

        1. Is the time_array longer then the stored self.time_array? If yes, False is returned.

        2. Is the smallest value of the time_array smaller then the smallest value in the stored self.time_array
        (and vice versa for the largest value), False is returned.

        Parameters
        ----------
        time_array : np.array
            The array of time values [s] for interpolation

        Returns
        -------
        bool
            True if the time values are suitable for interpolation.
        """

        if self.time_array.size == 0 or time_array.size == 0:
            return False

        if self.time_array.size < time_array.size:
            return False

        if self.time_array[0] <= time_array[0] and self.time_array[-1] >= time_array[-1]:
            return True

        return False

    def set_options_gfunction_calculation(self, options: dict, add: bool = True) -> None:
        """
        This function sets the options for the gfunction calculation of pygfunction.
        This dictionary is directly passed through to the gFunction class of pygfunction.
        For more information, please visit the documentation of pygfunction.

        Parameters
        ----------
        options : dict
            Dictionary with options for the gFunction class of pygfunction
        add : bool
            True if the options should be added, False is the options should be replaced.

        Returns
        -------
        None
        """
        if add:
            self.options.update(options)
            return

        # replace options
        self.options = options

    def remove_previous_data(self) -> None:
        """
        This function removes the previous calculated data by setting the borehole_length_array, time_array and
        previous_gfunctions back to empty arrays.

        Returns
        -------
        None
        """
        self.borehole_length_array = np.array([])
        self.time_array = np.array([])
        self.previous_gfunctions = np.array([])
        self.alpha = 0
        self.borefield = []
        self.fifo_list.clear()

    def set_new_calculated_data(self, time_values: np.ndarray, borehole_length: float, gvalues: np.ndarray, borefield,
                                alpha) -> bool:
        """
        This function stores the newly calculated gvalues if this is needed.

        Parameters
        ----------
        time_values : np.ndarray
            Array with all the time values [s] for which gvalues should be calculated
        borehole_length : float
            Borehole length [m]
        gvalues : np.ndarray
            Array with all the calculated gvalues for the corresponding borefield, alpha and time_values
        borefield : list[pygfunction.borehole]
            Borefield model for which the gvalues should be calculated
        alpha : float
            Thermal diffusivity of the ground [m2/s]

        Returns
        -------
        bool
            True if the data is saved, False otherwise
        """

        def check_if_data_should_removed() -> bool:
            """
            This function checks whether or not the previous data should be removed.
            It does so by comparing the stored with the new values for alpha, borefield and time_values.

            Returns
            -------
            bool
                True if the previous data should be removed
            """
            if not self._check_alpha(alpha):
                return True

            if not self._check_borefield(borefield):
                return True

            if not self._check_time_values(time_values):
                return True

            return False

        def check_if_data_should_be_saved() -> bool:
            """
            This function implements a couple of checks to see whether the new data should be saved.
            Currently, the following tests are implemented:

            1) check if the data should be saved

            2) check if the new time_values is longer then the saved one. If not, the data should not be saved
            since we would lose more data then we gain.

            Returns
            -------
            bool
                True if the data should be saved, False otherwise
            """

            if not self.store_previous_values:
                # previous data should not be stored
                return False

            if time_values.size < self.time_array.size:
                # the new time array is smaller, so we would lose data if it was saved, whereby the
                # previous data should be deleted.
                return False

            return True

        # check if the newly calculated data should be saved
        if not check_if_data_should_be_saved():
            return False

        # check if the previous stored data should be removed
        if check_if_data_should_removed():
            self.remove_previous_data()

        nearest_idx = 0

        if np.any(self.previous_gfunctions):
            nearest_val, nearest_idx = self._nearest_value(self.borehole_length_array, borehole_length)
            if self.borehole_length_array[nearest_idx] < borehole_length:
                nearest_idx += 1

        # insert data in stored data
        if self.borehole_length_array.size == 1:
            # self.previous_gfunctions should be converted to a 2D-array
            if self.borehole_length_array[0] > borehole_length:
                self.previous_gfunctions = np.vstack((gvalues, self.previous_gfunctions))
            else:
                self.previous_gfunctions = np.vstack((self.previous_gfunctions, gvalues))
        else:
            self.previous_gfunctions = np.insert(self.previous_gfunctions, nearest_idx, gvalues, 0)

        self.borehole_length_array = np.insert(self.borehole_length_array, nearest_idx, borehole_length)
        self.time_array = time_values
        self.borefield = borefield
        self.alpha = alpha

        return True

    def _check_borefield(self, borefield: gt.borefield.Borefield) -> bool:
        """
        This function checks whether the new borefield object is equal to the previous one.
        It does so by comparing all the parameters (neglecting the borehole length).
        If the borefield objects are unequal, the borefield variable is set to the new borefield
        and all the previously saved gfunctions are deleted.

        Parameters
        ----------
        borefield : pygfunction.borefield.Borefield
            New borefield for which the gfunctions should be calculated

        Returns
        -------
        True
            True if the borefields are the same, False otherwise
        """
        # borefields are unequal if they have different number of boreholes
        if len(borefield) != len(self.borefield):
            return False

        keys = set(borefield[0].__dict__.keys())
        keys.remove("H")

        for idx, _ in enumerate(borefield):
            for key in keys:
                if getattr(borefield[idx], key) != getattr(self.borefield[idx], key):
                    return False

        return True

    def _check_alpha(self, alpha) -> bool:
        """
        This function checks whether the thermal diffusivity object is equal to the previous one.
        If the alpha's are unequal, the alpha variable is set to the new alpha value
        and all the previously saved gfunctions are deleted.

        Parameters
        ----------
        alpha : float
            Thermal diffusivity of the ground of the borefield for which the gfunctions should be calculated [m2/s].

        Returns
        -------
        True
            True if the alpha's are the same, False otherwise
        """
        if alpha == 0.0:
            return False
        if alpha != self.alpha:
            return False

        return True


def calc_network_using_numpy(input_data: NDArray[np.float64], model_weights: list[NDArray[np.float64]],
                             normalize_vec: NDArray[np.float64]) -> NDArray[
    np.float64]:
    input_data = (input_data * normalize_vec).reshape(9, 1)
    res = np.maximum(0, model_weights[0].T.dot(input_data) + model_weights[1])
    res = np.maximum(0, model_weights[2].T.dot(res) + model_weights[3])
    res = np.maximum(0, model_weights[4].T.dot(res) + model_weights[5])
    return np.cumsum(res, axis=1).reshape(87)
