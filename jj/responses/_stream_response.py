from typing import Optional

from aiohttp import web
from aiohttp.typedefs import LooseHeaders
from multidict import CIMultiDict

from .._version import server_version

__all__ = ("StreamResponse",)


class StreamResponse(web.StreamResponse):
    """
    Represents an HTTP response that supports streaming.

    The `StreamResponse` class extends `aiohttp.web.StreamResponse` and adds a default
    `Server` header with the server version.

    :param status: The HTTP status code for the response (default is 200).
    :param reason: The reason phrase for the status code (optional).
    :param headers: Optional headers for the response, passed as a dictionary.
                    If no `Server` header is provided, it defaults to the server version.
    """

    def __init__(self, *,
                 status: int = 200,
                 reason: Optional[str] = None,
                 headers: Optional[LooseHeaders] = None) -> None:
        """
        Initialize the StreamResponse object with the specified status, reason, and headers.

        :param status: The HTTP status code for the response (default is 200).
        :param reason: The reason phrase for the status code (optional).
        :param headers: A dictionary of headers for the response (optional). If no `Server`
                        header is provided, it defaults to the current server version.
        """
        headers = CIMultiDict(headers or {})
        headers["Server"] = headers.get("Server", server_version)
        super().__init__(status=status, reason=reason, headers=headers)
