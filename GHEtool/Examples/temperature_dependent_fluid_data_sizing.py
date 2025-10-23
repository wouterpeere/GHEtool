"""
In this example, both a sizing with constant fluid properties and a sizing with temperature dependent fluid properties
is done.
"""
from GHEtool import *

from GHEtool.Validation.cases import load_case

import matplotlib.pyplot as plt


def size_with_temperature_dependence():
    # load data
    fluid_data = TemperatureDependentFluidData('MPG', 25)
    flow_data = ConstantFlowRate(vfr=0.3)
    pipe_data = DoubleUTube(1.5, 0.013, 0.016, 0.4, 0.035)
    ground_data = GroundFluxTemperature(2, 9.8)

    borefield = Borefield(
        ground_data=ground_data,
        flow_data=flow_data,
        fluid_data=fluid_data,
        pipe_data=pipe_data,
        load=MonthlyGeothermalLoadAbsolute(*load_case(4))
    )

    borefield.set_min_avg_fluid_temperature(2)
    borefield.set_max_avg_fluid_temperature(17)

    borefield.create_rectangular_borefield(12, 5, 6, 6, 150)

    # calculate required size with variable temperature
    size_variable = borefield.size_L3()
    results_variable = borefield.results

    # calculate required size with fixed temperature
    borefield.fluid_data = fluid_data.create_constant(2)
    size_fixed = borefield.size_L3()
    results_fixed = borefield.results

    peak_extraction_diff = results_fixed.peak_extraction - results_variable.peak_extraction
    peak_injection_diff = results_fixed.peak_injection - results_variable.peak_injection

    print(f'Sizing with temperature dependent fluid properties: {size_variable:.2f}m')
    print(f'Sizing with constant fluid properties: {size_fixed:.2f}m')
    print(f'Max temperature difference in extraction: {min(peak_extraction_diff):.2f}°C')
    print(f'Max temperature difference in injection: {max(peak_injection_diff):.2f}°C')

    time_array = borefield.load.time_L3 / 12 / 730.0 / 3600.0
    plt.figure()
    plt.plot(time_array, peak_extraction_diff, label="Difference in peak extraction temperature")
    plt.plot(time_array, peak_injection_diff, label="Difference in peak injection temperature")
    plt.ylabel('Temperature difference in peak power [°C]')
    plt.xlabel('Time [year]')
    plt.xticks(range(0, borefield.simulation_period + 1, 2))
    plt.legend()

    borefield.print_temperature_profile()


if __name__ == "__main__":  # pragma: no-cover
    size_with_temperature_dependence()
