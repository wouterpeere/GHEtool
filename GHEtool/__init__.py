import pathlib

from GHEtool.main_class import Borefield
from GHEtool.VariableClasses import CustomGFunction, FluidData, GFunction, GroundData, PipeData, SizingSetup

FOLDER: pathlib.Path = pathlib.Path(__file__).parent  # solve problem with importing GHEtool from sub-folders
from GHEtool.logger import ghe_logger
