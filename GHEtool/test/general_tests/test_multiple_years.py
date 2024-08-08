import logging

import numpy as np
import pygfunction as gt
import pandas as pd

from GHEtool import Borefield, FOLDER, GroundConstantTemperature, HourlyGeothermalLoadMultiYear, \
    MonthlyGeothermalLoadMultiYear


def test_multiple_years_L4():
    load_factor = 7
    data = GroundConstantTemperature(3, 10)
    borefield_gt = gt.boreholes.rectangle_field(10, 12, 6, 6, 110, 1, 0.075)
    borefield = Borefield()
    borefield.set_ground_parameters(data)
    borefield.Rb = 0.12
    borefield.set_borefield(borefield_gt)
    borefield.set_min_avg_fluid_temperature(0)
    borefield.set_max_avg_fluid_temperature(17)
    load = pd.read_csv(FOLDER.joinpath("test/methods/hourly_data/multiple_years.csv"), sep=",")
    # load["heating"][8760*25:] = 0
    hourly_load = HourlyGeothermalLoadMultiYear(load["heating"].clip(0) * load_factor,
                                                load["cooling"].clip(0) * load_factor)
    borefield.load = hourly_load
    assert np.allclose(borefield.load.hourly_extraction_load_simulation_period, load["heating"].clip(0) * load_factor)
    assert np.allclose(borefield.load.hourly_injection_load_simulation_period, load["cooling"].clip(0) * load_factor)
    assert np.allclose(borefield.load.hourly_load_simulation_period,
                       load["cooling"].clip(0) * load_factor - load["heating"].clip(0) * load_factor)
    h = borefield.size_L4(150)
    assert np.isclose(h, 114.912, rtol=0.001)
    load["heating"][8760 * 25:] = 0
    hourly_load = HourlyGeothermalLoadMultiYear(load["heating"].clip(0) * load_factor,
                                                load["cooling"].clip(0) * load_factor)
    borefield.load = hourly_load
    assert np.allclose(borefield.load.hourly_extraction_load_simulation_period, load["heating"].clip(0) * load_factor)
    assert np.allclose(borefield.load.hourly_injection_load_simulation_period, load["cooling"].clip(0) * load_factor)
    assert np.allclose(borefield.load.hourly_load_simulation_period,
                       load["cooling"].clip(0) * load_factor - load["heating"].clip(0) * load_factor)
    h = borefield.size_L4(150)
    assert np.isclose(h, 101.836, rtol=0.001)


def test_multiple_years_L3():
    load_factor = 7
    data = GroundConstantTemperature(3, 10)
    borefield_gt = gt.boreholes.rectangle_field(10, 12, 6, 6, 110, 1, 0.075)
    borefield = Borefield()
    borefield.set_ground_parameters(data)
    borefield.Rb = 0.12
    borefield.set_borefield(borefield_gt)
    borefield.set_min_avg_fluid_temperature(0)
    borefield.set_max_avg_fluid_temperature(17)
    load = pd.read_csv(FOLDER.joinpath("test/methods/hourly_data/multiple_years.csv"), sep=",")
    hourly_load = HourlyGeothermalLoadMultiYear(load["heating"].clip(0) * load_factor,
                                                load["cooling"].clip(0) * load_factor)
    borefield.load = hourly_load
    monthly_heating_load = np.array([np.mean((load["heating"].clip(0) * load_factor)[i - 730:i]) for i in
                                     range(730, len(load["heating"]) + 1, 730)])
    monthly_cooling_load = np.array([np.mean((load["cooling"].clip(0) * load_factor)[i - 730:i]) for i in
                                     range(730, len(load["cooling"]) + 1, 730)])
    peak_extraction = [np.max((load["heating"].clip(0) * load_factor)[i - 730:i]) for i in
                       range(730, len(load["heating"]) + 1, 730)]
    peak_injection = [np.max((load["cooling"].clip(0) * load_factor)[i - 730:i]) for i in
                      range(730, len(load["cooling"]) + 1, 730)]
    assert np.allclose(borefield.load.monthly_baseload_extraction_power_simulation_period, monthly_heating_load)
    assert np.allclose(borefield.load.monthly_baseload_injection_power_simulation_period, monthly_cooling_load)
    assert np.allclose(borefield.load.monthly_baseload_extraction_simulation_period, monthly_heating_load * 730)
    assert np.allclose(borefield.load.monthly_baseload_injection_simulation_period, monthly_cooling_load * 730)
    assert np.allclose(borefield.load.monthly_peak_extraction_simulation_period, peak_extraction)
    assert np.allclose(borefield.load.monthly_peak_injection_simulation_period, peak_injection)
    assert np.allclose(borefield.load.monthly_average_injection_power_simulation_period,
                       monthly_cooling_load - monthly_heating_load)
    h = borefield.size_L3(150)
    assert np.isclose(h, 110.233, rtol=0.001)
    load["heating"][8760 * 25:] = 0
    hourly_load = HourlyGeothermalLoadMultiYear(load["heating"].clip(0) * load_factor,
                                                load["cooling"].clip(0) * load_factor)
    borefield.load = hourly_load
    monthly_heating_load = np.array([np.mean((load["heating"].clip(0) * load_factor)[i - 730:i]) for i in
                                     range(730, len(load["heating"]) + 1, 730)])
    monthly_cooling_load = np.array([np.mean((load["cooling"].clip(0) * load_factor)[i - 730:i]) for i in
                                     range(730, len(load["cooling"]) + 1, 730)])
    peak_extraction = [np.max((load["heating"].clip(0) * load_factor)[i - 730:i]) for i in
                       range(730, len(load["heating"]) + 1, 730)]
    peak_injection = [np.max((load["cooling"].clip(0) * load_factor)[i - 730:i]) for i in
                      range(730, len(load["cooling"]) + 1, 730)]
    assert np.allclose(borefield.load.monthly_baseload_extraction_power_simulation_period, monthly_heating_load)
    assert np.allclose(borefield.load.monthly_baseload_injection_power_simulation_period, monthly_cooling_load)
    assert np.allclose(borefield.load.monthly_peak_extraction_simulation_period, peak_extraction)
    assert np.allclose(borefield.load.monthly_peak_injection_simulation_period, peak_injection)
    assert np.allclose(borefield.load.monthly_average_injection_power_simulation_period,
                       monthly_cooling_load - monthly_heating_load)
    h = borefield.size_L3(150)
    assert np.isclose(h, 100.418, rtol=0.001)


def test_multiple_years_L3_monthly_data():
    load_factor = 7
    data = GroundConstantTemperature(3, 10)
    borefield_gt = gt.boreholes.rectangle_field(10, 12, 6, 6, 110, 1, 0.075)
    borefield = Borefield()
    borefield.set_ground_parameters(data)
    borefield.Rb = 0.12
    borefield.set_borefield(borefield_gt)
    borefield.set_min_avg_fluid_temperature(0)
    borefield.set_max_avg_fluid_temperature(17)
    load = pd.read_csv(FOLDER.joinpath("test/methods/hourly_data/multiple_years.csv"), sep=",")
    monthly_heating_load = np.array([np.mean((load["heating"].clip(0) * load_factor)[i - 730:i]) for i in
                                     range(730, len(load["heating"]) + 1, 730)])
    monthly_cooling_load = np.array([np.mean((load["cooling"].clip(0) * load_factor)[i - 730:i]) for i in
                                     range(730, len(load["cooling"]) + 1, 730)])
    peak_extraction = [np.max((load["heating"].clip(0) * load_factor)[i - 730:i]) for i in
                       range(730, len(load["heating"]) + 1, 730)]
    peak_injection = [np.max((load["cooling"].clip(0) * load_factor)[i - 730:i]) for i in
                      range(730, len(load["cooling"]) + 1, 730)]
    monthly_load = MonthlyGeothermalLoadMultiYear(monthly_heating_load * 730, monthly_cooling_load * 730,
                                                  peak_extraction, peak_injection)
    borefield.load = monthly_load
    assert np.allclose(borefield.load.monthly_baseload_extraction_power_simulation_period, monthly_heating_load)
    assert np.allclose(borefield.load.monthly_baseload_injection_power_simulation_period, monthly_cooling_load)
    assert np.allclose(borefield.load.monthly_baseload_extraction_simulation_period, monthly_heating_load * 730)
    assert np.allclose(borefield.load.monthly_baseload_injection_simulation_period, monthly_cooling_load * 730)
    assert np.allclose(borefield.load.monthly_peak_extraction_simulation_period, peak_extraction)
    assert np.allclose(borefield.load.monthly_peak_injection_simulation_period, peak_injection)
    assert np.allclose(borefield.load.monthly_average_injection_power_simulation_period,
                       monthly_cooling_load - monthly_heating_load)
    assert borefield.load.simulation_period == 50
    h = borefield.size_L3(150)
    assert np.isclose(h, 110.233, rtol=0.001)
    load["heating"][8760 * 25:] = 0
    monthly_heating_load = np.array([np.mean((load["heating"].clip(0) * load_factor)[i - 730:i]) for i in
                                     range(730, len(load["heating"]) + 1, 730)])
    monthly_cooling_load = np.array([np.mean((load["cooling"].clip(0) * load_factor)[i - 730:i]) for i in
                                     range(730, len(load["cooling"]) + 1, 730)])
    peak_extraction = [np.max((load["heating"].clip(0) * load_factor)[i - 730:i]) for i in
                       range(730, len(load["heating"]) + 1, 730)]
    peak_injection = [np.max((load["cooling"].clip(0) * load_factor)[i - 730:i]) for i in
                      range(730, len(load["cooling"]) + 1, 730)]
    hourly_load = MonthlyGeothermalLoadMultiYear(monthly_heating_load * 730, monthly_cooling_load * 730,
                                                 peak_extraction, peak_injection)
    borefield.load = hourly_load
    assert np.allclose(borefield.load.monthly_baseload_extraction_power_simulation_period, monthly_heating_load)
    assert np.allclose(borefield.load.monthly_baseload_injection_power_simulation_period, monthly_cooling_load)
    assert np.allclose(borefield.load.monthly_peak_extraction_simulation_period, peak_extraction)
    assert np.allclose(borefield.load.monthly_peak_injection_simulation_period, peak_injection)
    assert np.allclose(borefield.load.monthly_average_injection_power_simulation_period,
                       monthly_cooling_load - monthly_heating_load)
    h = borefield.size_L3(150)
    assert np.isclose(h, 100.418, rtol=0.001)
