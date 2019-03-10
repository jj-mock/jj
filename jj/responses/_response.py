import io
from typing import Any, Optional, Union, MutableMapping
from json import dumps
from unittest.mock import sentinel as nil

from aiohttp import web

from ._stream_response import StreamResponse


__all__ = ("Response",)


class Response(web.Response, StreamResponse):
    def __init__(self, *,
                 json: Any = nil,
                 body: Optional[Union[str, bytes]] = None,
                 text: Optional[str] = None,
                 status: int = 200,
                 reason: Optional[str] = None,
                 headers: Optional[MutableMapping[str, str]] = None) -> None:
        headers = headers or {}

        if json is not nil:
            assert (body is None) and (text is None)
            body = dumps(json)
            headers.update({"Content-Type": "application/json"})

        if (body is None) and (text is None):
            body = ""

        if isinstance(body, io.IOBase):
            headers.update({"Content-Disposition": "inline"})

        super().__init__(body=body, text=text, status=status, reason=reason, headers=headers)
