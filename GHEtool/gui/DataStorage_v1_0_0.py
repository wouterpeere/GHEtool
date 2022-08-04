from ctypes import cast as ctypes_cast, py_object as ctypes_py_object
from VariableClasses.VariableClasses import GroundData, PipeData, FluidData
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from GHEtool import Borefield


class DataStorage:
    """
    Data storage class to store the input and output variables
    """
    __slots__ = 'GD', 'T_max', 'T_min', 'simulationPeriod', 'peakHeating', \
                'peakCooling', 'monthlyLoadHeating', 'monthlyLoadHeating', 'monthlyLoadCooling', 'boreField', 'ui', \
                'determineDepth', 'unitDemand', 'unitPeak', 'FactorDemand', 'FactorPeak', 'size_bore_field', 'H_max',\
                'B_max', 'B_min', 'L_max', 'W_max', 'Size_Method', 'fluidData', 'pipeData', 'R_b_calculation_method', \
                'Depth_Method', 'optimizeLoadProfile', 'dataFile', 'headerHeating', 'headerCooling', 'numberColumns', \
                'dataUnit', 'dataSeperator', 'dataDecimal', 'fileSelected'

    def __init__(self, ui: int) -> None:
        """
        Get Values from gui and initialize DataStorage class Parameters
        :param ui: Integer of user interface ID
        """
        # get user interface id and get gui object
        self.ui = ui
        obj = ctypes_cast(self.ui, ctypes_py_object).value
        # get purpose of simulation
        idx: int = getattr(obj, 'comboBox_aim').currentIndex()  # get index of aim comboBox
        self.determineDepth: bool = idx == 1  # aim is to determine required depth
        self.size_bore_field: bool = idx == 2  # aim is to size bore field by length and width in meter
        self.optimizeLoadProfile: bool = idx == 3  # aim is to optimize load profile by selected load profile
        # get Ground data values from gui
        h: float = getattr(obj, 'doubleSpinBox_H').value() if idx != 1 else 100  # depth [m]
        b: float = getattr(obj, 'doubleSpinBox_B').value()  # borehole spacing [m]
        k_s: float = getattr(obj, 'doubleSpinBox_k_s').value()  # conductivity of the soil [W/mK]
        tg: float = getattr(obj, 'doubleSpinBox_Tg').value()  # Ground temperature at infinity [°C]
        rb: float = getattr(obj, 'doubleSpinBox_Rb').value()  # equivalent borehole resistance [mK/W]
        n_1: int = getattr(obj, 'spinBox_N_1').value()  # width of rectangular field [#]
        n_2: int = getattr(obj, 'spinBox_N_2').value()  # length of rectangular field [#]
        # create GroundData class from inputs
        self.GD: GroundData = GroundData(h, b, k_s, tg, rb, n_1, n_2)
        # get maximal and minimal temperature as well as simulation period from gui
        self.T_max: float = getattr(obj, 'doubleSpinBox_TMax').value()  # maximum temperature [°C]
        self.T_min: float = getattr(obj, 'doubleSpinBox_TMin').value()  # minimum temperature [°C]
        self.simulationPeriod: int = getattr(obj, 'spinBox_Years').value()  # simulation period [years]
        # if bore field should be sized by length and width get more values
        # maximal borehole depth [m]
        self.H_max: float = getattr(obj, 'doubleSpinBox_H').value() if self.size_bore_field else None
        # maximal borehole spacing [m]
        self.B_max: float = getattr(obj, 'doubleSpinBox_B_max').value() if self.size_bore_field else None
        # minimal borehole spacing [m]
        self.B_min: float = getattr(obj, 'doubleSpinBox_B').value() if self.size_bore_field else None
        # maximal width of bore field [m]
        self.W_max: float = getattr(obj, 'doubleSpinBox_W_max').value() if self.size_bore_field else None
        # maximal length of bore field [m]
        self.L_max: float = getattr(obj, 'doubleSpinBox_L_max').value() if self.size_bore_field else None
        # sizing method for sizing by length and width (0=fast, 1=robust)
        self.Size_Method: int = getattr(obj, 'comboBox_Size_Method').currentIndex() if self.size_bore_field else None
        # if borehole depth should be determined or bore field should be sized by length and width get depth sizing
        # method
        # sizing method for borehole depth sizing (0=fast, 1=robust)
        self.Depth_Method: int = getattr(obj, 'comboBox_depth_Method').currentIndex() if (self.size_bore_field or
                                                                                          self.determineDepth) else None
        # get equivalent borehole resistance calculation method
        # 0 = constant known value, 1 = constant unknown value, 2 = during calculation updating unknown value
        self.R_b_calculation_method: int = getattr(obj, 'comboBox_Rb_method').currentIndex()
        if self.R_b_calculation_method > 0:
            # Thermal conductivity of fluid [W/mK]
            k_f: float = getattr(obj, 'doubleSpinBox_fluid_lambda').value()
            # Mass flow rate [kg/s]
            mfr: float = getattr(obj, 'doubleSpinBox_fluid_mass_flow_rate').value()
            # Density of fluid [kg/m3]
            rho: float = getattr(obj, 'doubleSpinBox_fluid_density').value()
            # Thermal capacity of fluid [J/kgK]
            Cp: float = getattr(obj, 'doubleSpinBox_fluid_thermal_capacity').value()
            # Dynamic viscosity of fluid [Pa/s]
            mu: float = getattr(obj, 'doubleSpinBox_fluid_viscosity').value()
            # create FluidData class
            self.fluidData: FluidData = FluidData(mfr, k_f, rho, Cp, mu)
            # grout thermal conductivity [W/mK]
            k_g: float = getattr(obj, 'doubleSpinBox_grout_conductivity').value()
            # inner pipe radius [m]
            r_in: float = getattr(obj, 'doubleSpinBox_pipe_inner_radius').value()
            # outer pipe radius [m]
            r_out: float = getattr(obj, 'doubleSpinBox_pipe_outer_radius').value()
            # pipe thermal conductivity [W/mK]
            k_p: float = getattr(obj, 'doubleSpinBox_pipe_conductivity').value()
            # distance of pipe until center [m]
            d_s: float = getattr(obj, 'doubleSpinBox_pipe_distance').value()
            # borehole radius [m]
            r_b: float = getattr(obj, 'doubleSpinBox_borehole_radius').value()
            # number of pipes [#]
            numberOfPipes: int = getattr(obj, 'spinBox_number_pipes').value()
            # pipe roughness [m]
            epsilon: float = getattr(obj, 'doubleSpinBox_pipe_roughness').value()
            # burial depth [m]
            d: float = getattr(obj, 'doubleSpinBox_borehole_burial_depth').value()
            # create PipeData class
            self.pipeData: PipeData = PipeData(k_g, r_in, r_out, k_p, d_s, r_b, numberOfPipes, epsilon, d)
        else:
            # Write None to unused variables
            self.fluidData = self.pipeData = None
        # if load profile should be optimized get fileImport data
        if self.optimizeLoadProfile:
            # get filename and path of data fileImport
            self.dataFile: str = getattr(obj, 'lineEdit_filename_data_file').text()
            # get seperator for data fileImport
            self.dataSeperator: int = getattr(obj, 'comboBox_SeperatorDataFile').currentIndex()
            # get decimal sign for data fileImport
            self.dataDecimal: int = getattr(obj, 'comboBox_decimalDataFile').currentIndex()
            # get number of columns (if heating and cooling are in same line (1) or different lines (2))
            self.numberColumns: int = getattr(obj, 'comboBox_dataColumn_data_file').currentIndex()
            # get data unit
            self.dataUnit: int = getattr(obj, 'comboBox_dataUnit_data_file').currentIndex()
            # get header names depending on if it is one or two
            if self.numberColumns == 0:
                self.headerHeating: str = getattr(obj, 'comboBox_heatingLoad_data_file').currentText()
                self.headerCooling: str = getattr(obj, 'comboBox_coolingLoad_data_file').currentText()
            else:
                self.headerHeating: str = getattr(obj, 'comboBox_combined_data_file').currentText()
                self.headerCooling: str = ''
        else:
            self.dataFile = self.numberColumns = self.dataUnit = self.headerHeating = self.headerCooling = \
                self.dataSeperator = self.dataDecimal = None
        # get unit for peak loads and demand loads
        self.unitPeak: str = getattr(obj, 'label_Unit_pH').text()
        self.unitDemand: str = getattr(obj, 'label_Unit_HL').text()
        u_p = self.unitPeak[1:-1]
        u_d = self.unitDemand[1:-1]
        # determine factors for unit updating
        self.FactorPeak: float = 1 if u_p == 'kW' else 0.001 if u_p == 'W' else 1000
        self.FactorDemand: float = 1 if u_d == 'kWh' else 0.001 if u_d == 'Wh' else 1000
        # Write peak heating load for every month into a list [kW]
        self.peakHeating: list = [getattr(obj, 'doubleSpinBox_Hp_Jan').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Feb').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Mar').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Apr').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_May').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Jun').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Jul').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Aug').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Sep').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Oct').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Nov').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Hp_Dec').value() * self.FactorPeak]
        # Write peak cooling load for every month into a list [kW]
        self.peakCooling: list = [getattr(obj, 'doubleSpinBox_Cp_Jan').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Feb').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Mar').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Apr').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_May').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Jun').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Jul').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Aug').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Sep').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Oct').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Nov').value() * self.FactorPeak,
                                  getattr(obj, 'doubleSpinBox_Cp_Dec').value() * self.FactorPeak]
        # Write monthly heating demand for every month into a list [kWh]
        self.monthlyLoadHeating: list = [getattr(obj, 'doubleSpinBox_HL_Jan').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Feb').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Mar').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Apr').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_May').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Jun').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Jul').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Aug').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Sep').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Oct').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Nov').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_HL_Dec').value() * self.FactorDemand]
        # Write monthly cooling demand for every month into a list [kWh]
        self.monthlyLoadCooling: list = [getattr(obj, 'doubleSpinBox_CL_Jan').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Feb').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Mar').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Apr').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_May').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Jun').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Jul').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Aug').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Sep').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Oct').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Nov').value() * self.FactorDemand,
                                         getattr(obj, 'doubleSpinBox_CL_Dec').value() * self.FactorDemand]
        # initialize bore field
        self.boreField: Optional[Borefield, None] = None
        # check if a file for optimizing the load profile has been selected
        self.fileSelected: bool = (self.optimizeLoadProfile and self.dataFile == '')

    def set_values(self) -> None:
        """Set Values to gui"""
        # get gui object
        obj = ctypes_cast(self.ui, ctypes_py_object).value
        # determine and set purpose of simulation
        idx: int = 1 if self.determineDepth else 2 if self.size_bore_field else 3 if self.optimizeLoadProfile else 0
        getattr(obj, 'comboBox_aim').setCurrentIndex(idx)
        # set ground data values
        getattr(obj, 'doubleSpinBox_H').setValue(self.GD.H)  # depth [m]
        getattr(obj, 'doubleSpinBox_B').setValue(self.GD.B)  # borehole spacing [m]
        getattr(obj, 'doubleSpinBox_k_s').setValue(self.GD.k_s)  # conductivity of the soil [W/mK]
        getattr(obj, 'doubleSpinBox_Tg').setValue(self.GD.Tg)  # Ground temperature at infinity [°C]
        getattr(obj, 'doubleSpinBox_Rb').setValue(self.GD.Rb)  # equivalent borehole resistance [mK/W]
        getattr(obj, 'spinBox_N_1').setValue(self.GD.N_1)  # width of rectangular field [#]
        getattr(obj, 'spinBox_N_2').setValue(self.GD.N_2)  # length of rectangular field [#]
        # set maximal and minimal temperature as well as simulation period
        getattr(obj, 'doubleSpinBox_TMax').setValue(self.T_max)  # maximum temperature [°C]
        getattr(obj, 'doubleSpinBox_TMin').setValue(self.T_min)  # minimum temperature [°C]
        getattr(obj, 'spinBox_Years').setValue(self.simulationPeriod)  # simulation period [years]
        # set peak and demand unit
        getattr(obj, 'label_Unit_pH').setText(self.unitPeak)
        getattr(obj, 'label_Unit_pC').setText(self.unitPeak)
        getattr(obj, 'label_Unit_HL').setText(self.unitDemand)
        getattr(obj, 'label_Unit_CL').setText(self.unitDemand)
        # if bore field should be sized by length and width set more values
        if self.size_bore_field:
            getattr(obj, 'doubleSpinBox_H').setValue(self.H_max)  # maximal borehole depth [m]
            getattr(obj, 'doubleSpinBox_B_max').setValue(self.B_max)  # maximal borehole spacing [m]
            getattr(obj, 'doubleSpinBox_B').setValue(self.B_min)  # minimal borehole spacing [m]
            getattr(obj, 'doubleSpinBox_W_max').setValue(self.W_max)  # maximal width of bore field [m]
            getattr(obj, 'doubleSpinBox_L_max').setValue(self.L_max)  # maximal length of bore field [m]
            # sizing method for sizing by length and width (0=fast, 1=robust)
            getattr(obj, 'comboBox_Size_Method').setCurrentIndex(self.Size_Method)
        # if borehole depth should be determined or bore field should be sized by length and width get depth sizing
        # method
        # sizing method for borehole depth sizing (0=fast, 1=robust)
        getattr(obj, 'comboBox_depth_Method').setCurrentIndex(self.Depth_Method) if (self.size_bore_field or
                                                                                     self.determineDepth) else None
        # set equivalent borehole resistance calculation method
        # 0 = constant known value, 1 = constant unknown value, 2 = during calculation updating unknown value
        getattr(obj, 'comboBox_Rb_method').setCurrentIndex(self.R_b_calculation_method)
        if self.R_b_calculation_method > 0:
            getattr(obj, 'doubleSpinBox_fluid_lambda').setValue(self.fluidData.k_f)  # Thermal conductivity [W/mK]
            getattr(obj, 'doubleSpinBox_fluid_mass_flow_rate').setValue(self.fluidData.mfr)  # Mass flow rate [kg/s]
            getattr(obj, 'doubleSpinBox_fluid_density').setValue(self.fluidData.rho)  # Density [kg/m3]
            getattr(obj, 'doubleSpinBox_fluid_thermal_capacity').setValue(self.fluidData.Cp)  # Thermal capacity [J/kgK]
            getattr(obj, 'doubleSpinBox_fluid_viscosity').setValue(self.fluidData.mu)  # Dynamic viscosity [Pa s]
            # grout thermal conductivity [W/mK]
            getattr(obj, 'doubleSpinBox_grout_conductivity').setValue(self.pipeData.k_g)
            getattr(obj, 'doubleSpinBox_pipe_inner_radius').setValue(self.pipeData.r_in)  # inner pipe radius [m]
            getattr(obj, 'doubleSpinBox_pipe_outer_radius').setValue(self.pipeData.r_out)  # outer pipe radius [m]
            # pipe thermal conductivity [W/mK]
            getattr(obj, 'doubleSpinBox_pipe_conductivity').setValue(self.pipeData.k_p)
            getattr(obj, 'doubleSpinBox_pipe_distance').setValue(self.pipeData.D_s)  # distance of pipe until center [m]
            getattr(obj, 'doubleSpinBox_borehole_radius').setValue(self.pipeData.r_b)  # borehole radius [m]
            getattr(obj, 'spinBox_number_pipes').setValue(self.pipeData.number_of_pipes)  # number of pipes [#]
            getattr(obj, 'doubleSpinBox_pipe_roughness').setValue(self.pipeData.epsilon)  # pipe roughness [m]
            getattr(obj, 'doubleSpinBox_borehole_burial_depth').setValue(self.pipeData.D)  # burial depth [m]
        # if load profile should be optimized get fileImport data
        if self.optimizeLoadProfile:
            # set filename and path of data fileImport
            getattr(obj, 'lineEdit_filename_data_file').setText(self.dataFile)
            # set seperator for data fileImport
            getattr(obj, 'comboBox_SeperatorDataFile').setCurrentIndex(self.dataSeperator)
            # get decimal sign for data fileImport
            getattr(obj, 'comboBox_decimalDataFile').setCurrentIndex(self.dataDecimal)
            # set number of columns (if heating and cooling are in same line (1) or different lines (2))
            getattr(obj, 'comboBox_dataColumn_data_file').setCurrentIndex(self.numberColumns)
            # set data unit
            getattr(obj, 'comboBox_dataUnit_data_file').setCurrentIndex(self.dataUnit)
            # set header names depending on if it is one or two
            if self.numberColumns == 0:
                getattr(obj, 'comboBox_heatingLoad_data_file').setCurrentText(self.headerHeating)
                getattr(obj, 'comboBox_coolingLoad_data_file').setCurrentText(self.headerCooling)
            else:
                getattr(obj, 'comboBox_combined_data_file').setCurrentText(self.headerHeating)
        # Write monthly heating demand for every month from list [kWh]
        getattr(obj, 'doubleSpinBox_Hp_Jan').setValue(self.peakHeating[0] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Feb').setValue(self.peakHeating[1] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Mar').setValue(self.peakHeating[2] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Apr').setValue(self.peakHeating[3] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_May').setValue(self.peakHeating[4] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Jun').setValue(self.peakHeating[5] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Jul').setValue(self.peakHeating[6] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Aug').setValue(self.peakHeating[7] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Sep').setValue(self.peakHeating[8] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Oct').setValue(self.peakHeating[9] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Nov').setValue(self.peakHeating[10] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Hp_Dec').setValue(self.peakHeating[11] / self.FactorPeak)
        # Write monthly cooling demand for every month from list [kWh]
        getattr(obj, 'doubleSpinBox_Cp_Jan').setValue(self.peakCooling[0] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Feb').setValue(self.peakCooling[1] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Mar').setValue(self.peakCooling[2] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Apr').setValue(self.peakCooling[3] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_May').setValue(self.peakCooling[4] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Jun').setValue(self.peakCooling[5] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Jul').setValue(self.peakCooling[6] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Aug').setValue(self.peakCooling[7] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Sep').setValue(self.peakCooling[8] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Oct').setValue(self.peakCooling[9] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Nov').setValue(self.peakCooling[10] / self.FactorPeak)
        getattr(obj, 'doubleSpinBox_Cp_Dec').setValue(self.peakCooling[11] / self.FactorPeak)
        # Write monthly peak heating load for every month from list [kW]
        getattr(obj, 'doubleSpinBox_HL_Jan').setValue(self.monthlyLoadHeating[0] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Feb').setValue(self.monthlyLoadHeating[1] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Mar').setValue(self.monthlyLoadHeating[2] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Apr').setValue(self.monthlyLoadHeating[3] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_May').setValue(self.monthlyLoadHeating[4] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Jun').setValue(self.monthlyLoadHeating[5] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Jul').setValue(self.monthlyLoadHeating[6] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Aug').setValue(self.monthlyLoadHeating[7] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Sep').setValue(self.monthlyLoadHeating[8] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Oct').setValue(self.monthlyLoadHeating[9] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Nov').setValue(self.monthlyLoadHeating[10] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_HL_Dec').setValue(self.monthlyLoadHeating[11] / self.FactorDemand)
        # Write monthly peak cooling load for every month from list [kW]
        getattr(obj, 'doubleSpinBox_CL_Jan').setValue(self.monthlyLoadCooling[0] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Feb').setValue(self.monthlyLoadCooling[1] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Mar').setValue(self.monthlyLoadCooling[2] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Apr').setValue(self.monthlyLoadCooling[3] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_May').setValue(self.monthlyLoadCooling[4] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Jun').setValue(self.monthlyLoadCooling[5] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Jul').setValue(self.monthlyLoadCooling[6] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Aug').setValue(self.monthlyLoadCooling[7] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Sep').setValue(self.monthlyLoadCooling[8] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Oct').setValue(self.monthlyLoadCooling[9] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Nov').setValue(self.monthlyLoadCooling[10] / self.FactorDemand)
        getattr(obj, 'doubleSpinBox_CL_Dec').setValue(self.monthlyLoadCooling[11] / self.FactorDemand)

    def __eq__(self, other) -> bool:
        """
        equality function to check if values are equal
        :param other: to compare Datastorage
        :return: boolean which is true if self has the same values as other
        """
        # if not of same class return false
        if not isinstance(other, DataStorage):
            return False
        # compare all slot values if one not match return false
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        # if all match return true
        return True
