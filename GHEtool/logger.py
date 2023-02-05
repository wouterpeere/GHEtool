import logging
from pathlib import Path, PurePath

log_format = logging.Formatter("%(asctime)s %(message)s")
ghe_logger = logging.getLogger()
ghe_logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(PurePath(Path.home(), 'Documents/GHEtool').joinpath('GHEtool.log'), mode='w')
file_handler.setFormatter(log_format)
ghe_logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
ghe_logger.addHandler(console_handler)
