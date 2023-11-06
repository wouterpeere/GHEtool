import numpy as np

from GHEtool import GroundConstantTemperature, MonthlyGeothermalLoadAbsolute, Borefield


def test_negative_g_func_values():
    # relevant borefield data for the calculations
    data = GroundConstantTemperature(1,             # conductivity of the soil (W/mK)
                                     12,            # Ground temperature at infinity (degrees C)
                                     5 * 10**6)   # ground volumetric heat capacity (J/m3K)

    # monthly loading values
    peak_cooling = np.array([0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.])  # Peak cooling in kW
    peak_heating = np.array([160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.])  # Peak heating in kW

    # annual heating and cooling load
    annual_heating_load = 300 * 10 ** 3  # kWh
    annual_cooling_load = 160 * 10 ** 3  # kWh

    # percentage of annual load per month (15.5% for January ...)
    monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
    monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])

    # resulting load per month
    monthly_load_heating = annual_heating_load * monthly_load_heating_percentage   # kWh
    monthly_load_cooling = annual_cooling_load * monthly_load_cooling_percentage   # kWh

    # set the load
    load = MonthlyGeothermalLoadAbsolute(monthly_load_heating, monthly_load_cooling, peak_heating, peak_cooling)

    # create the borefield object
    borefield = Borefield(load=load)

    borefield.set_ground_parameters(data)
    borefield.create_rectangular_borefield(10, 7, 3, 3, 150, 5, 0.2)

    borefield.Rb = 0.12  # equivalent borehole resistance (K/W)

    # set temperature boundaries
    borefield.set_max_avg_fluid_temperature(16)   # maximum temperature
    borefield.set_min_avg_fluid_temperature(0)    # minimum temperature

    g_func = borefield.gfunction(load.time_L3, 150)
    assert np.all(g_func > 0)
