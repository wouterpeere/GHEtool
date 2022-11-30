"""
This document contains all the code related to calculating the solution to the different
aims in the GUI.
"""
from PySide6.QtCore import QThread as QtCore_QThread
from PySide6.QtCore import Signal as QtCore_pyqtSignal

from GHEtool.gui.gui_data_storage import DataStorage
from GHEtool.gui.gui_structure import load_data_GUI


class CalcProblem(QtCore_QThread):
    """
    class to calculate the problem in an external thread
    """

    any_signal = QtCore_pyqtSignal(tuple)

    def __init__(self, ds: DataStorage, idx: int, parent=None) -> None:
        """
        This function initialises the calculation class.

        Parameters
        ----------
        ds : DataStorage
            DataStorage object with all the date to perform the calculation for
        idx : int
            Index of the current calculation thread
        parent :
            Parent class of the calculation problem
        """
        super(CalcProblem, self).__init__(parent)  # init parent class
        # set datastorage and index
        self.DS = ds
        self.idx = idx

    def run(self) -> None:
        """
        This function contains the actual code to run the different calculations.
        For each aim in the GUI, a new if statement is used. Here, one can put all the code
        needed to run the simulation/calculation with the all the functionalities of GHEtool.
        This function should return the DataStorage as a signal.

        Returns
        -------
        None
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
        if self.DS.hourly_data:
            data_unit = self.DS.option_unit_data

            peak_heating, peak_cooling = load_data_GUI(
                filename=self.DS.option_filename,
                thermal_demand=self.DS.option_column,
                heating_load_column=self.DS.option_heating_column_text,
                cooling_load_column=self.DS.option_cooling_column_text,
                combined=self.DS.option_single_column_text,
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
            try:
                # optimize load profile without printing the results
                borefield.optimise_load_profile()
            except ValueError as err:
                self.DS.debug_message = err
                # save bore field in Datastorage
                self.DS.borefield = None
                # return Datastorage as signal
                self.any_signal.emit((self.DS, self.idx))
                return
            except RuntimeError:
                # save bore field in Datastorage
                self.DS.borefield = None
                self.DS.ErrorMessage = self.translation.NotCalculated
                # return Datastorage as signal
                self.any_signal.emit((self.DS, self.idx))
                return

        ### Size borefield
        if self.DS.aim_req_depth:
            try:
                # size the borehole
                borefield.size()
            except ValueError as err:
                self.DS.debug_message = err
                # save bore field in Datastorage
                self.DS.borefield = None
                # return Datastorage as signal
                self.any_signal.emit((self.DS, self.idx))
                return
            except RuntimeError:
                # save bore field in Datastorage
                self.DS.borefield = None
                self.DS.ErrorMessage = self.translation.NotCalculated
                # return Datastorage as signal
                self.any_signal.emit((self.DS, self.idx))
                return

        ### Size borefield by length and width
        # if self.DS.aim_size_length:
        #     try:
        #         # To be implemented
        #         # option_method_size_length
        #         pass
        #     except RuntimeError or ValueError:
        #         # save bore field in Datastorage
        #         self.DS.borefield = None
        #         # return Datastorage as signal
        #         self.any_signal.emit((self.DS, self.idx))
        #         return

        ### Plot temperature profile
        if self.DS.aim_temp_profile:
            # try to calculate temperatures
            try:
                borefield.calculate_temperatures(borefield.H)
            except ValueError:
                pass

        # set debug message to ""
        self.DS.debug_message = ""

        # save borefield in Datastorage
        self.DS.borefield = borefield
        # return Datastorage as signal
        self.any_signal.emit((self.DS, self.idx))
        return
