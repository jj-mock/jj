from urllib.parse import urljoin

from aiohttp import ClientSession
from aiohttp.client_reqrep import ClientResponse
from multidict import MultiDict, CIMultiDict

from ..requests import Request
from ._response import Response


__all__ = ("TunnelResponse",)


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


class TunnelResponse(Response):
    def __init__(self, *, target: str) -> None:
        super().__init__()
        self._target = target

    @property
    def target(self) -> str:
        return self._target

    async def forward(self, request: Request) -> ClientResponse:
        url = urljoin(self._target, request.path)

        headers: MultiDict = MultiDict()
        for key, value in request.headers.items():
            if key.lower() not in _FILTERED_HEADERS:
                headers[key] = value

        params = request.query
        data = await request.read()
        async with ClientSession(auto_decompress=False) as session:
            async with session.request(request.method, url,
                                       params=params, headers=headers, data=data) as response:
                response.body = await response.read()  # type: ignore
                return response

    async def _start(self, request):
        response = await self.forward(request)

        self.set_status(response.status, response.reason)
        self._headers = CIMultiDict(response.headers)
        self.body = response.body

        return await super()._start(request)
