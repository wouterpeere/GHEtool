import itertools

import matplotlib.pyplot as plt
import numpy as np

from collections import defaultdict
from GHEtool.VariableClasses.BaseClass import BaseClass
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
from scipy.interpolate import interpn
from typing import Union


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
                 nominal_power: float = None,
                 default_secondary_temperature: float = None):
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
        default_secondary_temperature : float
            Default average temperature at the secondary side of the heat pump. This is used to calculate the correct efficiency
            in for example heating or dhw [°C]

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
        self._default_secondary_temperature: float = default_secondary_temperature

        self._range_primary: np.ndarray = np.array([])
        self._range_secondary: np.ndarray = np.array([])
        self._range_part_load: np.ndarray = np.array([])

        if not np.all(data > 0):
            raise ValueError('The efficiencies should all be above zero!')

        if len(data) != len(coordinates):
            raise ValueError('The provided data and coordinates array are not of the same length!')

        dimensions = 1 if isinstance(coordinates[0], (int, float, np.int32, np.int64, np.float16, np.float32)) else len(
            coordinates[0])
        if dimensions != 1 + self._has_secondary + self._has_part_load:
            raise ValueError(f'The provided coordinate data has {dimensions} dimensions whereas '
                             f'{1 + self._has_secondary + self._has_part_load} dimensions where provided.'
                             'Please check the nb_of_points for both secondary temperature and part load.')

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

        if dimensions == 3:
            self._data = self._delaunay_fill_grid(
                coordinates, data, (self._range_primary, self._range_secondary, self._range_part_load)
            )

            # get max powers per temperature (unchanged — not related to find_value)
            x = coordinates[:, 0]
            y = coordinates[:, 1]
            z = coordinates[:, 2]

            ix = np.searchsorted(self._range_primary, x)
            iy = np.searchsorted(self._range_secondary, y)

            flat_idx = ix * len(self._range_secondary) + iy

            max_z_flat = np.full(len(self._range_primary) * len(self._range_secondary), -np.inf)
            np.maximum.at(max_z_flat, flat_idx, z)
            max_z = max_z_flat.reshape(len(self._range_primary), len(self._range_secondary))
            self._max_part_load = self._finalize_part_load(max_z, (self._range_primary, self._range_secondary))

            min_z_flat = np.full(len(self._range_primary) * len(self._range_secondary), np.inf)
            np.minimum.at(min_z_flat, flat_idx, z)
            min_z = min_z_flat.reshape(len(self._range_primary), len(self._range_secondary))
            self._min_part_load = self._finalize_part_load(min_z, (self._range_primary, self._range_secondary))
        elif dimensions == 2:
            secondary_axis = self._range_secondary if self._has_secondary else self._range_part_load
            self._data = self._delaunay_fill_grid(
                coordinates, data, (self._range_primary, secondary_axis)
            )

            if not self._has_secondary:
                # get max powers per temperature (unchanged)
                x = coordinates[:, 0]
                y = coordinates[:, 1]

                idx = np.searchsorted(self._range_primary, x)

                max_y = np.full(len(self._range_primary), -np.inf)
                np.maximum.at(max_y, idx, y)
                self._max_part_load = self._finalize_part_load(max_y, (self._range_primary,))

                min_y = np.full(len(self._range_primary), np.inf)
                np.minimum.at(min_y, idx, y)
                self._min_part_load = self._finalize_part_load(min_y, (self._range_primary,))
        else:
            p = self._range_primary.argsort()
            self._data = data[p]

        if nominal_power is not None and reference_nominal_power is None:
            raise ValueError('Please enter a reference nominal power.')

        if self._has_part_load and nominal_power is not None:
            self._range_part_load *= nominal_power / reference_nominal_power
            self._max_part_load *= nominal_power / reference_nominal_power

        self._lower = np.array([p[0] for p in self._points])
        self._upper = np.array([p[-1] for p in self._points])

    @staticmethod
    def _finalize_part_load(max_arr: np.ndarray, axes: tuple) -> np.ndarray:
        """
        Replaces +/-inf placeholder cells (primary/secondary combinations with
        no underlying data) with a nearest-neighbor estimate from populated
        cells, so the array is fully finite before being handed to interpn.
        Works for both the max- and min-part-load arrays.
        """
        finite_mask = np.isfinite(max_arr)
        if finite_mask.all():
            return max_arr

        if len(axes) == 1:  # pragma: no cover
            grid_points = axes[0].reshape(-1, 1)
        else:
            mesh = np.meshgrid(*axes, indexing='ij')
            grid_points = np.column_stack([m.ravel() for m in mesh])

        flat = max_arr.ravel().copy()
        flat_finite_mask = finite_mask.ravel()

        nearest = NearestNDInterpolator(grid_points[flat_finite_mask], flat[flat_finite_mask])
        flat[~flat_finite_mask] = nearest(grid_points[~flat_finite_mask])

        return flat.reshape(max_arr.shape)

    @staticmethod
    def _normalize_coords(coordinates: np.ndarray):
        """
        Min-max normalizes each column of `coordinates` to [0, 1], so that
        Delaunay triangulation isn't distorted by axes with very different
        numeric ranges (e.g. temperature in single digits vs. power in tens).
        Returns the normalized coordinates plus (mins, ranges) so the same
        transform can be applied to query points.
        """
        mins = coordinates.min(axis=0)
        ranges = coordinates.max(axis=0) - mins
        ranges[ranges == 0] = 1.0  # guard against degenerate constant axes
        return (coordinates - mins) / ranges, mins, ranges

    @staticmethod
    def _delaunay_fill_grid(coordinates: np.ndarray, data: np.ndarray, axes: tuple) -> np.ndarray:
        """
        Builds a complete rectilinear grid over `axes` from scattered
        (coordinates, data), filling missing nodes via Delaunay-based linear
        interpolation, falling back to nearest-neighbor for nodes outside the
        convex hull. Degenerate coordinate dimensions (zero range -- e.g. a
        dataset tested at a single fixed secondary temperature) are dropped
        before triangulation, since Delaunay cannot triangulate points that
        don't span all given dimensions, and re-inserted afterward.
        """
        coordinates = np.asarray(coordinates, dtype=float)

        ranges = coordinates.max(axis=0) - coordinates.min(axis=0)
        varying = ranges > 0
        n_varying = varying.sum()

        mesh = np.meshgrid(*axes, indexing='ij')
        grid_points_full = np.column_stack([m.ravel() for m in mesh])

        existing = {tuple(row): val for row, val in zip(coordinates, data)}

        values = np.empty(len(grid_points_full))
        missing_mask = np.zeros(len(grid_points_full), dtype=bool)
        for i, pt in enumerate(grid_points_full):
            key = tuple(pt)
            if key in existing:
                values[i] = existing[key]
            else:
                missing_mask[i] = True

        if missing_mask.any():
            missing_pts_full = grid_points_full[missing_mask]

            if n_varying == 0:
                values[missing_mask] = data[0]
            else:
                coords_reduced = coordinates[:, varying]
                missing_reduced = missing_pts_full[:, varying]

                if n_varying == 1:
                    order = np.argsort(coords_reduced[:, 0])
                    est = np.interp(missing_reduced[:, 0],
                                    coords_reduced[order, 0], data[order])
                else:
                    # CHANGED: normalize both the fitting points and the query
                    # points onto [0, 1] per axis before triangulating, so
                    # Teva (small range) and power (large range) get equal
                    # geometric weight in the Delaunay triangulation
                    coords_norm, mins, ranges_norm = _Efficiency._normalize_coords(coords_reduced)
                    missing_norm = (missing_reduced - mins) / ranges_norm

                    linear = LinearNDInterpolator(coords_norm, data)
                    est = linear(missing_norm)
                    nan_mask = np.isnan(est)
                    if nan_mask.any():
                        nearest = NearestNDInterpolator(coords_norm, data)
                        est[nan_mask] = nearest(missing_norm[nan_mask])

                values[missing_mask] = est

        grid_shape = tuple(len(a) for a in axes)
        return values.reshape(grid_shape)

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
            if self._has_secondary and self._default_secondary_temperature is None:
                raise ValueError('The efficiency class requires a value for the secondary temperature.')
        if self._has_part_load != (power is not None):
            if self._has_part_load:
                raise ValueError('The efficiency class requires a value for the part-load.')

        # get maximum length
        _max_length = np.max([len(i) if i is not None and not isinstance(i, (float, int)) else 1 for i in
                              (primary_temperature, secondary_temperature, power)])

        # convert to arrays
        primary_temperature = np.array(
            np.full(_max_length, primary_temperature) if isinstance(primary_temperature,
                                                                    (float, int)) else primary_temperature)
        if secondary_temperature is not None:
            secondary_temperature = np.array(
                np.full(_max_length, secondary_temperature) if isinstance(secondary_temperature,
                                                                          (float, int)) else secondary_temperature)
        elif self._default_secondary_temperature is not None:
            secondary_temperature = np.full(_max_length, self._default_secondary_temperature)

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

            # make sure it stays below the maximum available power
            part_load_clipped = np.minimum(part_load_clipped,
                                           self._get_max_power(primary_temperature, secondary_temperature))
            # make sure it stays above the minimum available power
            part_load_clipped = np.maximum(part_load_clipped,
                                           self._get_min_power(primary_temperature, secondary_temperature, ))
        xi = primary_temperature_clipped
        if self._has_part_load and self._has_secondary:
            xi = list(zip(primary_temperature_clipped, secondary_temperature_clipped, part_load_clipped))
        elif self._has_secondary:
            xi = list(zip(primary_temperature_clipped, secondary_temperature_clipped))
        elif self._has_part_load:
            xi = list(zip(primary_temperature_clipped, part_load_clipped))

        xi = np.clip(xi, self._lower, self._upper)

        interp = interpn(self._points, self._data, xi, bounds_error=False, fill_value=np.nan)
        if not np.isnan(interp).any():
            return interp

    def _get_max_power(self,
                       primary_temperature: Union[float, np.ndarray],
                       secondary_temperature: Union[float, np.ndarray] = None, **kwargs) -> np.ndarray:
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
                if self._default_secondary_temperature is None:
                    raise ValueError("Secondary temperature is required.")
                else:
                    secondary_temperature = self._default_secondary_temperature

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

        return interpn(self._points[:1 + self._has_secondary], self._max_part_load, xi, bounds_error=False,
                       fill_value=np.nan)

    def _get_min_power(self,
                       primary_temperature: Union[float, np.ndarray],
                       secondary_temperature: Union[float, np.ndarray] = None, **kwargs) -> np.ndarray:
        """
        This function returns the minimum available power for a certain primary and secondary temperature.

        Parameters
        ----------
        primary_temperature : np.ndarray or float
            Value(s) for the average primary temperature of the heat pump for the efficiency calculation.
        secondary_temperature : np.ndarray or float
            Value(s) for the average secondary temperature of the heat pump for the efficiency calculation.

        Raises
        ------
        ValueError
            When secondary_temperature is in the dataset, and it is not provided.

        Returns
        -------
        Efficiency
            np.ndarray
        """
        if not self._has_part_load:
            return self._get_max_power(primary_temperature, secondary_temperature)

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

        Tp = np.clip(Tp, np.min(self._range_primary), np.max(self._range_primary))
        if self._has_secondary:
            Ts = np.clip(Ts, np.min(self._range_secondary), np.max(self._range_secondary))

        xi = list(zip(Tp, Ts)) if self._has_secondary else Tp

        return interpn(self._points[:1 + self._has_secondary], self._min_part_load, xi, bounds_error=False,
                       fill_value=np.nan)


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

    if ax is None:
        fig, ax = plt.subplots()

    # group by temperature
    grouped = defaultdict(lambda: {"power": [], "eff": []})

    for (T, _, P), e in zip(points, eff):
        if _ == 32.5:
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


def combine_n_heat_pumps(points_list, eff_list,
                         reference_primary_temperature: float = 0.0,
                         reference_secondary_temperature: float = 35.0,
                         n_pl_single: int = 3, n_pl_cascade: int = 10,
                         kwargs_list=None):
    """
    Vectorized version of combine_n_heat_pumps.

    Same signature/behaviour as the original, but:
      - p_min / p_max are queried once per machine across ALL combos in a
        single batched call (instead of once per combo per machine).
      - efficiency queries within a combo are vectorized over the pl grid
        (instead of one scalar call per pl step).
      - CAPPING instead of exclusion: a machine is never dropped from a
        combo just because the combo's (Teva, Tcond) falls outside that
        machine's own tested envelope. Instead, the query point is CLAMPED
        to that machine's own tested range before calling
        _get_min_power/_get_max_power/_get_efficiency, so the machine is
        assumed to plateau at its boundary performance rather than either
        vanishing from the combined envelope entirely, or being
        extrapolated by the interpolator beyond data it was never tested
        on. Every machine therefore contributes at every combo.
    """
    from GHEtool.VariableClasses.Efficiency.COP import COP

    if kwargs_list is None:  # pragma: no cover
        kwargs_list = [{'secondary': True, 'part_load': True} for _ in points_list]

    cops = [COP(data=np.array(eff), coordinates=np.array(pts), **kw)
            for pts, eff, kw in zip(points_list, eff_list, kwargs_list)]

    # rank order, established once at the reference regime (clamped per
    # machine in case the reference point itself sits outside some
    # machine's tested envelope)
    rank_key = [
        float(np.atleast_1d(cop._get_min_power(
            np.clip(reference_primary_temperature, cop._range_primary.min(), cop._range_primary.max()),
            np.clip(reference_secondary_temperature, cop._range_secondary.min(), cop._range_secondary.max()),
        ))[0])
        for cop in cops
    ]
    cops = [cops[i] for i in np.argsort(rank_key)]
    n = len(cops)

    # all (Teva, Tcond) combinations across all machines
    all_combos = set()
    for cop in cops:
        all_combos.update(itertools.product(cop._range_primary, cop._range_secondary))
    all_combos = np.array(sorted(all_combos))  # (Ncombo, 2)
    Teva_arr, Tcond_arr = all_combos[:, 0], all_combos[:, 1]
    n_combo = len(all_combos)

    # --- batch p_min / p_max per machine across ALL combos, one call each,
    # clamping each machine's query point to its own tested range ---
    p_min_mat = np.full((n, n_combo), np.nan)
    p_max_mat = np.full((n, n_combo), np.nan)
    Teva_clamped_mat = np.empty((n, n_combo))
    Tcond_clamped_mat = np.empty((n, n_combo))
    coverage = np.zeros((n, n_combo), dtype=bool)

    for i, cop in enumerate(cops):
        Teva_c = np.clip(Teva_arr, cop._range_primary.min(), cop._range_primary.max())
        Tcond_c = np.clip(Tcond_arr, cop._range_secondary.min(), cop._range_secondary.max())
        Teva_clamped_mat[i] = Teva_c
        Tcond_clamped_mat[i] = Tcond_c

        pmin = np.atleast_1d(cop._get_min_power(Teva_c, Tcond_c))
        pmax = np.atleast_1d(cop._get_max_power(Teva_c, Tcond_c))
        valid = np.isfinite(pmin) & np.isfinite(pmax) & (pmax >= pmin)

        idx = np.where(valid)[0]
        p_min_mat[i, idx] = pmin[valid]
        p_max_mat[i, idx] = pmax[valid]
        coverage[i, idx] = True

    combined_points = []
    combined_eff = []

    for c in range(n_combo):
        Teva, Tcond = Teva_arr[c], Tcond_arr[c]
        active = np.where(coverage[:, c])[0]
        if len(active) == 0:  # pragma: no cover
            continue

        P, E = _combine_at_combo_vector(
            [cops[i] for i in active],
            p_min_mat[active, c], p_max_mat[active, c],
            Teva_clamped_mat[active, c], Tcond_clamped_mat[active, c],
            n_pl_single, n_pl_cascade,
        )
        if len(P) == 0:  # pragma: no cover
            continue
        combined_points.append(np.column_stack(
            [np.full_like(P, Teva), np.full_like(P, Tcond), P]))
        combined_eff.append(E)

    if not combined_points:  # pragma: no cover
        return np.empty((0, 3)), np.empty(0)

    return np.vstack(combined_points), np.concatenate(combined_eff)


def _combine_at_combo_vector(active_cops, p_min, p_max, Teva_c, Tcond_c, n_pl_single, n_pl_cascade):
    """
    active_cops : list of COP objects active at this combo
    p_min, p_max : arrays, shape (n,) -- per-machine min/max power, already
        evaluated at each machine's own clamped (Teva_c[i], Tcond_c[i])
    Teva_c, Tcond_c : arrays, shape (n,) -- the clamped query point used for
        machine i (may differ machine to machine when the combo's true
        (Teva, Tcond) falls outside some machines' tested range)
    """
    n = len(active_cops)

    def eff_at(i, P):
        Teva_b = np.full_like(P, Teva_c[i], dtype=float)
        Tcond_b = np.full_like(P, Tcond_c[i], dtype=float)
        return np.atleast_1d(active_cops[i]._get_efficiency(Teva_b, Tcond_b, P))

    P_comb, E_comb = [], []
    two_machine_min = np.sort(p_min)[:2].sum() if n >= 2 else np.inf

    # --- single-machine zone: vectorized over pl, per machine ---
    pl_grid = np.linspace(0.0, 1.0, n_pl_single)
    for i in range(n):
        P = p_min[i] + pl_grid * (p_max[i] - p_min[i])
        mask = P < two_machine_min
        if not mask.any():  # pragma: no cover
            continue
        P_valid = P[mask]
        E_comb.append(eff_at(i, P_valid))
        P_comb.append(P_valid)

    # --- cascade zones: exactly k+1 machines active, sorted by p_min ---
    # Key insight: machine j's power/efficiency curve over the pl grid does
    # NOT depend on which stage k it appears in -- only on j itself. So
    # instead of recomputing eff_at(j, ...) once per stage it participates
    # in (O(n^2) calls total), compute it ONCE per machine (O(n) calls) and
    # get every stage's sum via a cumulative sum over machines.
    order = np.argsort(p_min)
    p_min_sorted, p_max_sorted, idx_sorted = p_min[order], p_max[order], order
    pl_grid_c = np.linspace(0.0, 1.0, n_pl_cascade)

    # stage_powers[j, :] / stage_effs[j, :] = machine j's (P, E) curve over pl_grid_c
    stage_powers = p_min_sorted[:, None] + pl_grid_c[None, :] * (p_max_sorted - p_min_sorted)[:, None]
    stage_effs = np.empty((n, n_pl_cascade))
    for j in range(n):
        stage_effs[j] = eff_at(idx_sorted[j], stage_powers[j])

    # cumulative sums over machines (in ascending p_min order) give, for
    # each k, the combined power/weighted-efficiency of machines 0..k
    cum_P = np.cumsum(stage_powers, axis=0)  # cum_P[k] = sum_{j<=k} Pi[j]
    cum_PE = np.cumsum(stage_powers * stage_effs, axis=0)

    p_min_cumsum = np.cumsum(p_min_sorted)  # p_min_cumsum[k] = sum_{j<=k} p_min[j]

    for k in range(1, n):
        P_min_stage = p_min_cumsum[k]
        P_max_stage = p_min_cumsum[k + 1] if k + 1 < n else np.inf

        P_tot = cum_P[k]
        E_tot = cum_PE[k] / P_tot

        mask = (P_tot >= P_min_stage) & (P_tot < P_max_stage) & np.isfinite(E_tot)
        if mask.any():
            P_comb.append(P_tot[mask])
            E_comb.append(E_tot[mask])

    if not P_comb:  # pragma: no cover
        return np.empty(0), np.empty(0)

    P_comb = np.concatenate(P_comb)
    E_comb = np.concatenate(E_comb)
    valid = np.isfinite(E_comb) & np.isfinite(P_comb)
    order = np.argsort(P_comb[valid])
    return P_comb[valid][order], E_comb[valid][order]


def _find_optimal_heat_pump_configuration(heat_pumps: list[_Efficiency], power: float, prim_temp: float,
                                          sec_temp: float = None) -> list:
    """
    This function finds the required combination of different heat pumps to be able to deliver the required power
    at a certain primary (and secondary) temperature.

    Parameters
    ----------
    heat_pumps : list
        List of efficiency objects
    power : float
        Required power [kW]
    prim_temp : float
        Primary temperature at which the power is required [°C]
    sec_temp : float
        Secondary temperature at which the power is required [°C]

    Returns
    -------
    list
        List with the number of heat pumps required for a certain power.
    """

    best = None
    n = len(heat_pumps)

    heat_pump_max_powers = [heat_pump._get_max_power(primary_temperature=prim_temp, secondary_temperature=sec_temp)[0]
                            for
                            heat_pump in heat_pumps]

    for mask in itertools.product([0, 1], repeat=n):
        mask = np.array(mask)
        total = heat_pump_max_powers @ mask
        if total >= power:
            units = mask.sum()
            overshoot = total - power
            candidate = (units, overshoot, -total)
            if best is None or candidate < best:
                best = candidate
                best_mask = mask

    return best_mask
