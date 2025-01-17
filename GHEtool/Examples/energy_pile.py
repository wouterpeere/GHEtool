import pygfunction as gt
from GHEtool import *
from GHEtool.Validation.cases import load_case

ground_data = GroundFluxTemperature(2.08, 8.3, 2.35 * 10 ** 6, 0.07)
pipe_data = MultipleUTube(1.6, 0.0105, 0.0125, 0.48, 0.55, 3)
fluid_data = FluidData(mfr=0.2)
fluid_data.import_fluid_from_pygfunction(gt.media.Fluid('MPG', 25, 15))

borefield = Borefield()
borefield.ground_data = ground_data
borefield.set_pipe_parameters(pipe_data)
borefield.set_fluid_parameters(fluid_data)
borefield.create_rectangular_borefield(5, 5, 1, 1, 25, 0.8, 0.6)
borefield.load = MonthlyGeothermalLoadAbsolute(*load_case(1))
# borefield.gfunction_calculation_object.use_cyl_correction_when_negative = False
borefield.print_temperature_profile()
