from typing import List

from .resolvable_matcher import ResolvableMatcher
from ..resolvers import Resolver
from ..requests import Request


__all__ = ("LogicalMatcher", "AllMatcher", "AnyMatcher")


class LogicalMatcher(ResolvableMatcher):
    def __init__(self, resolver: Resolver, matchers: List[ResolvableMatcher]) -> None:
        super().__init__(resolver)
        assert len(matchers) > 0
        self._matchers = matchers


class AllMatcher(LogicalMatcher):
    async def match(self, request: Request) -> bool:
        for matcher in self._matchers:
            if not await matcher.match(request):
                return False
        return True


class AnyMatcher(LogicalMatcher):
    async def match(self, request: Request) -> bool:
        for matcher in self._matchers:
            if await matcher.match(request):
                return True
        return False
