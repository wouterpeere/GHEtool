import numpy as np
from scipy.interpolate import RegularGridInterpolator


def build_Rb_interpolator(
        borefield,
        mfr_range,  # (min, max) flow rate per borehole, kg/s
        temperature_range,  # (min, max) temperature, °C
        n_mfr=500,
        n_temperature=500,
):
    """
    Precompute Rb on a (temperature x flow_rate) grid and return a fast interpolator.

    Parameters
    ----------
    mfr_range : tuple
        (min, max) flow rate per borehole in kg/s. Should comfortably span the
        actual range produced by borefield.flow_data.mfr_borefield(...) / n_boreholes,
        including the clamped minimum flow rate.
    temperature_range : tuple
        (min, max) fluid temperature in °C.

    Returns
    -------
    interp : RegularGridInterpolator
        Call as interp(np.column_stack([temp_query, mfr_query])).
    temp_grid, mfr_grid : np.ndarray
        The 1D axes used to build the grid (for bounds-checking / diagnostics).
    """
    temp_grid = np.linspace(*temperature_range, n_temperature)
    mfr_grid = np.linspace(*mfr_range, n_mfr)

    # Cartesian grid; 'ij' indexing keeps reshape consistent with (temperature, mfr) order.
    T_mesh, MFR_mesh = np.meshgrid(temp_grid, mfr_grid, indexing='ij')
    T_flat = T_mesh.ravel()
    MFR_flat = MFR_mesh.ravel()

    k_s_flat = borefield.ground_data.k_s(borefield.depth, borefield.D)
    if np.ndim(k_s_flat) > 0:
        k_s_flat = np.broadcast_to(k_s_flat, T_flat.shape)

    Rb_flat = borefield.borehole.get_Rb(
        borefield.H, borefield.D, borefield.r_b, k_s_flat,
        borefield.depth, use_explicit_models=True,
        nb_of_boreholes=borefield.number_of_boreholes,
        temperature=T_flat, mfr_borehole=MFR_flat,
    )

    Rb_grid = np.asarray(Rb_flat).reshape(n_temperature, n_mfr)

    interp = RegularGridInterpolator(
        (temp_grid, mfr_grid), Rb_grid,
        method='linear',  # 'cubic'/'quintic' available if you want smoother Rb
        bounds_error=False,  # extrapolate rather than raise outside the grid...
        fill_value=None,  # ...set to np.nan instead if you'd rather be warned
    )
    return interp, temp_grid, mfr_grid
