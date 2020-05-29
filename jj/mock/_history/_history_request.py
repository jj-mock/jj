from typing import Any, Dict, List, Tuple

from multidict import CIMultiDict, CIMultiDictProxy, MultiDict, MultiDictProxy
from packed import packable

from ...requests import Request

__all__ = ("HistoryRequest",)


@packable("jj.mock.HistoryRequest")
class HistoryRequest:
    def __init__(self, *,
                 method: str,
                 path: str,
                 segments: Dict[str, str],
                 params: "MultiDictProxy[str]",
                 headers: "CIMultiDictProxy[str]",
                 body: bytes) -> None:
        self._method = method
        self._path = path
        self._segments = segments
        self._params = params
        self._headers = headers
        self._body = body

    @property
    def method(self) -> str:
        return self._method

    @property
    def path(self) -> str:
        return self._path

    @property
    def segments(self) -> Dict[str, str]:
        return self._segments

    @property
    def params(self) -> "MultiDictProxy[str]":
        return self._params

    @property
    def headers(self) -> "CIMultiDictProxy[str]":
        return self._headers

    @property
    def body(self) -> bytes:
        return self._body

    @staticmethod
    async def from_request(request: Request) -> "HistoryRequest":
        body = await request.read()
        return HistoryRequest(
            method=request.method,
            path=request.path,
            segments=request.segments,
            params=request.params,
            headers=request.headers,
            body=body,
        )

    def __packed__(self) -> Dict[str, Any]:
        params = [[key, val] for key, val in self._params.items()]
        headers = [[key, val] for key, val in self._headers.items()]
        return {
            "method": self._method,
            "path": self._path,
            "segments": self._segments,
            "params": params,
            "headers": headers,
            "body": self.body,
        }

    @classmethod
    def __unpacked__(cls, *,
                     method: str,
                     path: str,
                     segments: Dict[str, str],
                     params: List[Tuple[str, str]],
                     headers: List[Tuple[str, str]],
                     body: bytes,
                     **kwargs: Any) -> "HistoryRequest":
        real_params = MultiDictProxy(MultiDict(params))
        real_headers = CIMultiDictProxy(CIMultiDict(headers))
        return HistoryRequest(
            method=method,
            path=path,
            segments=segments,
            params=real_params,
            headers=real_headers,
            body=body,
        )

    def __repr__(self) -> str:
        return (f"HistoryRequest("
                f"method={self._method!r}, "
                f"path={self._path!r}, "
                f"params={self._params!r}, "
                f"headers={self._headers!r}, "
                f"body={self._body!r}"
                f")")
