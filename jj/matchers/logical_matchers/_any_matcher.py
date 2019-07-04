from typing import Any, Dict, List

from packed import packable

from ...requests import Request
from ...resolvers import Resolver
from .._resolvable_matcher import ResolvableMatcher
from ._logical_matcher import LogicalMatcher

__all__ = ("AnyMatcher",)


@packable("jj.matchers.AnyMatcher")
class AnyMatcher(LogicalMatcher):
    def __init__(self, matchers: List[ResolvableMatcher], *, resolver: Resolver) -> None:
        super().__init__(resolver=resolver)
        assert len(matchers) > 0
        self._matchers = matchers

    async def match(self, request: Request) -> bool:
        for matcher in self._matchers:
            if await matcher.match(request):
                return True
        return False

    def __repr__(self) -> str:
        return (f"{self.__class__.__qualname__}"
                f"({self._matchers!r}, resolver={self._resolver!r})")

    def __packed__(self) -> Dict[str, Any]:
        return {"matchers": self._matchers}

    @classmethod
    def __unpacked__(cls, *,
                     matchers: List[ResolvableMatcher],
                     resolver: Resolver,
                     **kwargs: Any) -> "AnyMatcher":
        return cls(matchers, resolver=resolver)
