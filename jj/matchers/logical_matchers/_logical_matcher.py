from typing import List

from ...resolvers import Resolver
from .._resolvable_matcher import ResolvableMatcher

__all__ = ("LogicalMatcher",)


class LogicalMatcher(ResolvableMatcher):
    def __init__(self, resolver: Resolver, matchers: List[ResolvableMatcher]) -> None:
        super().__init__(resolver)
        assert len(matchers) > 0
        self._matchers = matchers
