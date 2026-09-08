import numpy as np
from GHEtool.VariableClasses.Regeneration import Regeneration


def test_regeneration_only_power():
    regeneration = Regeneration(200)
    assert regeneration.power == 200
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 5, 1, 4000), 200)
    regeneration = Regeneration(np.array([200, 300, 400]))
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 5, 1, 4000), 200)
    assert np.isclose(regeneration.get_regeneration_power_inlet(1, 5, 1, 4000), 300)
    assert np.isclose(regeneration.get_regeneration_power_inlet(2, 5, 1, 4000), 400)
    regeneration = Regeneration(np.array([200, 300, 400]), 1, a1=1, a2=2, min_delta_T=10)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 5, 1, 4000), 200)
    assert np.isclose(regeneration.get_regeneration_power_inlet(1, 5, 1, 4000), 300)
    assert np.isclose(regeneration.get_regeneration_power_inlet(2, 5, 1, 4000), 400)
    regeneration = Regeneration(np.array([200, 300, 400]), np.array([1, 1, 1]), a1=1, a2=2, min_delta_T=10)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 5, 1, 4000), 200)
    assert np.isclose(regeneration.get_regeneration_power_inlet(1, 5, 1, 4000), 300)
    assert np.isclose(regeneration.get_regeneration_power_inlet(2, 5, 1, 4000), 400)


def test_regeneration_temperature():
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0.1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 0, 1, 4000), 0.5999475405360499)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0.1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 2, 1, 4000), -0.39998496959015023)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0.001)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 0, 1, 4000), 0.5009681558476586)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 0, 1, 4000), 0.4999687519530029)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 2, 1, 4000), -0.4999687519530029)

    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=5e6, a2=0.1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 0, 1, 4000), 4000)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=5e6, a2=0.1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 2, 1, 4000), -4000)
    regeneration = Regeneration(power=100, temperature=np.array([1, 1, 1]), a1=5e6, a2=0.1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 2, 1, 4000), -4000)
    regeneration = Regeneration(power=10000, temperature=np.array([1, 1, 1]), a1=5e6, a2=0.1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 1, 1, 4000), 15.974437701515852)
    regeneration = Regeneration(power=10000, temperature=np.array([1, 1, 1]), a1=5e6, a2=0.1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 0, 1, 4000), 8003.194889170117)

    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=5e6)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 0, 1, 4000), 4000)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=5e6)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 2, 1, 4000), -4000)
    regeneration = Regeneration(power=100, temperature=np.array([1, 1, 1]), a1=5e6)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 2, 1, 4000), -4000)
    regeneration = Regeneration(power=10000, temperature=np.array([1, 1, 1]), a1=5e6)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 1, 1, 4000), 15.974437701515852)
    regeneration = Regeneration(power=10000, temperature=np.array([1, 1, 1]), a1=5e6)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 0, 1, 4000), 8003.194889170117)
    regeneration = Regeneration(power=10000, temperature=np.array([1, 1, 1]), a1=100)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 2, 1, 4000), 9777.777777777777)
    regeneration = Regeneration(power=10000, temperature=np.array([1, 1, 1]), a1=100, a2=1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 2, 1, 4000), 9782.657761064684)


def test_regeneration_temperature_min_delta():
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0.1, min_delta_T=1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(1, -1, 1, 4000), 0.5999475405360499)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0.1, min_delta_T=1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(1, 1, 1, 4000), 0)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0.001, min_delta_T=1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(-1, -1, 1, 4000), 0.5009681558476586)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0.1, min_delta_T=1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(0, 3, 1, 4000), -0.39998496959015023)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, a2=0, min_delta_T=1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(-1, -1, 1, 4000), 0.4999687519530029)
    regeneration = Regeneration(power=0, temperature=np.array([1, 1, 1]), a1=0.5, min_delta_T=1)
    assert np.isclose(regeneration.get_regeneration_power_inlet(-1, -1, 1, 4000), 0.4999687519530029)
