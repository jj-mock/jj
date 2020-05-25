from typing import Any, Dict, List, Tuple

from multidict import CIMultiDict, CIMultiDictProxy
from packed import packable

from ...responses import Response

__all__ = ("HistoryResponse",)


@packable("jj.mock.HistoryResponse")
class HistoryResponse:
    def __init__(self, *,
                 status: int,
                 reason: str,
                 headers: "CIMultiDictProxy[str]",
                 body: bytes) -> None:
        self._status = status
        self._reason = reason
        self._headers = headers
        self._body = body

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
    def body(self) -> bytes:
        return self._body

    @staticmethod
    async def from_response(response: Response) -> "HistoryResponse":
        body = response.get_body()
        return HistoryResponse(
            status=response.status,
            reason=response.reason,
            headers=CIMultiDictProxy(response.headers),
            body=body,
        )

    def __packed__(self) -> Dict[str, Any]:
        headers = [[key, val] for key, val in self._headers.items()]
        return {
            "status": self._status,
            "reason": self._reason,
            "headers": headers,
            "body": self._body,
        }

    @classmethod
    def __unpacked__(cls, *,
                     status: int,
                     reason: str,
                     headers: List[Tuple[str, str]],
                     body: bytes,
                     **kwargs: Any) -> "HistoryResponse":
        real_headers = CIMultiDictProxy(CIMultiDict(headers))
        return HistoryResponse(
            status=status,
            reason=reason,
            headers=real_headers,
            body=body,
        )

    def __repr__(self) -> str:
        return (f"HistoryResponse("
                f"status={self._status!r}, "
                f"reason={self._reason!r}, "
                f"headers={self._headers!r}, "
                f"body={self._body!r}"
                f")")
