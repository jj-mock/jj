from ...requests import Request
from ._logical_matcher import LogicalMatcher

__all__ = ("AllMatcher",)


class AllMatcher(LogicalMatcher):
    async def match(self, request: Request) -> bool:
        for matcher in self._matchers:
            if not await matcher.match(request):
                return False
        return True
