import numpy as np

from scipy.interpolate import interpn, interp1d
from typing import Union
from GHEtool.VariableClasses.BaseClass import BaseClass
from collections import defaultdict


class _EfficiencyBase(BaseClass):

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False

        for key in self.__dict__:
            value1 = self.__dict__[key]
            value2 = other.__dict__[key]

            if isinstance(value1, np.ndarray) and isinstance(value2, np.ndarray):
                if not np.array_equal(value1, value2):
                    return False
            else:
                if not np.array_equal(value1, value2):
                    return False

        return True


class _Efficiency(_EfficiencyBase, BaseClass):
    """
    Baseclass for all the efficiencies
    """

    def __init__(self,
                 data: np.ndarray,
                 coordinates: np.ndarray,
                 part_load: bool = False,
                 secondary: bool = False,
                 reference_nominal_power: float = None,
                 nominal_power: float = None):
        """

        Parameters
        ----------
        data : np.ndarray
            1D-array with all efficiency values.
        coordinates : np.ndarray
            1D array with all the coordinates at which the efficiency values can be found. These coordinates can be
            1D up to 3D, depending on whether secondary temperature and/or part load is taken into account.
        part_load : bool
            True if the data contains part load information.
        secondary : bool
            True if the data contains secondary temperature information
        reference_nominal_power : float
            If you want to use the efficiency class as a reference of different heat pumps, you need to define a reference
            for the nominal power, at which the data is defined. This is only relevant when part load data is available.
        nominal_power : float
            The nominal power at which to define the current efficiency class. This converts the provided efficiency data
            from the reference_nominal_power to the nominal_power. This is only relevant when part load data is available
            and the reference_nominal_power is provided.

        Raises
        ------
        ValueError
            When the shape of the data does not equal the provided ranges.
        ValueError
            When there is a datapoint smaller or equal to zero.

        """
        self._interp = None
        self._nearestp = None
        self._has_secondary: bool = secondary
        self._has_part_load: bool = part_load
        self._data_: np.ndarray = data
        self._coordinates_: np.ndarray = coordinates
        self._reference_nominal_power: float = reference_nominal_power
        self._nominal_power: float = nominal_power

        self._range_primary: np.ndarray = np.array([])
        self._range_secondary: np.ndarray = np.array([])
        self._range_part_load: np.ndarray = np.array([])

        # check if all data points are higher than 0
        if not np.all(data > 0):
            raise ValueError('The efficiencies should all be above zero!')

        # check if the data has the same length as the coordinates
        if len(data) != len(coordinates):
            raise ValueError('The provided data and coordinates array are not of the same length!')

        # check dimension
        dimensions = 1 if isinstance(coordinates[0], (int, float, np.int32, np.int64, np.float16, np.float32)) else len(
            coordinates[0])
        if dimensions != 1 + self._has_secondary + self._has_part_load:
            raise ValueError(f'The provided coordinate data has {dimensions} dimensions whereas '
                             f'{1 + self._has_secondary + self._has_part_load} dimensions where provided.'
                             'Please check the nb_of_points for both secondary temperature and part load.')

        # get ranges
        self._points = []
        if dimensions == 3:
            self._range_primary = np.sort(np.unique(coordinates[:, 0]))
            self._range_secondary = np.sort(np.unique(coordinates[:, 1]))
            self._range_part_load = np.sort(np.unique(coordinates[:, 2]))
            self._points.append(self._range_secondary)
            self._points.append(self._range_part_load)
        elif self._has_secondary:
            self._range_primary = np.sort(np.unique(coordinates[:, 0]))
            self._range_secondary = np.sort(np.unique(coordinates[:, 1]))
            self._points.append(self._range_secondary)
        elif self._has_part_load:
            self._range_primary = np.sort(np.unique(coordinates[:, 0]))
            self._range_part_load = np.sort(np.unique(coordinates[:, 1]))
            self._points.append(self._range_part_load)
        else:
            self._range_primary = np.sort(coordinates)
        self._points.insert(0, self._range_primary)

        def find_value(x, y, z=None):
            if z is None:
                index = np.nonzero(np.all(coordinates == (x, y), axis=1))[0]
            else:
                index = np.nonzero(np.all(coordinates == (x, y, z), axis=1))[0]

            # the data point exists
            if len(index) > 0:
                return data[index[0]]

            # the data point does not exist, so we have to interpolate to get it
            x_array = []
            y_array = []
            if z is None:
                # only one dimension to check
                for idx, val in enumerate(coordinates):
                    if val[0] == x:
                        x_array.append(val[1])
                        y_array.append(data[idx])
            else:
                # two dimensions to check
                for idx, val in enumerate(coordinates):
                    if val[0] == x and val[1] == y:
                        x_array.append(val[2])
                        y_array.append(data[idx])
            # as array
            x_array = np.array(x_array)
            y_array = np.array(y_array)

            # sort array
            p = x_array.argsort()
            x_array = x_array[p]
            y_array = y_array[p]

            temp = np.interp(y if z is None else z, x_array, y_array)
            return temp

        # populate data matrix
        if dimensions == 3:
            self._data = np.empty((len(self._range_primary), len(self._range_secondary), len(self._range_part_load)))
            for i in range(self._data.shape[0]):
                for j in range(self._data.shape[1]):
                    for k in range(self._data.shape[2]):
                        self._data[i, j, k] = find_value(self._range_primary[i],
                                                         self._range_secondary[j],
                                                         self._range_part_load[k])
            # get max powers per temperature
            x = coordinates[:, 0]
            y = coordinates[:, 1]
            z = coordinates[:, 2]

            ix = np.searchsorted(self._range_primary, x)
            iy = np.searchsorted(self._range_secondary, y)

            flat_idx = ix * len(self._range_secondary) + iy

            max_z_flat = np.full(len(self._range_primary) * len(self._range_secondary), -np.inf)
            np.maximum.at(max_z_flat, flat_idx, z)

            max_z = max_z_flat.reshape(len(self._range_primary), len(self._range_secondary))
            # convert index to part load value
            self._max_part_load = max_z

        elif dimensions == 2:
            self._data = np.empty(
                (len(self._range_primary), max(len(self._range_secondary), len(self._range_part_load))))
            if self._has_secondary:
                for i in range(self._data.shape[0]):
                    for j in range(self._data.shape[1]):
                        self._data[i, j] = find_value(self._range_primary[i],
                                                      self._range_secondary[j])
            else:
                for i in range(self._data.shape[0]):
                    for j in range(self._data.shape[1]):
                        self._data[i, j] = find_value(self._range_primary[i],
                                                      self._range_part_load[j])

                # get max powers per temperature
                x = coordinates[:, 0]
                y = coordinates[:, 1]

                idx = np.searchsorted(self._range_primary, x)

                max_y = np.full(len(self._range_primary), -np.inf)
                np.maximum.at(max_y, idx, y)

                self._max_part_load = max_y
        else:
            p = self._range_primary.argsort()
            self._data = data[p]

        # correct for nominal power
        if nominal_power is not None and reference_nominal_power is None:
            raise ValueError('Please enter a reference nominal power.')

        if self._has_part_load and nominal_power is not None:
            self._range_part_load *= nominal_power / reference_nominal_power

    def _get_efficiency(self,
                        primary_temperature: Union[float, np.ndarray],
                        secondary_temperature: Union[float, np.ndarray] = None,
                        power: Union[float, np.ndarray] = None) -> np.ndarray:
        """
        This function calculates the efficiency. This function uses interpolation and sets the out-of-bound values
        to the nearest value in the dataset. This function does hence not extrapolate.

        Parameters
        ----------
        primary_temperature : np.ndarray or float
            Value(s) for the average primary temperature of the heat pump for the efficiency calculation.
        secondary_temperature : np.ndarray or float
            Value(s) for the average secondary temperature of the heat pump for the efficiency calculation.
        power : np.ndarray or float
            Value(s) for the part load data of the heat pump for the efficiency calculation.

        Raises
        ------
        ValueError
            When secondary_temperature is in the dataset, and it is not provided. Same for power.

        Returns
        -------
        Efficiency
            np.ndarray
        """
        # check if all the required values are present
        if self._has_secondary != (secondary_temperature is not None):
            if self._has_secondary:
                raise ValueError('The EER class requires a value for the secondary temperature.')
        if self._has_part_load != (power is not None):
            if self._has_part_load:
                raise ValueError('The EER class requires a value for the part-load.')

        # get maximum length
        _max_length = np.max([len(i) if i is not None and not isinstance(i, (float, int)) else 1 for i in
                              (primary_temperature, secondary_temperature, power)])

        # convert to arrays
        primary_temperature = np.array(
            np.full(_max_length, primary_temperature) if isinstance(primary_temperature,
                                                                    (float, int)) else primary_temperature)
        secondary_temperature = np.array(
            np.full(_max_length, secondary_temperature) if isinstance(secondary_temperature,
                                                                      (float, int)) else secondary_temperature)
        power = np.array(np.full(_max_length, power) if isinstance(power, (float, int)) else power)

        # clip, so that no values fall outside the provided values
        primary_temperature_clipped = np.clip(primary_temperature,
                                              np.min(self._range_primary),
                                              np.max(self._range_primary))
        secondary_temperature_clipped = None
        part_load_clipped = None
        if self._has_secondary:
            secondary_temperature_clipped = np.clip(secondary_temperature, np.min(self._range_secondary),
                                                    np.max(self._range_secondary))
        if self._has_part_load:
            part_load_clipped = np.clip(power, np.min(self._range_part_load), np.max(self._range_part_load))

        xi = primary_temperature_clipped
        if self._has_part_load and self._has_secondary:
            xi = list(zip(primary_temperature_clipped, secondary_temperature_clipped, part_load_clipped))
        elif self._has_secondary:
            xi = list(zip(primary_temperature_clipped, secondary_temperature_clipped))
        elif self._has_part_load:
            xi = list(zip(primary_temperature_clipped, part_load_clipped))

        interp = interpn(self._points, self._data, xi, bounds_error=False, fill_value=np.nan)
        if not np.isnan(interp).any():
            return interp

    def _get_max_power(self,
                       primary_temperature: Union[float, np.ndarray],
                       secondary_temperature: Union[float, np.ndarray] = None) -> np.ndarray:
        """
        This function returns the maximum available power for a certain primary and secondary temperature.

        Parameters
        ----------
        primary_temperature : np.ndarray or float
            Value(s) for the average primary temperature of the heat pump for the efficiency calculation.
        secondary_temperature : np.ndarray or float
            Value(s) for the average secondary temperature of the heat pump for the efficiency calculation.

        Raises
        ------
        ValueError
            When secondary_temperature is in the dataset, and it is not provided. Same for power.

        Returns
        -------
        Efficiency
            np.ndarray
        """

        if not self._has_part_load:
            return 1e16

            # reuse your existing clipping and array logic
        _max_length = np.max([
            len(i) if i is not None and not isinstance(i, (float, int)) else 1
            for i in (primary_temperature, secondary_temperature)
        ])

        Tp = np.array(
            np.full(_max_length, primary_temperature)
            if isinstance(primary_temperature, (float, int))
            else primary_temperature
        )

        Ts = None
        if self._has_secondary:
            if secondary_temperature is None:
                raise ValueError("Secondary temperature is required.")
            Ts = np.array(
                np.full(_max_length, secondary_temperature)
                if isinstance(secondary_temperature, (float, int))
                else secondary_temperature
            )

        # clip
        Tp = np.clip(Tp, np.min(self._range_primary), np.max(self._range_primary))
        if self._has_secondary:
            Ts = np.clip(Ts, np.min(self._range_secondary), np.max(self._range_secondary))

        # interpolate directly on precomputed surface
        if self._has_secondary:
            xi = list(zip(Tp, Ts))
        else:
            xi = Tp

        return interpn(
            self._points[:1 + self._has_secondary],
            self._max_part_load,
            xi,
            bounds_error=False,
            fill_value=np.nan
        )


def plot_heat_pump_envelope(points, eff, ax=None, label_prefix="T"):
    """
    Plot heat pump efficiency as a function of power for each primary temperature.

    Parameters
    ----------
    points : ndarray of shape (N, 2)
        Array of (primary_temperature, available_power) pairs.
    eff : ndarray of shape (N,)
        Efficiencies corresponding to `points`.
    ax : matplotlib.axes.Axes, optional
        Axis to plot on. If None, a new figure and axis are created.
    label_prefix : str, optional
        Prefix for legend labels. Default is "T".

    Returns
    -------
    ax : matplotlib.axes.Axes
        Axis containing the plot.
    """

    import numpy as np
    import matplotlib.pyplot as plt
    from collections import defaultdict

    if ax is None:
        fig, ax = plt.subplots()

    # group by temperature
    grouped = defaultdict(lambda: {"power": [], "eff": []})

    for (T, P), e in zip(points, eff):
        grouped[T]["power"].append(P)
        grouped[T]["eff"].append(e)

    # plot each temperature
    for T in sorted(grouped.keys()):
        p = np.asarray(grouped[T]["power"])
        e = np.asarray(grouped[T]["eff"])

        # sort and remove duplicate power values
        idx = np.argsort(p)
        p = p[idx]
        e = e[idx]

        p_unique, idx_unique = np.unique(p, return_index=True)
        e_unique = e[idx_unique]

        ax.plot(p_unique, e_unique, marker="o", label=f"{label_prefix} = {T}")

    ax.set_xlabel("Power")
    ax.set_ylabel("Efficiency")
    ax.grid(True)
    ax.legend()

    return ax


def combine_n_heat_pumps(points_list, eff_list):
    """
    Combine the operating envelopes of multiple modulating heat pumps into a
    single equivalent operating envelope using strict cascade staging.

    At each primary temperature, the heat pumps are ordered by increasing
    minimum available power and combined according to a deterministic
    staging strategy:

    Operating logic (per temperature)
    ---------------------------------
    1. Single-machine operation
       Below the sum of the minimum powers of the two smallest heat pumps,
       only the smallest heat pump may operate.

    2. Single-machine overlap (HP1 vs HP2 only)
       In the same low-power region, both of the two smallest heat pumps
       may operate individually. At equal part load, the heat pump with
       the highest efficiency is selected.

       No overlap regions are allowed beyond this first staging level.

    3. Cascade operation with strict staging
       Once the combined minimum power of k heat pumps is reached,
       exactly k heat pumps operate simultaneously.

       For each cascade stage:
       - All active heat pumps operate at the same part load ratio.
       - The combined efficiency is computed as a power-weighted average.
       - Operation with fewer heat pumps is no longer allowed once a
         higher cascade stage is available.

       This enforces a monotonic staging sequence:
       1 → 2 → 3 → … → n heat pumps.

    Interpolation is permitted within the operating envelope of each heat
    pump. Extrapolation outside the envelope is not allowed.

    Parameters
    ----------
    points_list : list of ndarray
        List of arrays, one per heat pump. Each array has shape (Ni, 2) and
        contains (primary_temperature, available_power) pairs.
    eff_list : list of ndarray
        List of efficiency arrays corresponding to `points_list`. Each array
        has shape (Ni,).

    Returns
    -------
    combined_points : ndarray of shape (K, 2)
        Combined array of (primary_temperature, available_power) pairs
        representing the equivalent operating envelope.
    combined_eff : ndarray of shape (K,)
        Efficiencies corresponding to `combined_points`.

    Notes
    -----
    - Multiple power levels per primary temperature are supported.
    - Each primary temperature is processed independently.
    - Once a cascade with k heat pumps is possible, operation with fewer
      heat pumps is strictly disallowed.
    - The output envelope represents physically allowed operating states
      under a strict cascade control philosophy.
    - The output format matches the input format.
    """

    def group_by_temperature(points, eff):
        """
        Group power and efficiency data by primary temperature.

        Parameters
        ----------
        points : ndarray of shape (N, 2)
            Array of (temperature, power) pairs.
        eff : ndarray of shape (N,)
            Efficiencies corresponding to `points`.

        Returns
        -------
        grouped : dict
            Dictionary keyed by temperature with values containing sorted
            power and efficiency arrays.
        """
        grouped = defaultdict(lambda: {"power": [], "eff": []})

        for (T, P), e in zip(points, eff):
            grouped[T]["power"].append(P)
            grouped[T]["eff"].append(e)

        for T in grouped:
            p = np.asarray(grouped[T]["power"])
            e = np.asarray(grouped[T]["eff"])
            idx = np.argsort(p)
            grouped[T]["power"] = p[idx]
            grouped[T]["eff"] = e[idx]

        return grouped

    def interp_eff(P, p_arr, e_arr):
        """
        Interpolate efficiency at a given power level.
        """
        return np.interp(P, p_arr, e_arr)

    def combine_at_temperature_n(
            hps,
            n_pl_single=25,
            n_pl_cascade=40
    ):
        """
    Combine multiple heat pumps at a fixed primary temperature using strict
    cascade staging and linspace-based part load discretization.

    Heat pumps are ordered by increasing minimum available power and combined
    according to the following rules:

    - Below the first cascade threshold, only single-machine operation is
      allowed.
    - A single overlap zone exists only between the two smallest heat pumps
      and only below the first cascade threshold.
    - Above each cascade threshold, exactly k heat pumps operate
      simultaneously.
    - Once a higher cascade stage is available, operation with fewer heat
      pumps is not permitted.

    Part load behavior is evaluated on uniform linspace grids to produce
    smooth operating envelopes.

    Parameters
    ----------
    hps : list of dict
        List of heat pump operating envelopes available at this temperature.
        Each dict contains:
        - "power" : ndarray
            Sorted array of available powers.
        - "eff" : ndarray
            Efficiencies corresponding to "power".
    n_pl_single : int, optional
        Number of part load points used for the single-machine overlap region
        between the two smallest heat pumps.
    n_pl_cascade : int, optional
        Number of part load points used for each cascade stage.

    Returns
    -------
    P_comb : ndarray
        Combined available powers at this temperature.
    E_comb : ndarray
        Corresponding combined efficiencies.

    Notes
    -----
    - All active heat pumps in a cascade stage operate at the same part load.
    - Combined efficiencies are computed as power-weighted averages.
    - Strict staging ensures that exactly one operating mode is valid for
      each power level.
    """
        # sort heat pumps by minimum power
        hps = sorted(hps, key=lambda hp: hp["power"][0])
        n = len(hps)

        p_min = [hp["power"][0] for hp in hps]
        p_max = [hp["power"][-1] for hp in hps]

        P_comb = []
        E_comb = []

        # -------------------------
        # zone 1: single HP1 only
        # -------------------------
        for P in hps[0]["power"]:
            if n == 1 or P < p_min[1]:
                P_comb.append(P)
                E_comb.append(
                    interp_eff(P, hps[0]["power"], hps[0]["eff"])
                )

        # -------------------------
        # overlap zone: HP1 vs HP2 ONLY
        # -------------------------
        if n >= 2:
            hp1 = hps[0]
            hp2 = hps[1]

            P_overlap_max = p_min[0] + p_min[1]

            pl_grid = np.linspace(0.0, 1.0, n_pl_single)

            for pl in pl_grid:
                P1 = p_min[0] + pl * (p_max[0] - p_min[0])
                P2 = p_min[1] + pl * (p_max[1] - p_min[1])

                candidates = []

                if p_min[0] <= P1 <= p_max[0]:
                    candidates.append(
                        (P1, interp_eff(P1, hp1["power"], hp1["eff"]))
                    )

                if p_min[1] <= P2 <= p_max[1]:
                    candidates.append(
                        (P2, interp_eff(P2, hp2["power"], hp2["eff"]))
                    )

                if not candidates:
                    continue

                P_best, E_best = max(candidates, key=lambda x: x[1])

                if P_best < P_overlap_max:
                    P_comb.append(P_best)
                    E_comb.append(E_best)

        # -------------------------
        # cascade zones: exactly k+1 machines
        # -------------------------
        for k in range(1, n):
            active = hps[:k + 1]

            P_min_stage = sum(p_min[:k + 1])
            P_max_stage = (
                sum(p_min[:k + 2]) if k + 1 < n else np.inf
            )

            pl_grid = np.linspace(0.0, 1.0, n_pl_cascade)

            for pl in pl_grid:
                powers = []
                effs = []

                for i, hp in enumerate(active):
                    Pi = p_min[i] + pl * (p_max[i] - p_min[i])
                    if Pi < p_min[i] or Pi > p_max[i]:
                        break
                    powers.append(Pi)
                    effs.append(
                        interp_eff(Pi, hp["power"], hp["eff"])
                    )
                else:
                    P_tot = sum(powers)

                    # STRICT staging window
                    if not (P_min_stage <= P_tot < P_max_stage):
                        continue

                    E_tot = np.dot(powers, effs) / P_tot

                    P_comb.append(P_tot)
                    E_comb.append(E_tot)

        # -------------------------
        # cleanup
        # -------------------------
        P_comb = np.asarray(P_comb)
        E_comb = np.asarray(E_comb)

        mask = np.isfinite(E_comb)
        idx = np.argsort(P_comb[mask])

        return P_comb[mask][idx], E_comb[mask][idx]

    # group each heat pump by temperature
    hp_groups = [
        group_by_temperature(points, eff)
        for points, eff in zip(points_list, eff_list)
    ]

    combined_points = []
    combined_eff = []

    # all temperatures across all heat pumps
    all_T = sorted(
        set().union(*[hp.keys() for hp in hp_groups])
    )

    for T in all_T:
        # collect all heat pumps available at this temperature
        hps_at_T = [
            hp[T] for hp in hp_groups if T in hp
        ]

        if not hps_at_T:
            continue

        if len(hps_at_T) == 1:
            # only one machine available
            P = hps_at_T[0]["power"]
            E = hps_at_T[0]["eff"]
        else:
            # multiple machines → combine
            P, E = combine_at_temperature_n(hps_at_T)

        for p, e in zip(P, E):
            combined_points.append((T, p))
            combined_eff.append(e)

    return np.asarray(combined_points), np.asarray(combined_eff)
