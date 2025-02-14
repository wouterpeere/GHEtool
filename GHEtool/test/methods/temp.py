from GHEtool import *
import pygfunction as gt
import numpy as np
from GHEtool.Methods.optimise_load_profile import optimise_load_profile_power

borefield_gt = gt.boreholes.rectangle_field(10, 12, 6, 6, 150, 4, 0.075)
hourly_load = HourlyBuildingLoad(efficiency_heating=10 ** 6, efficiency_cooling=10 ** 6, efficiency_dhw=10 ** 6)

borefield = Borefield()
data = GroundConstantTemperature(3, 10)
borefield.set_ground_parameters(data)
borefield.set_Rb(0.2)
borefield.set_borefield(borefield_gt)
borefield.set_max_avg_fluid_temperature(16)
borefield.set_min_avg_fluid_temperature(0)
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"), col_heating=1,
                                col_cooling=0, col_dhw=1)
hourly_load.hourly_heating_load = np.zeros(8760)
borefield.load = hourly_load

borefield_load, external_load = optimise_load_profile_power(borefield, hourly_load, dhw_preferential=True)
_percentage_extraction = (np.sum(borefield_load.hourly_heating_load_simulation_period) + np.sum(
    borefield_load.hourly_dhw_load_simulation_period)) / \
                         (np.sum(hourly_load.hourly_heating_load_simulation_period) + np.sum(
                             hourly_load.hourly_dhw_load_simulation_period)) * 100
_percentage_injection = np.sum(borefield_load.hourly_cooling_load_simulation_period) / \
                        np.sum(hourly_load.hourly_cooling_load_simulation_period) * 100
print(_percentage_extraction)
print(_percentage_injection)
print(borefield_load.max_peak_extraction)
print(borefield_load.max_peak_injection)
print(external_load.max_peak_heating)
print(external_load.max_peak_cooling)
# list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.976, 66.492,
#                                                    643.137, 195.331, 33.278, 340.705,
#                                                    name='Optimise load profile 1, reversed (power, dhw not preferential)',
#                                                    power=True,
#                                                    hourly=False, dhw_preferential=False))
# list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.971, 66.424,
#                                                    639.283, 195.053, 37.132, 340.983,
#                                                    name='Optimise load profile 1, reversed (power, hourly, dhw not preferential)',
#                                                    power=True,
#                                                    hourly=True, dhw_preferential=False))
# hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\hourly_profile.csv"), col_heating=1,
#                                 col_cooling=0, col_dhw=0)
# hourly_load.set_hourly_heating_load(np.zeros(8760))
# hourly_load.cop_dhw = 10 ** 6
# list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.976, 66.492,
#                                                    643.137, 195.331, 33.278, 340.705,
#                                                    name='Optimise load profile 1, reversed (power, dhw load)',
#                                                    power=True,
#                                                    hourly=False, dhw_preferential=True))
# list_of_test_objects.add(OptimiseLoadProfileObject(borefield, hourly_load, 150, 99.971, 66.424,
#                                                    639.283, 195.053, 37.132, 340.983,
#                                                    name='Optimise load profile 1, reversed (power, hourly, dhw load)',
#                                                    power=True,
#                                                    hourly=True, dhw_preferential=True))
