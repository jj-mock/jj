import logging
from logging import LogRecord

__all__ = ("RequestFilter",)


class RequestFilter(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        request = getattr(record, "jj_request", None)
        response = getattr(record, "jj_response", None)
        if (request is not None) and (response is None):
            return False
        return super().filter(record) is not False
