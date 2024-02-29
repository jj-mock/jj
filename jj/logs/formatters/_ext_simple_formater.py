import os
from logging import LogRecord
from string import Template

from ...requests import Request
from ...responses import Response
from ._simple_formatter import SimpleFormatter

__all__ = ("ExtSimpleFormatter",)

body_output_limit = int(os.getenv('JJ_LOG_BODY_OUTPUT_LIMIT', 10 ** 6))


class ExtSimpleFormatter(SimpleFormatter):
    def __init__(self, log_format: str) -> None:
        super().__init__()
        self.log_format = log_format

    def format_request(self, request: Request, record: LogRecord) -> str:
        return ""

    def format_response(self, response: Response, request: Request,
                        record: LogRecord) -> str:
        formatter_template = Template(self.log_format)
        formatter = formatter_template.substitute(
            req_method=f"-> {request.method}",
            req_query=f" {request.url.path_qs}",
            req_headers=f"\n-> {dict(request.headers)}",
            res_code=f"\n<- {response.status}",
            res_reason=f"\n<- {response.reason}",
            res_headers=f"\n<- {dict(response.headers)}",
            res_body=f"\n<- {response.body[:body_output_limit].decode('utf-8')}" if isinstance(
                response.body, bytes) and len(response.body) > 0 else ""
        )

        return formatter
