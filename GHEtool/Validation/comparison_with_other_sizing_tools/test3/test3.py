"""
The work of (Ahmadfard and Bernier, 2019) provides a set of test cases that can be used to compare
software tools with the ultimate goal of improving the reliability of design methods for sizing
vertical ground heat exchangers. This document delivers the results on the test file using the GHEtool
L2-, L3- and L4-sizing methods.

Test 3 – Required length during the first year

References:
-----------
    - Ahmadfard, M., and M. Bernier. 2019. A review of vertical ground heat exchanger sizing tools including an inter-model
comparison [in eng]. Renewable sustainable energy reviews (OXFORD) 110:247–265.
"""
from GHEtool import *
import numpy as np
import time


def test_3_6h():
    # initiate ground, fluid and pipe data
    ground_data = GroundFluxTemperature(k_s=2.25, T_g=10, volumetric_heat_capacity=2592000, flux=0)
    fluid_data = FluidData(mfr=33.1/49, rho=1026, Cp=4019, mu=0.003377, k_f=0.468)
    pipe_data = MultipleUTube(r_in=0.013, r_out=0.0167, D_s=0.075/2, k_g=1.73, k_p=0.4, number_of_pipes=1)

    # start test with dynamic Rb*
    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(7, 7, 5, 5, 110, 2.5, 0.075)

    # load the hourly profile
    load = HourlyGeothermalLoad(simulation_period=10)
    load.load_hourly_profile("test3.csv", header=True, separator=",", col_heating=1, col_cooling=0)
    borefield.load = load

    delta_t = max(load.max_peak_cooling, load.max_peak_cooling) * 1000 / (fluid_data.Cp * fluid_data.mfr) / 49

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t/2)
    borefield.set_min_avg_fluid_temperature(0 - delta_t/2)

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
    borefield.set_ground_parameters(ground_data)
    borefield.set_fluid_parameters(fluid_data)
    borefield.set_pipe_parameters(pipe_data)
    borefield.create_rectangular_borefield(7, 7, 5, 5, 110, 2.5, 0.075)
    Rb_static = 0.1
    borefield.set_Rb(Rb_static)

    # set temperature bounds
    borefield.set_max_avg_fluid_temperature(35 + delta_t/2)
    borefield.set_min_avg_fluid_temperature(0 - delta_t/2)

    # load the hourly profile
    load = HourlyGeothermalLoad(simulation_period=10)
    load.load_hourly_profile("test3.csv", header=True, separator=",", col_heating=1, col_cooling=0)
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

    assert np.equal(depth_L2, 117.36039732946608)
    assert np.equal(depth_L3, 117.1785111449418)
    assert np.equal(depth_L4, 117.14859810762285)
    assert np.equal(depth_L2s, 107.52272928881716)
    assert np.equal(depth_L3s, 107.34311737737467)
    assert np.equal(depth_L4s, 107.36958044500126)
    assert np.equal(Rb_L2, 0.12265691458202486)
    assert np.equal(Rb_L3, 0.12265286595141986)
    assert np.equal(Rb_L4, 0.12265220070895928)


if __name__ == "__main__":
    test_3_6h()
<<<<<<< HEAD:GHEtool/Validation/InterSizingtoolsComp/test3/test3.py


=======
>>>>>>> origin/issue243-add-validation-based-on-ahmadfard-bernier:GHEtool/Validation/comparison_with_other_sizing_tools/test3/test3.py
