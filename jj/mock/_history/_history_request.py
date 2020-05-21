from typing import Any, Dict, List, Tuple

from packed import packable

from ...requests import Request

__all__ = ("HistoryRequest",)


@packable("HistoryRequest")
class HistoryRequest:
    def __init__(self, method: str, path: str,
                 params: List[Tuple[str, str]],
                 headers: List[Tuple[str, str]]) -> None:
        self._method = method
        self._path = path
        self._params = params
        self._headers = headers

    @staticmethod
    def from_request(request: Request) -> "HistoryRequest":
        params = [[key, val] for key, val in request.params.items()]
        headers = [[key, val] for key, val in request.headers.items()]
        return HistoryRequest(request.method, request.path, params, headers)  # type: ignore

    def __packed__(self) -> Dict[str, Any]:
        return {
            "method": self._method,
            "path": self._path,
            "params": self._params,
            "headers": self._headers,
        }

    @classmethod
    def __unpacked__(cls, *, method: str, path: str,
                     params: List[Tuple[str, str]],
                     headers: List[Tuple[str, str]],
                     **kwargs: Any) -> "HistoryRequest":
        return HistoryRequest(method=method, path=path, params=params, headers=headers)

    def __repr__(self) -> str:
        return (f"HistoryRequest("
                f"method={self._method!r}, "
                f"path={self._path!r}, "
                f"params={self._params!r}, "
                f"headers={self._headers!r}"
                f")")
