import logging
from logging import LogRecord

from ..requests import Request
from ..responses import Response

__all__ = ("Filter",)


class Filter(logging.Filter):
    def filter_request(self, request: Request, record: LogRecord) -> bool:
        return super().filter(record)

    def filter_response(self, response: Response, request: Request, record: LogRecord) -> bool:
        return super().filter(record)

    def filter(self, record: LogRecord) -> bool:
        request = getattr(record, "jj_request", None)
        response = getattr(record, "jj_response", None)
        if (response is not None) and (request is not None):
            return self.filter_response(response, request, record)
        elif request is not None:
            return self.filter_request(request, record)
        else:
            return super().filter(record)
