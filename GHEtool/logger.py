import logging
from pathlib import Path, PurePath

log_format = logging.Formatter("%(asctime)s %(message)s")
ghe_logger = logging.getLogger()
ghe_logger.setLevel(logging.INFO)

log_file_path = Path(PurePath(Path.home(), 'Documents/GHEtool'))
log_file_path.mkdir(parents=True, exist_ok=True)
file_handler = logging.FileHandler(log_file_path.joinpath('GHEtool.log'), mode='w')
file_handler.setFormatter(log_format)
ghe_logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
ghe_logger.addHandler(console_handler)
