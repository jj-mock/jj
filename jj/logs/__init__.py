import logging
import os

from ._filter import Filter
from ._logger import Logger
from ._request_filter import RequestFilter
from ._system_log_filter import SystemLogFilter
from .formatters import ExtSimpleFormatter, Formatter, SimpleFormatter

INFO = logging.INFO
DEBUG = logging.DEBUG

__all__ = ("Logger", "Filter", "Formatter", "SimpleFormatter", "SystemLogFilter", "RequestFilter",)

log_level_str = os.getenv('JJ_LOG_LEVEL', 'INFO')
log_level = getattr(logging, log_level_str, logging.INFO)
log_format = os.getenv('JJ_LOG_FORMAT', '$req_method $req_query $res_code $res_reason $res_body')
# full_format '$req_method $req_query $req_headers $res_code $res_reason $res_headers $res_body'

# Set custom Logger class

_old_logger_class = logging.getLoggerClass()
logging.setLoggerClass(Logger)

# Register Loggers

logger: Logger = logging.getLogger("jj.access_logger")  # type: ignore
logger.setLevel(log_level)
logger.propagate = False

# Register Filter

filter_ = Filter()
request_filter_ = RequestFilter()
logger.addFilter(filter_)
logger.addFilter(request_filter_)
if log_level != DEBUG:
    logger.addFilter(SystemLogFilter())

# Register Handler

handler = logging.StreamHandler()
logger.addHandler(handler)

# Register Formatter

formatter = ExtSimpleFormatter(log_format)
handler.setFormatter(formatter)

# Restore default Logger class

logging.setLoggerClass(_old_logger_class)
