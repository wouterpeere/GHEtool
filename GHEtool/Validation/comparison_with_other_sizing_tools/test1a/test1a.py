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


def test_1a_6h():
    # initiate ground, fluid and pipe data
    ground_data = GroundFluxTemperature(k_s=1.8, T_g=17.5, volumetric_heat_capacity=2073600, flux=0)
    fluid_data = ConstantFluidData(rho=1052, cp=3795, mu=0.0052, k_f=0.48)
    flow_data = ConstantFlowRate(mfr=0.44)
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
    load.load_hourly_profile(os.path.join(os.path.dirname(__file__), 'test1a.csv'), header=True, separator=",",
                             col_extraction=1, col_injection=0)
    borefield.load = load

    delta_t = max(load.max_peak_extraction, load.max_peak_injection) * 1000 / (fluid_data.cp() * flow_data.mfr())

    # set temperature bounds
    borefield.set_max_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_fluid_temperature(0 - delta_t / 2)

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
    borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)
    Rb_static = 0.13
    borefield.set_Rb(Rb_static)

    # set temperature bounds
    borefield.set_max_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_fluid_temperature(0 - delta_t / 2)

    # load the hourly profile
    borefield.load = load

    # Sizing with constant Rb
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
    assert np.isclose(depth_L2, 59.3636198458606)
    assert np.isclose(depth_L3, 59.539512919146844)
    assert np.isclose(depth_L4, 56.263487685923195)
    assert np.isclose(depth_L2s, 59.8323879060427)
    assert np.isclose(depth_L3s, 60.00760582636102)
    assert np.isclose(depth_L4s, 56.732044011668464)
    assert np.isclose(Rb_L2, 0.12800794794314643)
    assert np.isclose(Rb_L3, 0.12801297090220962)
    assert np.isclose(Rb_L4, 0.1279218446632468)


def test_1a_1h():
    # initiate ground, fluid and pipe data
    ground_data = GroundFluxTemperature(k_s=1.8, T_g=17.5, volumetric_heat_capacity=2073600, flux=0)
    fluid_data = ConstantFluidData(rho=1052, cp=3795, mu=0.0052, k_f=0.48)
    flow_data = ConstantFlowRate(mfr=0.44)
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
    load.load_hourly_profile(os.path.join(os.path.dirname(__file__), 'test1a.csv'), header=True, separator=",",
                             col_extraction=1, col_injection=0)
    borefield.load = load
    borefield.load.peak_duration = 1

    delta_t = max(load.max_peak_extraction, load.max_peak_injection) * 1000 / (fluid_data.cp() * flow_data.mfr())

    # set temperature bounds
    borefield.set_max_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_fluid_temperature(0 - delta_t / 2)

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
    borefield.create_rectangular_borefield(1, 1, 6, 6, 110, 4, 0.075)
    Rb_static = 0.13
    borefield.set_Rb(Rb_static)

    # set temperature bounds
    borefield.set_max_fluid_temperature(35 + delta_t / 2)
    borefield.set_min_fluid_temperature(0 - delta_t / 2)

    # load the hourly profile
    borefield.load = load
    borefield.load.peak_duration = 1

    # Sizing with constant Rb
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
    assert np.isclose(depth_L2, 46.4408463170366)
    assert np.isclose(depth_L3, 46.73652745970898)
    assert np.isclose(depth_L4, 56.26298710970397)
    assert np.isclose(depth_L2s, 46.986986159967906)
    assert np.isclose(depth_L3s, 47.282207335475356)
    assert np.isclose(depth_L4s, 56.73157055683088)
    assert np.isclose(Rb_L2, 0.12767939520070198)
    assert np.isclose(Rb_L3, 0.1276860188802275)
    assert np.isclose(Rb_L4, 0.12792183113119798)


if __name__ == "__main__":  # pragma: no cover
    test_1a_6h()
    test_1a_1h()
