"""
This document contains 4 different cases referring to the paper: Peere, W., Picard, D., Cupeiro Figueroa, I., Boydens, W., and Helsen, L. Validated combined first and last year borefield sizing methodology. In Proceedings of International Building Simulation Conference 2021 (2021). Brugge (Belgium), 1-3 September 2021.
"""
import numpy as np


def load_case(number):
    """This function returns the values for one of the four cases."""

    if number == 1:
        # case 1
        # limited in the first year by cooling
        monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
        monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
        monthly_load_heating = monthly_load_heating_percentage * 300 * 10 ** 3  # kWh
        monthly_load_cooling = monthly_load_cooling_percentage * 150 * 10 ** 3  # kWh
        peak_cooling = np.array([0., 0., 22., 44., 83., 117., 134., 150., 100., 23., 0., 0.])
        peak_heating = np.zeros(12)

    elif number == 2:
        # case 2
        # limited in the last year by cooling
        monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, .117, 0.144])
        monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
        monthly_load_heating = monthly_load_heating_percentage * 160 * 10 ** 3  # kWh
        monthly_load_cooling = monthly_load_cooling_percentage * 240 * 10 ** 3  # kWh
        peak_cooling = np.array([0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.])  # Peak cooling in kW
        peak_heating = np.array([160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.])

    elif number == 3:
        # case 3
        # limited in the first year by heating
        monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, .117, 0.144])
        monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
        monthly_load_heating = monthly_load_heating_percentage * 160 * 10 ** 3  # kWh
        monthly_load_cooling = monthly_load_cooling_percentage * 240 * 10 ** 3  # kWh
        peak_cooling = np.zeros(12)
        peak_heating = np.array([300.0, 266.25, 191.25, 103.125, 0.0, 0.0, 0.0, 0.0, 75.75, 159.375, 223.125, 255.0])

    else:
        # case 4
        # limited in the last year by heating
        monthly_load_heating_percentage = np.array([0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144])
        monthly_load_cooling_percentage = np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
        monthly_load_heating = monthly_load_heating_percentage * 300 * 10 ** 3  # kWh
        monthly_load_cooling = monthly_load_cooling_percentage * 150 * 10 ** 3  # kWh
        peak_cooling = np.array([0., 0., 22., 44., 83., 117., 134., 150., 100., 23., 0., 0.])
        peak_heating = np.array([300., 268., 191., 103., 75., 0., 0., 38., 76., 160., 224., 255.])

    return monthly_load_cooling, monthly_load_heating, peak_cooling, peak_heating
