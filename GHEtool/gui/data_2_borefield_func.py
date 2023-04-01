"""
function to create a borefield class from a datastorage
"""
from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Tuple

import numpy as np

from GHEtool import Borefield, FluidData, GroundData, PipeData
from GHEtool.gui.gui_structure import load_data_GUI

if TYPE_CHECKING:  # pragma: no cover
    from numpy.typing import NDArray

    from ScenarioGUI.gui_classes.gui_data_storage import DataStorage


def data_2_borefield(ds: DataStorage) -> Tuple[Borefield, partial[[], None]]:
    # import bore field class from GHEtool and not in start up to save time
    from GHEtool import Borefield

    # create the bore field object
    borefield = Borefield(
        simulation_period=ds.option_simu_period,
        gui=True,
    )
    _set_boreholes(ds, borefield)
    # set temperature boundaries
    borefield.set_max_ground_temperature(ds.option_max_temp)  # maximum temperature
    borefield.set_min_ground_temperature(ds.option_min_temp)  # minimum temperature

    # set ground data
    borefield.set_ground_parameters(_create_ground_data(ds))

    # set peak lengths
    borefield.set_length_peak_cooling(ds.option_len_peak_cooling)
    borefield.set_length_peak_heating(ds.option_len_peak_heating)

    ### GENERAL SETUPS

    # check if Rb is a constant, otherwise set the fluid/pipe parameters
    if ds.option_method_rb_calc > 0:
    # Rb will be dynamically calculated
    # set fluid and pipe data
        borefield.set_fluid_parameters(_create_fluid_data(ds))
        borefield.set_pipe_parameters(_create_pipe_data(ds))

    # set monthly loads
    peak_heating, peak_cooling, monthly_load_heating, monthly_load_cooling = _create_monthly_loads_peaks(ds)
    borefield.set_peak_heating(peak_heating)
    borefield.set_peak_cooling(peak_cooling)
    borefield.set_baseload_heating(monthly_load_heating)
    borefield.set_baseload_cooling(monthly_load_cooling)

    # set hourly loads if available
    if ds.option_temperature_profile_hourly == 1:
        data_unit = ds.option_unit_data

        peak_heating, peak_cooling = load_data_GUI(
            filename=ds.option_filename,
            thermal_demand=ds.option_column,
            heating_load_column=ds.option_heating_column_text,
            cooling_load_column=ds.option_cooling_column_text,
            combined=ds.option_single_column_text,
            sep=";" if ds.option_seperator_csv == 0 else ",",
            dec="." if ds.option_decimal_csv == 0 else ",",
            fac=0.001 if data_unit == 0 else 1 if data_unit == 1 else 1000,
            hourly=True)

        # hourly data to be loaded
        borefield.set_hourly_heating_load(peak_heating)
        borefield.set_hourly_cooling_load(peak_cooling)

    # set up the borefield sizing
    borefield.sizing_setup(H_init=borefield.borefield[0].H,
                           use_constant_Rb=ds.option_method_rb_calc == 0,
                           use_constant_Tg=ds.option_method_temp_gradient == 0,
                           L2_sizing=ds.option_method_size_depth == 0,
                           L3_sizing=ds.option_method_size_depth == 1,
                           L4_sizing=ds.option_method_size_depth == 2)

    ### FUNCTIONALITIES (i.e. aims)

    # if load should be optimized do this
    if ds.aim_optimize:
        # optimize load profile without printing the results
        return borefield, partial(borefield.optimise_load_profile)

            ### Size borefield
    if ds.aim_req_depth:
        return borefield, partial(borefield.size)


        ### Size borefield by length and width
        # if ds.aim_size_length:
        #     try:
        #         # To be implemented
        #         # option_method_size_length
        #         pass
        #     except RuntimeError or ValueError:
        #         # save bore field in Datastorage
        #         ds.borefield = None
        #         # return Datastorage as signal
        #         self.any_signal.emit((ds, self.idx))
        #         return

        ### Plot temperature profile
    if ds.aim_temp_profile:
        return borefield, partial(borefield.calculate_temperatures, borefield.H)


def _set_boreholes(ds: DataStorage, borefield: Borefield) -> None:
    """
    This function creates the dataclasses (PipeData, FluidData and GroundData) based on entered values.
    These can be used in the calculation thread.

    Returns
    -------
    None
    """
    borefield.create_rectangular_borefield(ds.option_width, ds.option_length, ds.option_spacing, ds.option_spacing, ds.option_depth, ds.option_pipe_depth,
                                           ds.option_pipe_borehole_radius)


def _create_fluid_data(ds: DataStorage) -> FluidData:
    return FluidData(ds.option_fluid_mass_flow, ds.option_fluid_conductivity, ds.option_fluid_density, ds.option_fluid_capacity, ds.option_fluid_viscosity)


def _create_pipe_data(ds: DataStorage) -> PipeData:
    return PipeData(ds.option_pipe_grout_conductivity, ds.option_pipe_inner_radius, ds.option_pipe_outer_radius, ds.option_pipe_conductivity,
                    ds.option_pipe_distance, ds.option_pipe_number, ds.option_pipe_roughness)


def _calculate_flux(ds: DataStorage) -> float:
    """
    This function calculates the geothermal flux.
    This is calculated based on:

    temperature gradient [K/100m] * conductivity [W/mK] / 100
    = temperature gradient [K/m] * conductivity [W/mK]

    Returns
    -------
    Geothermal flux : float
        Geothermal flux in [W/m2]
    """
    return ds.option_temp_gradient * ds.option_conductivity / 100


def _create_ground_data(ds: DataStorage) -> GroundData:
    return GroundData(ds.option_conductivity, ds.option_ground_temp if ds.option_method_temp_gradient == 0 else ds.option_ground_temp_gradient,
                      ds.option_constant_rb, ds.option_heat_capacity * 1000, _calculate_flux(ds))


def _create_monthly_loads_peaks(ds: DataStorage) -> Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    peak_heating: NDArray[np.float64] = np.array([ds.option_hp_jan, ds.option_hp_feb, ds.option_hp_mar, ds.option_hp_apr, ds.option_hp_may, ds.option_hp_jun,
                                                    ds.option_hp_jul, ds.option_hp_aug, ds.option_hp_sep, ds.option_hp_oct, ds.option_hp_nov, ds.option_hp_dec])
    peak_cooling: NDArray[np.float64] = np.array([ds.option_cp_jan, ds.option_cp_feb, ds.option_cp_mar, ds.option_cp_apr, ds.option_cp_may, ds.option_cp_jun,
                              ds.option_cp_jul, ds.option_cp_aug, ds.option_cp_sep, ds.option_cp_oct, ds.option_cp_nov, ds.option_cp_dec])
    monthly_load_heating: NDArray[np.float64] = np.array([ds.option_hl_jan, ds.option_hl_feb, ds.option_hl_mar, ds.option_hl_apr, ds.option_hl_may, ds.option_hl_jun,
                                     ds.option_hl_jul, ds.option_hl_aug, ds.option_hl_sep, ds.option_hl_oct, ds.option_hl_nov, ds.option_hl_dec])
    monthly_load_cooling: NDArray[np.float64] = np.array([ds.option_cl_jan, ds.option_cl_feb, ds.option_cl_mar, ds.option_cl_apr, ds.option_cl_may, ds.option_cl_jun,
                                     ds.option_cl_jul, ds.option_cl_aug, ds.option_cl_sep, ds.option_cl_oct, ds.option_cl_nov, ds.option_cl_dec])
    return peak_heating, peak_cooling, monthly_load_heating, monthly_load_cooling
