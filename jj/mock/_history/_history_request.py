from typing import Any, Dict, List, Tuple

from packed import packable

from ...requests import Request

__all__ = ("HistoryRequest",)


@packable("jj.mock.HistoryRequest")
class HistoryRequest:
    def __init__(self, *,
                 method: str,
                 path: str,
                 segments: Dict[str, str],
                 params: List[Tuple[str, Any]],
                 headers: List[Tuple[str, Any]],
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
    def params(self) -> List[Tuple[str, Any]]:
        return self._params

    @property
    def headers(self) -> List[Tuple[str, Any]]:
        return self._headers

    @property
    def body(self) -> bytes:
        return self._body

    @staticmethod
    async def from_request(request: Request) -> "HistoryRequest":
        params = [[key, val] for key, val in request.params.items()]
        headers = [[key, val] for key, val in request.headers.items()]

        body = await request.read()

        return HistoryRequest(
            method=request.method,
            path=request.path,
            segments=request.segments,
            params=params,  # type: ignore
            headers=headers,  # type: ignore
            body=body,
        )

    def __packed__(self) -> Dict[str, Any]:
        return {
            "method": self._method,
            "path": self._path,
            "segments": self._segments,
            "params": self._params,
            "headers": self._headers,
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
        return HistoryRequest(
            method=method,
            path=path,
            segments=segments,
            params=params,
            headers=headers,
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
