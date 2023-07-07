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


def addLoggingLevel(levelName, levelNum, methodName=None):  # pragma: no cover
    # copied from: https://stackoverflow.com/questions/2183233/
    # how-to-add-a-custom-loglevel-to-pythons-logging-facility/35804945#35804945
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
       raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
       raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
       raise AttributeError('{} already defined in logger class'.format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)

addLoggingLevel('MAIN_INFO', logging.INFO - 5)
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
ghe_logger.addHandler(console_handler)
