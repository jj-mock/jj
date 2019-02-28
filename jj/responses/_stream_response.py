from typing import Optional, MutableMapping

from aiohttp import web

from .._version import server_version


__all__ = ("StreamResponse",)


class StreamResponse(web.StreamResponse):
    def __init__(self, *,
                 status: int = 200,
                 reason: Optional[str] = None,
                 headers: Optional[MutableMapping[str, str]] = None) -> None:
        headers = headers or {}
        super().__init__(status=status, reason=reason, headers={
            **headers,
            "Server": headers.get("Server", server_version)
        })
