import logging
import os

from ._filter import Filter
from ._logger import Logger
from ._request_filter import RequestFilter
from ._system_log_filter import SystemLogFilter
from .formatters import Formatter, SimpleFormatter, TemplateFormatter

__all__ = ("Logger", "Filter", "Formatter", "SimpleFormatter", "TemplateFormatter",
           "SystemLogFilter", "RequestFilter",)

# Set custom Logger class

_old_logger_class = logging.getLoggerClass()
logging.setLoggerClass(Logger)

# Register Loggers

logger: Logger = logging.getLogger("jj.access_logger")  # type: ignore
log_level = getattr(logging, os.getenv("JJ_LOG_LEVEL", "INFO"))
logger.setLevel(log_level)
logger.propagate = False

# Register Filter

filter_ = Filter()
request_filter_ = RequestFilter()
logger.addFilter(filter_)
logger.addFilter(request_filter_)
if log_level != logging.DEBUG:
    logger.addFilter(SystemLogFilter())

# Register Handler

handler = logging.StreamHandler()
logger.addHandler(handler)

# Register Formatter

formatter = TemplateFormatter()
handler.setFormatter(formatter)

# Restore default Logger class

logging.setLoggerClass(_old_logger_class)
