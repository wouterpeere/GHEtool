import logging
from pathlib import Path, PurePath


class CustomFormatter(logging.Formatter):

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    white = '\x1b[37;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.white + self.fmt + self.reset,
            logging.INFO: self.white + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


log_format = CustomFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)")
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
