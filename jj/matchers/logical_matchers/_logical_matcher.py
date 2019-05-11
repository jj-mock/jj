from typing import List

from ...resolvers import Resolver
from .._resolvable_matcher import ResolvableMatcher

__all__ = ("LogicalMatcher",)


class LogicalMatcher(ResolvableMatcher):
    def __init__(self, resolver: Resolver, matchers: List[ResolvableMatcher]) -> None:
        super().__init__(resolver)
        assert len(matchers) > 0
        self._matchers = matchers

    def __repr__(self) -> str:
        return (f"{self.__class__.__qualname__}"
                f"({self._resolver!r}, matchers={self._matchers!r})")
