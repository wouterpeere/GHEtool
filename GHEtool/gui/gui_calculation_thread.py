from PySide6.QtCore import QThread as QtCore_QThread
from PySide6.QtCore import Signal as QtCore_pyqtSignal

from GHEtool.gui.gui_data_storage import DataStorage
from GHEtool.gui.gui_structure import load_data_GUI


class BoundsOfPrecalculatedData:
    """
    class to check if selected values are within the bounds for the precalculated data
    """

    __slots__ = "H", "B_Min", "B_Max", "k_s_Min", "k_s_Max", "N_Max"

    def __init__(self) -> None:
        self.H: float = 350.0  # Maximal depth [m]
        self.B_Max: float = 9.0  # Maximal borehole spacing [m]
        self.B_Min: float = 3.0  # Minimal borehole spacing [m]
        self.k_s_Min: float = 1  # Minimal thermal conductivity of the soil [W/mK]
        self.k_s_Max: float = 4  # Maximal thermal conductivity of the soil [W/mK]
        self.N_Max: int = 20  # Maximal number of boreholes in one direction [#]

    def check_if_outside_bounds(self, h: float, b: float, k_s: float, n: int) -> bool:
        """
        Check if selected values are within the bounds for the precalculated data
        :param h: depth [m]
        :param b: Spacings [m]
        :param k_s: Thermal conductivity of the soil [W/mK]
        :param n: Maximal number of borehole in one rectangular field direction
        :return: true if outside of bounds
        """
        if h > self.H:
            return True
        if not (self.B_Min <= b <= self.B_Max):
            return True
        if not (self.k_s_Min <= k_s <= self.k_s_Max):
            return True
        if n > self.N_Max:
            return True
        return False


class CalcProblem(QtCore_QThread):
    """
    class to calculate the problem in an external thread
    """

    any_signal = QtCore_pyqtSignal(tuple)

    def __init__(self, ds: DataStorage, idx: int, parent=None) -> None:
        """
        initialize calculation class
        :param ds: datastorage to perform calculation for
        :param idx: index of current thread
        :param parent: parent class
        """
        super(CalcProblem, self).__init__(parent)  # init parent class
        # set datastorage and index
        self.DS = ds
        self.idx = idx

    def run(self) -> None:
        """
        run calculations
        :return: None
        """
        # import bore field class from GHEtool and not in start up to save time
        from GHEtool import Borefield

        # create the bore field object
        borefield = Borefield(
            simulation_period=self.DS.option_simu_period,
            borefield=self.DS.borefield_pygfunction,
            gui=True,
        )
        # set temperature boundaries
        borefield.set_max_ground_temperature(self.DS.option_max_temp)  # maximum temperature
        borefield.set_min_ground_temperature(self.DS.option_min_temp)  # minimum temperature

        # set ground data
        borefield.set_ground_parameters(self.DS.ground_data)

        ### GENERAL SETUPS

        # check if Rb is a constant, otherwise set the fluid/pipe parameters
        if self.DS.option_method_rb_calc > 0:
            # Rb will be dynamically calculated
            # set fluid and pipe data
            borefield.set_fluid_parameters(self.DS.fluid_data)
            borefield.set_pipe_parameters(self.DS.pipe_data)

        # set monthly loads
        borefield.set_peak_heating(self.DS.peakHeating)
        borefield.set_peak_cooling(self.DS.peakCooling)
        borefield.set_baseload_heating(self.DS.monthlyLoadHeating)
        borefield.set_baseload_cooling(self.DS.monthlyLoadCooling)

        # set hourly loads if available
        if self.DS.option_method_size_depth == 2:
            data_unit = self.DS.option_unit_data

            peak_heating, peak_cooling = load_data_GUI(
                filename=self.DS.option_filename,
                thermal_demand=self.DS.option_column,
                heating_load_column=self.DS.option_heating_column,
                cooling_load_column=self.DS.option_cooling_column,
                combined=self.DS.option_single_column,
                sep=";" if self.DS.option_seperator_csv == 0 else ",",
                dec="." if self.DS.option_decimal_csv == 0 else ",",
                fac=0.001 if data_unit == 0 else 1 if data_unit == 1 else 1000,
                hourly=True)

            # hourly data to be loaded
            borefield.set_hourly_heating_load(peak_heating)
            borefield.set_hourly_cooling_load(peak_cooling)

        # setup the borefield sizing
        borefield.sizing_setup(H_init=self.DS.borefield_pygfunction[0].H,
                               use_constant_Rb=self.DS.option_method_rb_calc == 0,
                               use_constant_Tg=self.DS.option_method_temp_gradient == 0,
                               L2_sizing=self.DS.option_method_size_depth == 0,
                               L3_sizing=self.DS.option_method_size_depth == 1,
                               L4_sizing=self.DS.option_method_size_depth == 2)

        ### FUNCTIONALITIES (i.e. aims)

        # if load should be optimized do this
        if self.DS.aim_optimize:
            # get column and decimal seperator
            sep: str = ";" if self.DS.option_seperator_csv == 0 else ","
            dec: str = "." if self.DS.option_decimal_csv == 0 else ","
            # import pandas here to save start up time
            from pandas import read_csv as pd_read_csv

            # load data from csv file
            try:
                data = pd_read_csv(self.DS.filename, sep=sep, decimal=dec)
            except FileNotFoundError:
                self.any_signal.emit((self.DS, self.idx))
                return
            # get data unit factor of energy demand
            unit: float = 0.001 if self.DS.option_unit_data == 0 else 1 if self.DS.option_unit_data == 1 else 1_000
            # if data is in 2 column create a list of the loaded data else sepperate data by >0 and <0 and then create a
            # list and muliplty in both cases with the unit factor to achive data in kW
            if self.DS.option_column == 1:
                print(data.columns[self.DS.option_heating_column])
                borefield.hourly_heating_load = data[data.columns[self.DS.option_heating_column]] * unit
                borefield.hourly_cooling_load = data[data.columns[self.DS.option_cooling_column]] * unit
            else:
                borefield.hourly_heating_load = data[data.columns[self.DS.option_single_column]].apply(lambda x: x >= 0) * unit
                borefield.hourly_cooling_load = data[data.columns[self.DS.option_single_column]].apply(lambda x: x < 0) * unit
            # optimize load profile without printing the results
            borefield.optimise_load_profile(depth=self.DS.ground_data.H, print_results=False)
            # save bore field in Datastorage
            self.DS.borefield = borefield
            # return Datastorage as signal
            self.any_signal.emit((self.DS, self.idx))
            return

        ### Size borefield
        if self.DS.aim_req_depth:
            try:
                # size the borehole
                borefield.size()

            except RuntimeError or ValueError:
                # save bore field in Datastorage
                self.DS.borefield = None
                self.DS.ErrorMessage = self.translation.NotCalculated
                # return Datastorage as signal
                self.any_signal.emit((self.DS, self.idx))
                return

        ### Size borefield by length and width
        if self.DS.aim_size_length:
            try:
                # To be implemented
                # option_method_size_length
                pass
            except RuntimeError or ValueError:
                # save bore field in Datastorage
                self.DS.borefield = None
                # return Datastorage as signal
                self.any_signal.emit((self.DS, self.idx))
                return

        ### Plot temperature profile
        if self.DS.aim_temp_profile:
            # try to calculate temperatures
            try:
                borefield.calculate_temperatures(borefield.H)
            except ValueError:
                pass

        # save borefield in Datastorage
        self.DS.borefield = borefield
        # return Datastorage as signal
        self.any_signal.emit((self.DS, self.idx))
        return
