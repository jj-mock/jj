import logging

from ._logger import Logger
from ._filter import Filter
from .formatters import Formatter, SimpleFormatter


__all__ = ("Logger", "Filter", "Formatter", "SimpleFormatter")


# Set custom Logger class

_old_logger_class = logging.getLoggerClass()
logging.setLoggerClass(Logger)

# Register Loggers

logger: Logger = logging.getLogger("jj.access_logger")  # type: ignore
logger.setLevel(logging.INFO)
logger.propagate = False

# Register Filter

filter_ = Filter()
logger.addFilter(filter_)

# Register Handler

handler = logging.StreamHandler()
logger.addHandler(handler)

# Register Formatter

formatter = SimpleFormatter()
handler.setFormatter(formatter)

# Restore default Logger class

logging.setLoggerClass(_old_logger_class)
