from logging import LogRecord

from jj.logs import Filter
from jj.requests import Request
from jj.responses import Response

__all__ = ("SystemLogFilter",)


class SystemLogFilter(Filter):
    def filter_request(self, request: Request, record: LogRecord) -> bool:
        return "x-jj-remote-mock" not in request.headers

    def filter_response(self, response: Response, request: Request, record: LogRecord) -> bool:
        return self.filter_request(request, record)
