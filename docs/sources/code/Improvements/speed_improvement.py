import pytest
from GHEtool import *
import matplotlib.pyplot as plt
import pygfunction as gt
import time


def _optimise_load_profile():
    # initiate ground data
    data = GroundData(3, 10, 0.2)

    # initiate pygfunction borefield model
    borefield_gt = gt.boreholes.rectangle_field(10, 10, 6, 6, 110, 1, 0.075)

    # initiate borefield
    borefield = Borefield()

    # set ground data in borefield
    borefield.set_ground_parameters(data)

    # set pygfunction borefield
    borefield.set_borefield(borefield_gt)

    # load the hourly profile
    borefield.load_hourly_profile("hourly_profile.csv", header=True, separator=";",
                                  first_column_heating=True)

    # optimise the load for a 10x10 field (see data above) and a fixed depth of 150m.
    borefield.optimise_load_profile(depth=150, print_results=False)


GFunction.DEFAULT_STORE_PREVIOUS_VALUES = False
start = time.time()
_optimise_load_profile()
print(time.time() - start)
GFunction.DEFAULT_STORE_PREVIOUS_VALUES = True
start = time.time()
_optimise_load_profile()
print(time.time() - start)

def test_optimise_load_profile(monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda: None)
    monkeypatch.setattr(GFunction, 'DEFAULT_STORE_PREVIOUS_VALUES', True)

    start_time = time.time()
    _optimise_load_profile()
    end_time = time.time()
    diff = end_time - start_time

    monkeypatch.setattr(GFunction, 'DEFAULT_STORE_PREVIOUS_VALUES', False)

    start_time_without = time.time()
    _optimise_load_profile()
    end_time_without = time.time()
    diff_without = end_time_without - start_time_without

    print(f'\nOptimise load profile took  {round(diff_without, 2)} ms in v2.1.0 and '
          f'{round(diff, 2)} ms in v2.1.1. This is an improvement of {round((diff_without-diff)/diff*100)}%.')