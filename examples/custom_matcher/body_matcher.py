from typing import Dict, Any

from packed import packable

from jj import Request, App
from jj.matchers import RequestMatcher
from jj.resolvers import Resolver

__all__ = ("match_body_key", "BodyKeyMatcher",)


@packable("BodyKeyMatcher")
class BodyKeyMatcher(RequestMatcher):
    def __init__(self, key: str, *, resolver: Resolver) -> None:
        super().__init__(resolver=resolver)
        self._key = key

    async def match(self, request: Request) -> bool:
        try:
            body = await request.json()
        except Exception:
            return False
        return self._key in body

    def __packed__(self) -> Dict[str, Any]:
        return {"key": self._key}

    @classmethod
    def __unpacked__(cls, *,
                     key: str,
                     resolver: Resolver,
                     **kwargs: Any) -> "BodyKeyMatcher":
        return cls(key, resolver=resolver)


def match_body_key(key: str) -> BodyKeyMatcher:
    return BodyKeyMatcher(key, resolver=App.resolver)
