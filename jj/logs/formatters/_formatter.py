import logging
from logging import LogRecord

from ...responses import Response
from ...requests import Request


__all__ = ("Formatter",)


class Formatter(logging.Formatter):
    def format_request(self, request: Request, record: LogRecord) -> str:
        return super().format(record)

    def format_response(self, response: Response, request: Request, record: LogRecord) -> str:
        return super().format(record)

    def format(self, record: LogRecord) -> str:
        request = getattr(record, "jj_request", None)
        response = getattr(record, "jj_response", None)
        if response is not None:
            return self.format_response(response, request, record)
        elif request is not None:
            return self.format_request(request, record)
        else:
            return super().format(record)
