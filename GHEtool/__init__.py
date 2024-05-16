import pathlib

from GHEtool.Borefield import Borefield
from GHEtool.VariableClasses import *
FOLDER: pathlib.Path = pathlib.Path(__file__).parent  # solve problem with importing GHEtool from sub-folders
from GHEtool.logger import ghe_logger
