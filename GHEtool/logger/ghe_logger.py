"""
Script to create the GHEtool logger for the console and the text file
"""
import logging
from pathlib import Path, PurePath


class CustomFormatter(logging.Formatter):
    """
    Class to create a special console coloring of the messages
    """
    # define colors
    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    white = '\x1b[37;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt: str):
        """

        Parameters
        ----------
        fmt : str
            Format of the log message
        """
        super().__init__(fmt=fmt)
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.white + self.fmt + self.reset,
            logging.INFO: self.white + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats the record.

        Parameters
        ----------
        record: logging.LogRecord
            record to be formatted

        Returns
        -------
        str
            Formatted log message
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


# create a custom formatter for the logger using time - name - level - message and filename - line number as format
log_format = CustomFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)")
# create GHEtool logger and set level to info
ghe_logger = logging.getLogger()
ghe_logger.setLevel(logging.INFO)
# get the log path file as documents/GHEtool folder
log_file_path = Path(PurePath(Path.home(), 'Documents/GHEtool'))
log_file_path.mkdir(parents=True, exist_ok=True)
# add a text logger
file_handler = logging.FileHandler(log_file_path.joinpath('GHEtool.log'), mode='w')
file_handler.setFormatter(log_format)
ghe_logger.addHandler(file_handler)
# add a console logger for info
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
# add a console logger for warnings (default)
console_handler_warning = logging.StreamHandler()
console_handler_warning.setLevel(logging.WARNING)
console_handler_warning.setFormatter(log_format)
ghe_logger.addHandler(console_handler_warning)
