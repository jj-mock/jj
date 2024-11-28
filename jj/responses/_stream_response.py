from typing import Any, Optional, cast

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
                 headers: Optional[LooseHeaders] = None,
                 **kwargs: Any) -> None:
        """
        Initialize the StreamResponse object with the specified status, reason, and headers.

        :param status: The HTTP status code for the response (default is 200).
        :param reason: The reason phrase for the status code (optional).
        :param headers: A dictionary of headers for the response (optional). If no `Server`
                        header is provided, it defaults to the current server version.
        """

        # _real_headers is an internal parameter used to pass a pre-populated
        # headers object. It is used by the `Response` class to avoid copying
        # the headers when creating a new response object. It is not intended
        # to be used by external code.
        _real_headers = kwargs.pop("_real_headers", None)

        if _real_headers is not None:
            headers = cast(CIMultiDict[str], _real_headers)
        else:
            headers = CIMultiDict(headers or {})
        headers["Server"] = headers.get("Server", server_version)

        super().__init__(status=status, reason=reason, headers=headers, **kwargs)
