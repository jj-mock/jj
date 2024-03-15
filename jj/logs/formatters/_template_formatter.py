import codecs
from logging import LogRecord
from os import getenv
from string import Template

from multidict import MultiMapping

from ...requests import Request
from ...responses import Response
from ._formatter import Formatter

__all__ = ("TemplateFormatter",)

LOG_FORMAT = getenv("JJ_LOG_FORMAT", "-> $req_method $req_path\n<- $res_code $res_reason\n")
LOG_BODY_LIMIT = int(getenv("JJ_LOG_BODY_LIMIT", 10 ** 6))


class TemplateFormatter(Formatter):
    def __init__(self, log_format: str = LOG_FORMAT, log_body_limit: int = LOG_BODY_LIMIT) -> None:
        super().__init__()
        self._log_format = codecs.decode(log_format.encode(), 'unicode_escape')
        self._log_body_limit = log_body_limit
        self._template = Template(self._log_format)

    def format_response(self, response: Response, request: Request, record: LogRecord) -> str:
        try:
            return self._substitute(response, request)
        except KeyError as e:
            return f"Incorrect log format: ${e} does not exist"
        except Exception as e:
            return f"Error while formatting log: {repr(e)}"

    def _substitute(self, response: Response, request: Request) -> str:
        response_body = response.get_body()
        return self._template.substitute(
            # request
            req_method=request.method,
            req_path=request.url.path,
            req_query=request.url.query_string,
            req_headers=self._format_headers(request.headers),
            # response
            res_code=response.status,
            res_reason=response.reason,
            res_headers=self._format_headers(response.headers),
            res_body=response_body[:self._log_body_limit],
        )

    def _format_headers(self, headers: MultiMapping[str]) -> str:
        result = []
        for key, val in headers.items():
            result.append(f" {key}: {val}")
        return "\n".join(result)
