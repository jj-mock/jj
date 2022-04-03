from typing import Any, Dict

from packed import packable

from ..requests import Request
from ._expiration_policy import ExpirationPolicy

__all__ = ("ExpireNever",)


@packable("jj.expiration_policy.ExpireNever")
class ExpireNever(ExpirationPolicy):
    async def is_expired(self, request: Request) -> bool:
        return False

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"

    def __packed__(self) -> Dict[str, Any]:
        return dict()

    @classmethod
    def __unpacked__(cls, **kwargs: Any) -> "ExpireNever":
        return cls()
