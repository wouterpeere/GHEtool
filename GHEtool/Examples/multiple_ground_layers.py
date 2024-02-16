"""
This example sizes a borefield using the advanced option of using multiple ground layers.
"""

from GHEtool import *
from GHEtool.Validation.cases import load_case

def multiple_ground_layers():
    # initiate borefield model
    borefield = Borefield()
    borefield.create_rectangular_borefield(10, 10, 6, 6, 110, 1, 0.075)
    borefield.set_Rb(0.12)

    # set temperature boundaries
    borefield.set_max_avg_fluid_temperature(16)  # maximum temperature
    borefield.set_min_avg_fluid_temperature(0)  # minimum temperature
    borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(4))

    # create two ground classes
    constant_ks = GroundFluxTemperature(1.7, 10)

    layer_1 = GroundLayer(k_s=1.7, thickness=4.9)
    layer_2 = GroundLayer(k_s=2.3, thickness=1.9)
    layer_3 = GroundLayer(k_s=2.1, thickness=3)
    layer_4 = GroundLayer(k_s=1.5, thickness=69.7)
    layer_5 = GroundLayer(k_s=2.1, thickness=16.1)
    layer_6 = GroundLayer(k_s=1.7, thickness=None)

    layered_ground = GroundFluxTemperature(T_g=10)
    layered_ground.add_layer_on_bottom([layer_1, layer_2, layer_3, layer_4, layer_5, layer_6])

    # size borefield according to the two different ground data variables
    borefield.ground_data = constant_ks
    print(f'The required borehole depth is {borefield.size():.3f}m if you use a constant approximation for the ground conductivity.')

    borefield.ground_data = layered_ground
    print(f'The required borehole depth is {borefield.size():.3f}m if you use a detailed ground model with multiple layers.')


if __name__ == "__main__":  # pragma: no cover
    multiple_ground_layers()
