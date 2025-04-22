from GHEtool import *
import optuna
import numpy as np
from functools import cache

import pygfunction as gt

# set general parameters
ground_data = GroundFluxTemperature(3, 10)
fluid_data = ConstantFluidData(0.2, 0.568, 998, 4180, 1e-3)
flow_data = ConstantFlowRate(mfr=0.2)
pipe_data = DoubleUTube(1, 0.015, 0.02, 0.4, 0.05)

load = HourlyBuildingLoad()  # use SCOP of 5 for heating
load.load_hourly_profile(FOLDER.joinpath("test\methods\hourly_data\\auditorium.csv"), header=True,
                         separator=";", col_cooling=1, col_heating=0)

borefield = Borefield(ground_data=ground_data,
                      flow_data=flow_data,
                      fluid_data=fluid_data,
                      pipe_data=pipe_data,
                      load=load)
borefield.set_max_avg_fluid_temperature(20)
borefield.set_min_avg_fluid_temperature(3)

width = 60
length = 40
B_min = 5
B_max = 10

min_nb_x = int(width / B_max)
max_nb_x = int(width / B_min)
min_nb_y = int(length / B_max)
max_nb_y = int(length / B_min)

print(f'Line: 1 - {max(min_nb_x, min_nb_y)} - {max(max_nb_x, max_nb_y)}')
print(f'L: 1 - {min_nb_x + min_nb_y - 1} - {max_nb_x + max_nb_y - 1}')
temp = max(max_nb_x, max_nb_y)
temp_min = min(max_nb_x, max_nb_y)
temp_max = max(temp, 2 * temp_min)
short = temp_max != temp
temp2 = max(min_nb_x, min_nb_y)
temp_min2 = min(min_nb_x, min_nb_y)
temp_max2 = max(temp, 2 * temp_min)
short2 = temp_max2 != temp2
print(
    f'U: 1 - {(temp2 if short2 else temp_min2) + 2 * (temp2 if not short2 else temp_min2) - 2} - {(temp if short else temp_min) + 2 * (temp if not short else temp_min) - 2}')
print(f'box: 1 - {min_nb_x * 2 + min_nb_y * 2 - 4} - {max_nb_x * 2 + max_nb_y * 2 - 4}')
print(f'rectangle: 1 - {min_nb_x * min_nb_y} - {max_nb_x * max_nb_y}')

range_line_max = {}
range_line_min = {}
range_L_max = {}
range_L_min = {}
range_U_max = {}
range_U_min = {}
range_box_max = {}
range_box_min = {}
range_rectangle_max = {}
range_rectangle_min = {}


@cache
def line(x, y):
    temp = gt.boreholes.rectangle_field(x, y, max(B_max, width / x), max(B_max, length / y), 100, 0.7, 0.07)
    return len(temp), temp


@cache
def L(x, y):
    temp = gt.boreholes.L_shaped_field(x, y, max(B_max, width / x), max(B_max, length / y), 100, 0.7, 0.07)
    return len(temp), temp


@cache
def U(x, y):
    temp = gt.boreholes.U_shaped_field(x, y, max(B_max, width / x), max(B_max, length / y), 100, 0.7, 0.07)
    return len(temp), temp


@cache
def box(x, y):
    temp = gt.boreholes.box_shaped_field(x, y, max(B_max, width / x), max(B_max, length / y), 100, 0.7, 0.07)
    return len(temp), temp


@cache
def rectangle(x, y):
    temp = gt.boreholes.rectangle_field(x, y, max(B_max, width / x), max(B_max, length / y), 100, 0.7, 0.07)
    return len(temp), temp


for x in range(1, min_nb_x + 1):
    for y in range(1, min_nb_y + 1):
        range_line_max[x] = (x, 1, 'line')
        range_L_max[L(x, y)[0]] = (x, y, 'L')
        range_U_max[U(x, y)[0]] = (x, y, 'U')
        range_box_max[box(x, y)[0]] = (x, y, 'box')
        range_rectangle_max[rectangle(x, y)[0]] = (x, y, 'rect')

for x in range(1, max_nb_x + 1):
    for y in range(1, max_nb_y + 1):
        range_line_min[x] = (x, 1, 'line')
        range_L_min[L(x, y)[0]] = (x, y, 'L')
        range_U_min[U(x, y)[0]] = (x, y, 'U')
        range_box_min[box(x, y)[0]] = (x, y, 'box')
        range_rectangle_min[rectangle(x, y)[0]] = (x, y, 'rect')

range_to_optimise = [range_line_max, range_line_min, range_L_max, range_L_min, range_U_max, range_U_min,
                     range_box_max, range_box_min, range_rectangle_max, range_rectangle_min]


@cache
def size(x, y, form):
    if form == 'line':
        borefield.borefield = line(x, y)[1]
    elif form == 'U':
        borefield.borefield = U(x, y)[1]
    elif form == 'L':
        borefield.borefield = L(x, y)[1]
    elif form == 'box':
        borefield.borefield = box(x, y)[1]
    else:
        borefield.borefield = rectangle(x, y)[1]
    try:
        depth = borefield.size_L3()
    except:
        depth = np.nan
    return depth


for range in range_to_optimise:
    for config in range:
        x, y, form = range[config]

        depth = size(x, y, form)
        print(f'{range[config]} - {config} - {depth * config:.2f}m')
        range[config] = depth * x * y
