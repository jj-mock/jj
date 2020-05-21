from typing import Any, Dict, List, Optional, Tuple

from packed import packable

from ...responses import Response

__all__ = ("HistoryResponse",)


@packable("HistoryResponse")
class HistoryResponse:
    def __init__(self, status: int, reason: str,
                 headers: List[Tuple[str, str]],
                 body: Optional[bytes]) -> None:
        self._status = status
        self._reason = reason
        self._headers = headers
        self._body = body

    @staticmethod
    def from_response(response: Response) -> "HistoryResponse":
        packed = response.__packed__()
        return HistoryResponse(
            status=packed["status"],
            reason=packed["reason"],
            headers=packed["headers"],
            body=packed["body"],
        )

    def __packed__(self) -> Dict[str, Any]:
        return {
            "status": self._status,
            "reason": self._reason,
            "headers": self._headers,
            "body": self._body,
        }

    @classmethod
    def __unpacked__(cls, *, status: int, reason: str,
                     headers: List[Tuple[str, str]],
                     body: Optional[bytes],
                     **kwargs: Any) -> "HistoryResponse":
        return HistoryResponse(
            status=status,
            reason=reason,
            headers=headers,
            body=body,
        )

    def __repr__(self) -> str:
        return (f"HistoryResponse("
                f"status={self._status!r}, "
                f"reason={self._reason!r}, "
                f"headers={self._headers!r}, "
                f"body={self._body!r}"
                f")")
