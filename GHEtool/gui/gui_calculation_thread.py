from pickle import load as pk_load
from typing import Tuple

from PySide6.QtCore import QThread as QtCore_QThread
from PySide6.QtCore import Signal as QtCore_pyqtSignal

from GHEtool.gui.gui_data_storage import DataStorage


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
            peak_heating=self.DS.peakHeating,
            peak_cooling=self.DS.peakCooling,
            baseload_heating=self.DS.monthlyLoadHeating,
            baseload_cooling=self.DS.monthlyLoadCooling,
            gui=True,
        )
        # set temperature boundaries
        borefield.set_max_ground_temperature(self.DS.option_max_temp)  # maximum temperature
        borefield.set_min_ground_temperature(self.DS.option_min_temp)  # minimum temperature
        # set ground data
        borefield.set_ground_parameters(self.DS.ground_data)
        # check bounds of precalculated data
        bopd: BoundsOfPrecalculatedData = BoundsOfPrecalculatedData()
        outside_bounds: bool = bopd.check_if_outside_bounds(
            self.DS.ground_data.H, self.DS.ground_data.B, self.DS.ground_data.k_s, max(self.DS.ground_data.N_1, self.DS.ground_data.N_2)
        )
        # set default value for constant Rb calculation
        use_constant_rb: bool = True
        # check if Rb is unknown
        if self.DS.option_method_rb_calc > 0:
            # set fluid and pipe data
            borefield.set_fluid_parameters(self.DS.fluid_data)
            borefield.set_pipe_parameters(self.DS.pipe_data)
            # set use_constant_rb to False if R_b_calculation_method == 2
            use_constant_rb: bool = self.DS.option_method_rb_calc == 1
            # set Rb to the new calculated one if a constant unknown Rb is selected
            borefield.Rb = borefield.calculate_Rb() if use_constant_rb else self.DS.ground_data.Rb
        # create custom rectangle bore field if no precalculated data is available
        if outside_bounds:
            # import boreholes from pygfuntion here to save start up time
            from pygfunction import boreholes as gt_boreholes

            # get minimum and maximal number of boreholes in one direction
            n_max: int = max(self.DS.ground_data.N_1, self.DS.ground_data.N_2)
            n_min: int = max(self.DS.ground_data.N_1, self.DS.ground_data.N_2)
            # initialize custom field with variables selected
            custom_field = gt_boreholes.rectangle_field(
                N_1=n_max, N_2=n_min, B_1=self.DS.ground_data.B, B_2=self.DS.ground_data.B, H=self.DS.ground_data.H, D=4, r_b=0.075
            )
            # create name of custom bore field to save it later
            borefield_custom: str = f"customField_{n_max}_{n_min}_{self.DS.ground_data.B}_{self.DS.ground_data.k_s}"
            # try if the bore field has already be calculated then open this otherwise calculate it
            try:
                from pathlib import Path, PurePath
                from os.path import dirname, realpath, exists
                from os import makedirs
                file_path: str = str(PurePath(Path.home(), 'Documents/GHEtool/Data/', "{borefield_custom}.pickle"))
                makedirs(dirname(file_path), exist_ok=True)
                pk_load(open(file_path, "rb"))
            except FileNotFoundError:
                borefield.create_custom_dataset(custom_field, borefield_custom)
            # set new bore field g-function
            borefield.set_custom_gfunction(borefield_custom)
            # set bore field to custom one
            borefield.set_borefield(custom_field)

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
        if self.DS.aim_req_depth:
            try:
                # size the borehole depth if wished
                borefield.size(
                    self.DS.ground_data.H,
                    L2_sizing=self.DS.option_method_size_depth == 0,
                    L3_sizing=self.DS.option_method_size_depth == 1,
                    L4_sizing=self.DS.option_method_size_depth == 2,
                    use_constant_Rb=use_constant_rb,
                )
            except RuntimeError or ValueError:
                # save bore field in Datastorage
                self.DS.borefield = None

                self.DS.ErrorMessage = self.translation.NotCalculated
                # return Datastorage as signal
                self.any_signal.emit((self.DS, self.idx))
                return

        if self.DS.aim_size_length:
            try:
                # size bore field by length and width either fast (Size_Method == 0) or robust (Size_Method == 1)
                if self.DS.option_method_size_length == 0:
                    borefield.size_complete_field_fast(
                        H_max=self.DS.option_max_depth,
                        l_1=self.DS.option_max_width,
                        l_2=self.DS.option_max_length,
                        B_min= self.DS.option_min_spacing,
                        B_max=self.DS.option_max_spacing,
                        L2_sizing=self.DS.option_method_size_depth == 0,
                        use_constant_Rb=use_constant_rb,
                    )
                else:
                    borefield.size_complete_field_robust(
                        H_max=self.DS.option_max_depth,
                        l_1=self.DS.option_max_width,
                        l_2=self.DS.option_max_length,
                        B_min= self.DS.option_min_spacing,
                        B_max=self.DS.option_max_spacing,
                        L2_sizing=self.DS.option_method_size_depth == 0,
                        use_constant_Rb=use_constant_rb,
                    )
            except RuntimeError or ValueError:
                # save bore field in Datastorage
                self.DS.borefield = None
                # return Datastorage as signal
                self.any_signal.emit((self.DS, self.idx))
                return
        # try to calculate temperatures
        try:
            borefield.calculate_temperatures(borefield.H)
        except ValueError:
            pass
        # save bore field in Datastorage
        self.DS.borefield = borefield
        # return Datastorage as signal
        self.any_signal.emit((self.DS, self.idx))
        return
