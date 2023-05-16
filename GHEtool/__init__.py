import pathlib

from GHEtool.main_class import Borefield
from GHEtool.VariableClasses import GroundData, PipeData, CustomGFunction, GFunction, ConstantFluidData, LinearFluidData
from GHEtool.VariableClasses import SizingSetup
FOLDER: pathlib.Path = pathlib.Path(__file__).parent  # solve problem with importing GHEtool from sub-folders
