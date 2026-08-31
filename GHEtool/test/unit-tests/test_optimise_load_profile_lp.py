"""
Tests for the LP-based hybrid dispatch optimisation.
"""
import numpy as np
import pytest

from GHEtool import Borefield, GroundConstantTemperature, HourlyBuildingLoad, FOLDER, COP
from GHEtool.Methods import optimise_load_profile_lp

TMIN, TMAX = 0., 16.


def _demand():
    import pandas as pd
    df = pd.read_csv(FOLDER.joinpath('Examples/hourly_profile.csv'), sep=';')
    return np.array(df.iloc[:, 0]), np.array(df.iloc[:, 1])


def _borefield(load) -> Borefield:
    borefield = Borefield(load=load, ground_data=GroundConstantTemperature(3, 10))
    borefield.create_rectangular_borefield(10, 12, 6, 6, 150, 4, 0.075)
    borefield.Rb = 0.12
    borefield.set_max_fluid_temperature(TMAX)
    borefield.set_min_fluid_temperature(TMIN)
    return borefield


def test_energy_objective_certified_and_bounded():
    dem_h, dem_c = _demand()
    load = HourlyBuildingLoad(dem_h, dem_c, 10, 4., 20.)
    served, external, info = optimise_load_profile_lp(_borefield(load), load, objective='energy',
                                                      return_shadow_prices=True)
    # served + external = demand, all within bounds
    assert np.all(served.hourly_heating_load >= -1e-9)
    assert np.all(served.hourly_cooling_load >= -1e-9)
    assert np.allclose(served.hourly_heating_load + external.hourly_heating_load, dem_h)
    assert np.allclose(served.hourly_cooling_load + external.hourly_cooling_load, dem_c)
    # certified temperatures respect the band
    t_min, t_max = info['certified_temperature_range']
    assert TMIN - 0.025 <= t_min and t_max <= TMAX + 0.025
    # a binding problem: something is served, something is shaved
    served_energy = np.sum(served.hourly_heating_load) + np.sum(served.hourly_cooling_load)
    total_energy = np.sum(dem_h) + np.sum(dem_c)
    assert 0.5 * total_energy < served_energy < total_energy
    # shadow prices: nonnegative and at least one binding constraint
    assert len(info['temperature_constraints']) > 0
    assert all(s['shadow_price'] >= -1e-9 for s in info['temperature_constraints'])
    assert info['marginal_objective_value_per_meter'] >= 0.


def test_power_objective_dominates_on_capacity():
    dem_h, dem_c = _demand()
    load = HourlyBuildingLoad(dem_h, dem_c, 10, 4., 20.)
    served_e, external_e = optimise_load_profile_lp(_borefield(load), load, objective='energy')
    served_p, external_p = optimise_load_profile_lp(_borefield(load), load, objective='power')

    def caps(external):
        return max(np.max(external.hourly_heating_load), 0.), max(np.max(external.hourly_cooling_load), 0.)

    cap_e = sum(caps(external_e))
    cap_p = sum(caps(external_p))
    # the capacity objective can never need more backup capacity than the energy objective
    assert cap_p <= cap_e + 1e-6


def test_invalid_inputs_raise():
    dem_h, dem_c = _demand()
    cop = COP(np.array([2., 3., 4., 5., 6.]), np.array([-5., 0., 5., 10., 15.]))
    load_var = HourlyBuildingLoad(dem_h, dem_c, 10, cop, 20.)
    with pytest.raises(ValueError):
        optimise_load_profile_lp(_borefield(load_var), load_var)
    load = HourlyBuildingLoad(dem_h, dem_c, 10, 4., 20.)
    with pytest.raises(ValueError):
        optimise_load_profile_lp(_borefield(load), load, objective='cost')
