"""
This file contains the test for the pipedata
"""

from GHEtool.VariableClasses.PipeData import *
import matplotlib.pyplot as plt

### Test U-pipes

def test_draw_internals(monkeypatch):
    pipe = DoubleUPipe(1, 0.015, 0.02, 0.4, 0.05)
    monkeypatch.setattr(plt, 'show', lambda: None)
    pipe.draw_borehole_internal(0.075)


# def test_pipe_data():
#     data = PipeData(1, 0.015, 0.02, 0.4, 0.05, 2)
#     assert data.k_g == 1
#     assert data.r_in == 0.015
#     assert data.r_out == 0.02
#     assert data.k_p == 0.4
#     assert data.D_s == 0.05
#     assert data.number_of_pipes == 2
#
# def test_pipe_data_equal():
#     data = PipeData(1, 0.015, 0.02, 0.4, 0.05, 2)
#     data2 = PipeData(1, 0.015, 0.02, 0.4, 0.05, 2)
#     assert data == data2
#
#
# def test_pipe_data_unequal():
#     data = PipeData(1, 0.015, 0.02, 0.4, 0.05, 2)
#     data2 = PipeData(1, 0.016, 0.02, 0.4, 0.05, 2)
#     assert data != data2