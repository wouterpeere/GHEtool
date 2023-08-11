import multiprocessing
from GHEtool import Borefield, GroundConstantTemperature, MonthlyGeothermalLoadAbsolute
import pygfunction as gt

def calc(borefield: Borefield, queue):
    borefield.size()
    queue.put(borefield)

def main():

    data = GroundConstantTemperature(3, 10)
    borefield_64 = gt.boreholes.rectangle_field(8, 8, 6, 6, 110, 1, 0.075)

    # monthly loading values
    peak_cooling = [0., 0, 34., 69., 133., 187., 213., 240., 160., 37., 0., 0.]  # Peak cooling in kW
    peak_heating = [160., 142, 102., 55., 0., 0., 0., 0., 40.4, 85., 119., 136.]  # Peak heating in kW

    # annual heating and cooling load
    annual_heating_load = 300 * 10 ** 3  # kWh
    annual_cooling_load = 160 * 10 ** 3  # kWh

    # percentage of annual load per month (15.5% for January ...)
    monthly_load_heating_percentage = [0.155, 0.148, 0.125, .099, .064, 0., 0., 0., 0.061, 0.087, 0.117, 0.144]
    monthly_load_cooling_percentage = [0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025]

    # resulting load per month
    monthly_load_heating = list(map(lambda x: x * annual_heating_load, monthly_load_heating_percentage))  # kWh
    monthly_load_cooling = list(map(lambda x: x * annual_cooling_load, monthly_load_cooling_percentage))  # kWh

    # set the load
    load = MonthlyGeothermalLoadAbsolute(monthly_load_heating, monthly_load_cooling, peak_heating, peak_cooling)

    # create the borefield object
    borefield = Borefield(load=load, gui=True)

    borefield.set_ground_parameters(data)
    borefield.set_borefield(borefield_64)
    borefield.Rb = 0.2

    # set temperature boundaries
    borefield.set_max_ground_temperature(16)  # maximum temperature
    borefield.set_min_ground_temperature(0)  # minimum temperature

    # precalculate
    #borefield.create_custom_dataset()

    # size borefield
    #depth_precalculated = borefield.size()
    queue = multiprocessing.Queue()
    process: multiprocessing.Process = multiprocessing.Process(target=calc, args=(borefield,queue))
    process.start()
    process.join(timeout=6)
    print(process.is_alive())

if __name__ == '__main__':
    main()