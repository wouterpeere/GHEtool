"""
The work of (Ahmadfard and Bernier, 2019) provides a set of test cases that can be used to compare
software tools with the ultimate goal of improving the reliability of design methods for sizing
vertical ground heat exchangers. This document delivers the results on the test file using the GHEtool
L2-, L3- and L4-sizing methods.

Test 1 -Synthetic balanced load – one borehole

References:
-----------
    - Ahmadfard, M., and M. Bernier. 2019. A review of vertical ground heat exchanger sizing tools including an inter-model
comparison [in eng]. Renewable sustainable energy reviews (OXFORD) 110:247–265.
"""
import os
import time

import numpy as np

from GHEtool import *


def test_1b():
    # initiate ground, fluid and pipe data
    ground_data = GroundFluxTemperature(k_s=1.8, T_g=17.5, volumetric_heat_capacity=2073600, flux=0)
    fluid_data = ConstantFluidData(rho=1052, cp=3795, mu=0.0052, k_f=0.48)
    flow_data = ConstantFlowRate(mfr=0.5585)
    pipe_data = MultipleUTube(r_in=0.0137, r_out=0.0167, D_s=0.075 / 2, k_g=1.4, k_p=0.43, number_of_pipes=1)

    # start test with dynamic Rb*
    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.ground_data = ground_data
    borefield.fluid_data = fluid_data
    borefield.pipe_data = pipe_data
    borefield.flow_data = flow_data
    borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)

    # load the hourly profile
    load = HourlyGeothermalLoad(simulation_period=10)
    load.load_hourly_profile(os.path.join(os.path.dirname(__file__), 'test1b.csv'), header=True, separator=";",
                             decimal_seperator=",", col_extraction=1,
                             col_injection=0)
    borefield.load = load

    delta_t = max(load.max_peak_extraction, load.max_peak_injection) * 1000 / (fluid_data.cp() * flow_data.mfr())

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(0 - delta_t / 2)

    # Sizing with dynamic Rb
    # according to L2
    L2_start = time.time()
    depth_L2 = borefield.size(100, L2_sizing=True)
    Rb_L2 = borefield.Rb
    L2_stop = time.time()

    # according to L3
    L3_start = time.time()
    depth_L3 = borefield.size(100, L3_sizing=True)
    Rb_L3 = borefield.Rb
    L3_stop = time.time()

    # according to L4
    L4_start = time.time()
    depth_L4 = borefield.size(100, L4_sizing=True)
    Rb_L4 = borefield.Rb
    L4_stop = time.time()

    # start test with constant Rb*
    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.ground_data = ground_data
    borefield.fluid_data = fluid_data
    borefield.pipe_data = pipe_data
    borefield.flow_data = flow_data
    borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)
    Rb_static = 0.13
    borefield.set_Rb(Rb_static)

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_avg_fluid_temperature(0 - delta_t / 2)

    # load the hourly profile
    borefield.load = load

    L2s_start = time.time()
    depth_L2s = borefield.size(100, L2_sizing=True)
    L2s_stop = time.time()

    # according to L3
    L3s_start = time.time()
    depth_L3s = borefield.size(100, L3_sizing=True)
    L3s_stop = time.time()

    # according to L4
    L4s_start = time.time()
    depth_L4s = borefield.size(100, L4_sizing=True)
    L4s_stop = time.time()

    print(
        f"The sizing according to L2 has a depth of {depth_L2:.2f}m (using dynamic Rb* of {Rb_L2:.3f}) and {depth_L2s:.2f}m (using constant Rb*)")
    print(
        f"The sizing according to L3 has a depth of {depth_L3:.2f}m (using dynamic Rb* of {Rb_L3:.3f}) and {depth_L3s:.2f}m (using constant Rb*)")
    print(
        f"The sizing according to L4 has a depth of {depth_L4:.2f}m (using dynamic Rb* of {Rb_L4:.3f}) and {depth_L4s:.2f}m (using constant Rb*)")

    assert np.isclose(depth_L2, 75.67161488446233)
    assert np.isclose(depth_L3, 75.62427445122744)
    assert np.isclose(depth_L4, 71.49641008062054)
    assert np.isclose(depth_L2s, 76.71715998100636)
    assert np.isclose(depth_L3s, 76.67104470064083)
    assert np.isclose(depth_L4s, 72.52389782010322)
    assert np.isclose(Rb_L2, 0.12648875915036317)
    assert np.isclose(Rb_L3, 0.12648767833749805)
    assert np.isclose(Rb_L4, 0.12639600391560102)


if __name__ == "__main__":  # pragma: no cover
    test_1b()
