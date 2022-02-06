from typing import Any, Dict, List, Tuple

from aiohttp.web_exceptions import HTTPRequestEntityTooLarge
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
                 body: Any,
                 raw: bytes) -> None:
        self._method = method
        self._path = path
        self._segments = segments
        self._params = params
        self._headers = headers
        self._body = body
        self._raw = raw

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
    def body(self) -> Any:
        return self._body

    @property
    def raw(self) -> bytes:
        return self._raw

    @classmethod
    async def from_request(cls, request: Request) -> "HistoryRequest":
        try:
            raw = await request.read()
        except HTTPRequestEntityTooLarge:
            raw = b"<binary>"
            await request.release()
        return cls(
            method=request.method,
            path=request.path,
            segments=request.segments,
            params=request.params,
            headers=request.headers,
            body=raw,
            raw=raw,
        )

    def to_dict(self) -> Dict[str, Any]:
        params = [[key, val] for key, val in self._params.items()]
        headers = [[key, val] for key, val in self._headers.items()]
        return {
            "method": self._method,
            "path": self._path,
            "segments": self._segments,
            "params": params,
            "headers": headers,
            "body": self._body,
            "raw": self._raw,
        }

    def __packed__(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, request: Dict[str, Any]) -> "HistoryRequest":
        real_params = MultiDictProxy(MultiDict(request["params"]))
        real_headers = CIMultiDictProxy(CIMultiDict(request["headers"]))
        raw = request.get("raw", request["body"])  # backward compatibility
        return cls(
            method=request["method"],
            path=request["path"],
            segments=request["segments"],
            params=real_params,
            headers=real_headers,
            body=request["body"],
            raw=raw,
        )

    @classmethod
    def __unpacked__(cls, *,
                     method: str,
                     path: str,
                     segments: Dict[str, str],
                     params: List[Tuple[str, str]],
                     headers: List[Tuple[str, str]],
                     body: Any,
                     **kwargs: Any) -> "HistoryRequest":
        return cls.from_dict({
            "method": method,
            "path": path,
            "segments": segments,
            "params": params,
            "headers": headers,
            "body": body,
            **kwargs,
        })

    def __repr__(self) -> str:
        return (f"HistoryRequest("
                f"method={self._method!r}, "
                f"path={self._path!r}, "
                f"params={self._params!r}, "
                f"headers={self._headers!r}, "
                f"body={self._body!r}"
                f")")
