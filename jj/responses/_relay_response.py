from typing import Any, Dict, Tuple
from urllib.parse import urljoin

from aiohttp import ClientSession
from aiohttp.typedefs import LooseHeaders
from aiohttp.web_request import BaseRequest
from multidict import CIMultiDict, CIMultiDictProxy
from packed import packable

from ._response import Response

__all__ = ("RelayResponse",)


# http://tools.ietf.org/html/rfc2616#section-13.5.1
_HOP_BY_HOP_HEADERS = (
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade")

_FILTERED_HEADERS = _HOP_BY_HOP_HEADERS + ("host", "content-length")

_TargetResponseType = Tuple[int, Any, CIMultiDictProxy[str], bytes]


@packable("jj.responses.RelayResponse")
class RelayResponse(Response):
    def __init__(self, *, target: str) -> None:
        super().__init__()
        self._target = target
        self._prepare_hook_called = False

    @property
    def target(self) -> str:
        return self._target

    def _filter_headers(self, headers: LooseHeaders) -> CIMultiDict[str]:
        filtered: CIMultiDict[str] = CIMultiDict()
        for key, value in headers.items():
            if key.lower() not in _FILTERED_HEADERS:
                filtered[key] = value
        return filtered

    async def _do_target_request(self, request: BaseRequest) -> _TargetResponseType:
        url = urljoin(self._target, request.path)
        headers = self._filter_headers(request.headers)

        data = await request.read()

        async with ClientSession(auto_decompress=False) as session:
            async with session.request(request.method, url, params=request.query, headers=headers,
                                       data=data, allow_redirects=True) as response:
                body = await response.read()
        return response.status, response.reason, response.headers, body

    async def _prepare_hook(self, request: BaseRequest) -> "RelayResponse":
        if self._prepare_hook_called:
            return self
        status, reason, headers, body = await self._do_target_request(request)
        self.set_status(status, reason)
        self._headers = CIMultiDict(self._filter_headers(headers))
        self.body = body
        self._prepare_hook_called = True
        return self

    def copy(self) -> "RelayResponse":
        assert not self.prepared
        return self.__class__(target=self._target)

    def __packed__(self) -> Dict[str, Any]:
        return {"target": self._target}

    @classmethod
    def __unpacked__(cls, *, target: str, **kwargs: Any) -> "RelayResponse":  # type: ignore
        return cls(target=target)
