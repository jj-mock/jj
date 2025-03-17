from typing import Any, Dict, List, Tuple

from multidict import CIMultiDict, CIMultiDictProxy
from packed import packable

from ...responses import Response, StreamResponse

__all__ = ("HistoryResponse",)


@packable("jj.mock.HistoryResponse")
class HistoryResponse:
    def __init__(self, *,
                 status: int,
                 reason: str,
                 headers: "CIMultiDictProxy[str]",
                 body: Any,
                 raw: bytes) -> None:
        self._status = status
        self._reason = reason
        self._headers = headers
        self._body = body
        self._raw = raw

    @property
    def status(self) -> int:
        return self._status

    @property
    def reason(self) -> str:
        return self._reason

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
    async def from_response(cls, response: StreamResponse) -> "HistoryResponse":
        if isinstance(response, Response):
            raw = response.get_body()
        else:
            raw = b"<stream response>"
        return cls(
            status=response.status,
            reason=response.reason,
            headers=CIMultiDictProxy(response.headers),
            body=raw,
            raw=raw,
        )

    def to_dict(self) -> Dict[str, Any]:
        headers = [[key, val] for key, val in self._headers.items()]
        return {
            "status": self._status,
            "reason": self._reason,
            "headers": headers,
            "body": self._body,
            "raw": self._raw,
        }

    def __packed__(self) -> Dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, request: Dict[str, Any]) -> "HistoryResponse":
        real_headers: CIMultiDictProxy[str] = CIMultiDictProxy(CIMultiDict(request["headers"]))
        raw = request.get("raw", request["body"])  # backward compatibility
        return cls(
            status=request["status"],
            reason=request["reason"],
            headers=real_headers,
            body=request["body"],
            raw=raw,
        )

    @classmethod
    def __unpacked__(cls, *,
                     status: int,
                     reason: str,
                     headers: List[Tuple[str, str]],
                     body: Any,
                     **kwargs: Any) -> "HistoryResponse":
        return cls.from_dict({
            "status": status,
            "reason": reason,
            "headers": headers,
            "body": body,
            **kwargs,
        })

    def __repr__(self) -> str:
        return (f"HistoryResponse("
                f"status={self._status!r}, "
                f"reason={self._reason!r}, "
                f"headers={self._headers!r}, "
                f"body={self._body!r}"
                f")")
