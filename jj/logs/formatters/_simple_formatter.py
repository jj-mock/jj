from logging import LogRecord
from os import linesep

from ...requests import Request
from ...responses import Response
from ._formatter import Formatter

__all__ = ("SimpleFormatter",)


class SimpleFormatter(Formatter):
    def format_request(self, request: Request, record: LogRecord) -> str:
        return "-> {} {}".format(request.method, request.url.path)

    def format_response(self, response: Response, request: Request, record: LogRecord) -> str:
        res = linesep.join([
            "-> {} {}".format(request.method, request.url.path),
            "<- {} {}".format(response.status, response.reason),
            "",
        ])
        return res
