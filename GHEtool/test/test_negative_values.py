import numpy as np

from GHEtool import GroundConstantTemperature, HourlyGeothermalLoad, Borefield

import pygfunction as gt

from GHEtool.VariableClasses import _time_values


def test_negative_g_func_values():
    # relevant borefield data for the calculations
    data = GroundConstantTemperature(1,  # conductivity of the soil (W/mK)
                                     12,  # Ground temperature at infinity (degrees C)
                                     5 * 10 ** 6)  # ground volumetric heat capacity (J/m3K)
    # set the load
    load = HourlyGeothermalLoad(np.zeros(8760), np.zeros(8760), 100)

    # create the borefield object
    borefield = Borefield(load=load)

    borefield.set_ground_parameters(data)
    borefield.create_rectangular_borefield(10, 7, 3, 3, 150, 5, 0.2)

    borefield.Rb = 0.12  # equivalent borehole resistance (K/W)

    # set temperature boundaries
    borefield.set_max_avg_fluid_temperature(16)  # maximum temperature
    borefield.set_min_avg_fluid_temperature(0)  # minimum temperature

    g_func0 = borefield.gfunction(load.time_L4, 150)

    borefield.gfunction_calculation_object.remove_previous_data()
    borefield.gfunction_calculation_object.set_options_gfunction_calculation({'linear_threshold': 16000})

    g_func1 = borefield.gfunction(load.time_L4, 150)

    time_vals = _time_values(t_max=load.time_L4[-1])

    g_func2 = gt.gfunction.gFunction(borefield.borefield, data.alpha, time_vals,
                                     options=borefield.gfunction_calculation_object.options,
                                     method=borefield.gfunction_calculation_object.options['method']).gFunc

    borefield.gfunction_calculation_object.options['linear_threshold'] = time_vals[10]

    g_func3 = gt.gfunction.gFunction(borefield.borefield, data.alpha, time_vals,
                                     options=borefield.gfunction_calculation_object.options,
                                     method=borefield.gfunction_calculation_object.options['method']).gFunc

    del borefield.gfunction_calculation_object.options['linear_threshold']

    g_func3[:10] = gt.gfunction.gFunction(borefield.borefield, data.alpha, time_vals[:10],
                                     options=borefield.gfunction_calculation_object.options,
                                     method=borefield.gfunction_calculation_object.options['method']).gFunc


    import matplotlib.pyplot as plt
    plt.Figure()
    plt.plot(g_func0, label="g_func0")
    plt.plot(g_func1, label="g_func1")
    plt.plot(np.interp(load.time_L4, time_vals, g_func2), label="g_func2")
    plt.legend()
    plt.show()


    assert np.allclose(g_func1, np.interp(load.time_L4, time_vals, g_func2))
    assert np.allclose(g_func0, np.interp(load.time_L4, time_vals, g_func3), rtol=0.001)
    assert np.all(g_func0 > 0)
    assert np.all(g_func1 > 0)
    assert np.all(g_func2 > 0)
