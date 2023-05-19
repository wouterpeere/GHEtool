import pathlib

from GHEtool.main_class import Borefield
from GHEtool.VariableClasses import FluidData, GroundData, PipeData, CustomGFunction, GFunction
from GHEtool.VariableClasses import SizingSetup
FOLDER: pathlib.Path = pathlib.Path(__file__).parent  # solve problem with importing GHEtool from sub-folders
