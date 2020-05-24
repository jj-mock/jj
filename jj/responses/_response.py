import io
from http.cookies import Morsel
from json import dumps
from typing import Any, Dict, List, Optional, Tuple, Union
from unittest.mock import sentinel as nil

from aiohttp import web
from aiohttp.payload import BytesPayload, IOBasePayload, TextIOPayload
from aiohttp.typedefs import LooseHeaders
from aiohttp.web import ContentCoding
from multidict import CIMultiDict
from packed import packable

from ..http.headers import CONTENT_DISPOSITION, CONTENT_TYPE
from ._stream_response import StreamResponse

__all__ = ("Response",)


@packable("jj.responses.Response")
class Response(web.Response, StreamResponse):
    def __init__(self, *,
                 json: Any = nil,
                 body: Optional[Union[str, bytes]] = None,
                 text: Optional[str] = None,
                 status: int = 200,
                 reason: Optional[str] = None,
                 headers: Optional[LooseHeaders] = None) -> None:
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

    @property
    def content_coding(self) -> Optional[ContentCoding]:
        return self._compression_force

    def _cookie_to_dict(self, cookie: "Morsel[str]") -> Dict[str, Union[str, None]]:
        dictionary: Dict[str, Union[str, None]] = {
            "name": cookie.key,
            "value": cookie.value,
        }
        for attr in ("expires", "domain", "max-age", "path", "secure", "httponly", "version"):
            key = attr.replace("-", "_")
            val = cookie.get(attr)
            dictionary[key] = None if val == "" else val
        return dictionary

    def copy(self) -> "Response":
        assert not self.prepared

        response = self.__class__(status=self.status, reason=self.reason,
                                  headers=self.headers, body=self.body)  # type: ignore
        for cookie in self.cookies.values():
            response.set_cookie(**self._cookie_to_dict(cookie))  # type: ignore
        if self.chunked:
            response.enable_chunked_encoding()
        if self._compression_force:
            response.enable_compression(self._compression_force)
        return response

    def get_body(self) -> bytes:
        if isinstance(self.body, (bytes, bytearray, memoryview)):
            return bytes(self.body)
        elif isinstance(self.body, BytesPayload):
            return bytes(self.body._value)
        elif isinstance(self.body, TextIOPayload):
            return bytes(self.body._value.read(), self.body.encoding)  # type: ignore
        elif isinstance(self.body, IOBasePayload):
            return bytes(self.body._value.read())
        else:
            raise ValueError("Unsupported body type {}".format(type(self.body)))

    def __packed__(self) -> Dict[str, Any]:
        assert not self.prepared

        headers = [[key, val] for key, val in self.headers.items()]
        cookies = [self._cookie_to_dict(cookie) for cookie in self.cookies.values()]

        body = self.get_body()
        compression = self._compression_force
        if isinstance(compression, ContentCoding):
            compression = compression.value

        return {
            "status": self.status,
            "reason": self.reason,
            "headers": headers,
            "cookies": cookies,
            "body": body,
            "chunked": self.chunked,
            "compression": compression,
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
                     **kwargs: Any) -> "Response":
        response = cls(status=status, reason=reason, headers=headers, body=body)  # type: ignore
        for cookie in cookies:
            response.set_cookie(**cookie)  # type: ignore
        if compression:
            response.enable_compression(compression)
        if chunked:
            response.enable_chunked_encoding()
        return response
