from typing import Optional
from urllib.parse import urljoin

from aiohttp import ClientSession
from aiohttp.abc import AbstractStreamWriter
from aiohttp.web_request import BaseRequest
from multidict import CIMultiDict, MultiDict

from ._stream_response import StreamResponse

__all__ = ("RelayResponse",)


# http://tools.ietf.org/html/rfc2616#section-13.5.1
_HOP_BY_HOP_HEADERS = (
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding"
    "upgrade")

_FILTERED_HEADERS = _HOP_BY_HOP_HEADERS + ("host", "content-length")


class RelayResponse(StreamResponse):
    def __init__(self, *, target: str) -> None:
        super().__init__()
        self._target = target

    @property
    def target(self) -> str:
        return self._target

    async def prepare(self, request: BaseRequest) -> Optional[AbstractStreamWriter]:
        url = urljoin(self.target, request.path)

        headers: MultiDict[str] = MultiDict()
        for key, value in request.headers.items():
            if key.lower() not in _FILTERED_HEADERS:
                headers[key] = value

        async with ClientSession(auto_decompress=False) as session:
            async with session.request(request.method, url,
                                       params=request.query,
                                       headers=headers,
                                       data=request.content,
                                       allow_redirects=True) as response:
                self.set_status(response.status, response.reason)
                self._headers = CIMultiDict(response.headers)

                await super().prepare(request)

                async for data in response.content.iter_any():
                    await self.write(data)

                await self.write_eof()

        return await super().prepare(request)
