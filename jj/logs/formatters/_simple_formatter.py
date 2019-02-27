from logging import LogRecord

from ._formatter import Formatter, Request, Response


__all__ = ("SimpleFormatter",)


class SimpleFormatter(Formatter):
    def format_request(self, request: Request, record: LogRecord) -> str:
        return "-> {}".format(request.url.path)

    def format_response(self, response: Response, request: Request, record: LogRecord) -> str:
        return "<- {} {}\n".format(response.status, response.reason)
