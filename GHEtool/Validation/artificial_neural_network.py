"""
The goal of this file is to validate the artificial neural network, based on the work of Blanke et al. ([#BlankeEtAl]_).
It shows that all simulations are withing 2% and that the ANN gives a slight overestimation (so it is on the safe side).
The simulation time is 200-1000 times faster.

References
----------
.. [#BlankeEtAl] Blanke T., Pfeiffer F., Göttsche J., Döring B. (2024) Artificial neural networks use
for the design of geothermal probe fields. In Proceedings of BauSim Conference 2024:  10th Conference of
IBPSA-Germany and Austria. Vienna (Austria), 23-26 September 2024. https://doi.org/10.26868/29761662.2024.12
"""
import copy

from GHEtool import *
from GHEtool.Validation.cases import load_case
import time

## define cases

# 4 cases
borefield_case_1 = Borefield(ground_data=GroundConstantTemperature(3.5, 10),
                             load=MonthlyGeothermalLoadAbsolute(*load_case(1)))
borefield_case_1.create_rectangular_borefield(10, 6, 6.5, 6.5, 100, 4, 0.075)

borefield_case_2 = Borefield(ground_data=GroundConstantTemperature(3.5, 10),
                             load=MonthlyGeothermalLoadAbsolute(*load_case(2)))
borefield_case_2.create_rectangular_borefield(10, 6, 6.5, 6.5, 100, 4, 0.075)

borefield_case_3 = Borefield(ground_data=GroundConstantTemperature(3.5, 10),
                             load=MonthlyGeothermalLoadAbsolute(*load_case(3)))
borefield_case_3.create_rectangular_borefield(10, 6, 6.5, 6.5, 100, 4, 0.075)

borefield_case_4 = Borefield(ground_data=GroundConstantTemperature(3.5, 10),
                             load=MonthlyGeothermalLoadAbsolute(*load_case(4)))
borefield_case_4.create_rectangular_borefield(10, 6, 6.5, 6.5, 100, 4, 0.075)

borefield = Borefield()
borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 4, 0.075)
borefield.ground_data = GroundFluxTemperature(3, 10)
borefield.fluid_data = ConstantFluidData(0.568, 998, 4180, 1e-3)
borefield.flow_data = ConstantFlowRate(mfr=0.2)
borefield.pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)
borefield.calculation_setup(use_constant_Rb=False)
borefield.set_max_avg_fluid_temperature(17)
borefield.set_min_avg_fluid_temperature(3)
hourly_load = HourlyGeothermalLoad()
hourly_load.simulation_period = 20
hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\office.csv"), header=True, separator=";",
                                col_injection=0, col_extraction=1)
borefield.load = hourly_load
borefield_office = copy.deepcopy(borefield)

hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True, separator=";",
                                col_injection=0, col_extraction=1)
borefield.load = hourly_load
borefield.create_rectangular_borefield(5, 4, 6, 6, 110, 4, 0.075)
borefield_auditorium = copy.deepcopy(borefield)

hourly_load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\swimming_pool.csv"), header=True,
                                separator=";",
                                col_injection=0, col_extraction=1)
borefield.load = hourly_load
borefield.create_rectangular_borefield(15, 20, 6, 6, 110, 4, 0.075)
borefield_swimming_pool = copy.deepcopy(borefield)

# define lists
list_borefields_L3 = [
    ('case 1', borefield_case_1),
    ('case 2', borefield_case_2),
    ('case 3', borefield_case_3),
    ('case 4', borefield_case_4),
    ('office', borefield_office),
    ('auditorium', borefield_auditorium),
    ('swimming pool', borefield_swimming_pool)
]

list_borefields_L4 = [
    ('office', borefield_office),
    ('auditorium', borefield_auditorium),
    ('swimming pool', borefield_swimming_pool)
]


def validate_L3():
    print('--- L3 ---')
    for name, borefield in list_borefields_L3:
        borefield.calculation_setup(use_neural_network=False)
        start = time.time()
        depth_reg = borefield.size_L3()
        time_reg = time.time() - start

        borefield.calculation_setup(use_neural_network=True)
        start = time.time()
        depth_ann = borefield.size_L3()
        time_ann = time.time() - start

        print(f'The required depth for case "{name}" is: {depth_reg:.2f}m (regular) or {depth_ann:.2f}m (ANN) '
              f'(difference of {((depth_ann - depth_reg) / depth_reg * 100):.2f}%). The calculation time was '
              f'{time_reg:.4f}s (regular) and {time_ann:.4f}s (ANN) (factor of {(time_reg / time_ann):.0f}).')

        assert (depth_ann - depth_reg) / depth_reg < 0.02  # should be under 2%


def validate_L4():
    print('--- L4 ---')
    for name, borefield in list_borefields_L4:
        borefield.calculation_setup(use_neural_network=False)
        start = time.time()
        depth_reg = borefield.size_L4()
        time_reg = time.time() - start

        borefield.calculation_setup(use_neural_network=True)
        start = time.time()
        depth_ann = borefield.size_L4()
        time_ann = time.time() - start

        print(f'The required depth for case "{name}" is: {depth_reg:.2f}m (regular) or {depth_ann:.2f}m (ANN) '
              f'(difference of {((depth_ann - depth_reg) / depth_reg * 100):.2f}%). The calculation time was '
              f'{time_reg:.4f}s (regular) and {time_ann:.4f}s (ANN) (factor of {(time_reg / time_ann):.0f}).')

        assert (depth_ann - depth_reg) / depth_reg < 0.02  # should be under 2%


if __name__ == "__main__":  # pragma: no cover
    validate_L3()
    validate_L4()
