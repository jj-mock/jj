import logging
import os
from logging import LogRecord
from string import Template

from ...requests import Request
from ...responses import Response
from ._simple_formatter import SimpleFormatter

__all__ = ("ExtSimpleFormatter",)

INFO = logging.INFO
DEBUG = logging.DEBUG

log_level = int(os.getenv('MOCK_LOG_LEVEL', INFO))
body_output_limit = int(os.getenv('MOCK_BODY_OUTPUT_LIMIT', 10 ** 6))
format = os.getenv('MOCK_FORMAT',
                   '$req_method $req_query $res_code $res_reason $res_body')
# full_format '$req_method $req_query $req_headers $res_code $res_reason $res_headers $res_body'
formatter_template = Template(format)


class ExtSimpleFormatter(SimpleFormatter):
    def format_request(self, request: Request, record: LogRecord) -> str:
        return ""

    def format_response(
        self, response: Response, request: Request, record: LogRecord, log_level: int = log_level,
        format: str = format) -> str:
        formatter = formatter_template.substitute(
            req_method=f"-> {request.method}",
            req_query=f" {request.url.path_qs}",
            req_headers=f"\n-> {dict(request.headers)}",
            res_code=f"\n<- {response.status}",
            res_reason=f"\n<- {response.reason}",
            res_headers=f"\n<- {dict(response.headers)}",
            res_body=f"\n<- {response.body[:body_output_limit]}" if isinstance(response.body, bytes) and len(
                response.body) > 0 else ""
        )

        return formatter
