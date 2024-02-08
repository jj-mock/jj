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

body_output_limit = int(os.getenv('MOCK_BODY_OUTPUT_LIMIT', 10 ** 6))
log_level = os.getenv('MOCK_LOG_LEVEL', INFO)
format = os.getenv('MOCK_FORMAT',
                   '$req_method $req_url $req_path $req_query $req_headers '
                   '$res_code $res_reason $res_headers $res_body')
formatter_template = Template(format)


class ExtSimpleFormatter(SimpleFormatter):
    def format_response(
        self, response: Response, request: Request, record: LogRecord,
        log_level: int = INFO,
        format: str = '$req_method $req_url $req_path $req_query $req_headers '
                      '$res_code $res_reason $res_headers $res_body') -> str:
        formatter = formatter_template.substitute(
            req_method=request.method,
            req_url=request.url,
            req_path=request.url.path,
            req_query=request.url.path_qs,
            req_headers=request.headers,
            res_code=response.status,
            res_reason=response.reason,
            res_headers=response.headers,
            res_body=response.body[:body_output_limit] if isinstance(response.body, bytes) and len(
                response.body) > 0 else response.body
        )
        return formatter.replace(' ', '\n')
