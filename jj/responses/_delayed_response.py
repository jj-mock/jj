import asyncio
import io
from http.cookies import Morsel
from json import dumps
from typing import Any, Dict, List, Optional, Tuple, Union
from unittest.mock import sentinel as nil

from aiohttp import web
from aiohttp.abc import AbstractStreamWriter
from aiohttp.typedefs import LooseHeaders
from aiohttp.web import ContentCoding
from aiohttp.web_request import BaseRequest
from multidict import CIMultiDict
from packed import packable

from ..http.headers import CONTENT_DISPOSITION, CONTENT_TYPE
from ._stream_response import StreamResponse
from ._utils import cookie_to_dict, get_response_body

__all__ = ("DelayedResponse",)


@packable("jj.responses.DelayedResponse")
class DelayedResponse(web.Response, StreamResponse):
    def __init__(self, *,
                 json: Any = nil,
                 body: Optional[Union[str, bytes]] = None,
                 text: Optional[str] = None,
                 status: int = 200,
                 reason: Optional[str] = None,
                 headers: Optional[LooseHeaders] = None,
                 delay: Optional[float] = None) -> None:
        headers = CIMultiDict(headers or {})

        if json is not nil:
            assert (body is None) and (text is None)
            body = dumps(json)
            if CONTENT_TYPE not in headers:
                headers[CONTENT_TYPE] = "application/json"

        if (body is None) and (text is None):
            body = ""

        if isinstance(body, io.IOBase):
            if CONTENT_DISPOSITION not in headers:
                headers[CONTENT_DISPOSITION] = "inline"

        super().__init__(body=body, text=text, status=status, reason=reason, headers=headers)
        self._delay = delay  # seconds

    @property
    def content_coding(self) -> Optional[ContentCoding]:
        return self._compression_force

    @property
    def delay(self) -> Union[float, None]:
        return self._delay

    def _cookie_to_dict(self, cookie: "Morsel[str]") -> Dict[str, Union[str, None]]:
        # backward compatibility
        return cookie_to_dict(cookie)

    def copy(self) -> "DelayedResponse":
        assert not self.prepared

        response = self.__class__(status=self.status, reason=self.reason, delay=self._delay,
                                  headers=self.headers, body=self.body)  # type: ignore
        for cookie in self.cookies.values():
            response.set_cookie(**cookie_to_dict(cookie))  # type: ignore
        if self.chunked:
            response.enable_chunked_encoding()
        if self._compression_force:
            response.enable_compression(self._compression_force)
        return response

    def get_body(self) -> bytes:
        # backward compatibility
        return get_response_body(self.body)

    async def _prepare_hook(self, request: BaseRequest) -> "DelayedResponse":
        if self._delay:
            await asyncio.sleep(self._delay)
        return self

    async def prepare(self, request: BaseRequest) -> Optional[AbstractStreamWriter]:
        await self._prepare_hook(request)
        return await super().prepare(request)

    def __packed__(self) -> Dict[str, Any]:
        assert not self.prepared

        headers = [[key, val] for key, val in self.headers.items()]
        cookies = [cookie_to_dict(cookie) for cookie in self.cookies.values()]

        body = get_response_body(self.body)

        compression: Optional[str] = None
        if isinstance(self._compression_force, ContentCoding):
            compression = self._compression_force.value
        else:
            compression = self._compression_force

        return {
            "status": self.status,
            "reason": self.reason,
            "headers": headers,
            "cookies": cookies,
            "body": body,
            "chunked": self.chunked,
            "compression": compression,
            "delay": self._delay,
        }

    @classmethod
    def __unpacked__(cls, *,
                     status: int,
                     reason: Optional[str],
                     headers: List[Tuple[str, str]],
                     cookies: List[Dict[str, Union[str, None]]],
                     body: Optional[bytes],
                     chunked: bool,
                     compression: Optional[ContentCoding],
                     delay: Optional[float],
                     **kwargs: Any) -> "DelayedResponse":
        response = cls(status=status, reason=reason,
                       headers=headers, body=body, delay=delay)  # type: ignore
        for cookie in cookies:
            response.set_cookie(**cookie)  # type: ignore
        if compression:
            response.enable_compression(ContentCoding(compression))
        if chunked:
            response.enable_chunked_encoding()
        return response
