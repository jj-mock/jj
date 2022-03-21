__all__ = ("ExpireAfterRequests",)

from typing import Any, Dict

from packed import packable

from ._expiration_policy import ExpirationPolicy


@packable("jj.expiration_policy.ExpireAfterRequests")
class ExpireAfterRequests(ExpirationPolicy):
    def __init__(self, max_requests_count: int) -> None:
        self.max_requests_count = max_requests_count
        self.current_requests_count = 0

    def is_expired(self) -> bool:
        if self.current_requests_count < self.max_requests_count:
            self.current_requests_count += 1
            return False
        return True

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self.max_requests_count!r})"

    def __packed__(self) -> Dict[str, Any]:
        return {
            "max_requests_count": self.max_requests_count,
        }

    @classmethod
    def __unpacked__(cls, max_requests_count: int) -> "ExpireAfterRequests":
        return cls(max_requests_count=max_requests_count)
