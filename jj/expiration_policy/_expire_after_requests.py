from typing import Any, Dict

from packed import packable

from ..requests import Request
from ._expiration_policy import ExpirationPolicy

__all__ = ("ExpireAfterRequests",)


@packable("jj.expiration_policy.ExpireAfterRequests")
class ExpireAfterRequests(ExpirationPolicy):
    def __init__(self, max_requests_count: int) -> None:
        assert max_requests_count > 0, \
            f'max_requests_count must be more than 0, {max_requests_count} given'

        self._max_requests_count = max_requests_count
        self._current_requests_count = 0

    @property
    def max_requests_count(self) -> int:
        return self._max_requests_count

    async def is_expired(self, request: Request) -> bool:
        if self._current_requests_count < self._max_requests_count:
            self._current_requests_count += 1
            return False
        return True

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self._max_requests_count!r})"

    def __packed__(self) -> Dict[str, Any]:
        return {
            "max_requests_count": self._max_requests_count,
        }

    @classmethod
    def __unpacked__(cls, *, max_requests_count: int, **kwargs: Any) -> "ExpireAfterRequests":
        return cls(max_requests_count=max_requests_count)
