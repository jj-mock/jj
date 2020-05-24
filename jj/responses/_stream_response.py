from typing import Optional

from aiohttp import web
from aiohttp.typedefs import LooseHeaders
from multidict import CIMultiDict

from .._version import server_version

__all__ = ("StreamResponse",)


class StreamResponse(web.StreamResponse):
    def __init__(self, *,
                 status: int = 200,
                 reason: Optional[str] = None,
                 headers: Optional[LooseHeaders] = None) -> None:
        headers = CIMultiDict(headers or {})
        headers["Server"] = headers.get("Server", server_version)
        super().__init__(status=status, reason=reason, headers=headers)
