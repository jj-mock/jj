from ...requests import Request
from ._logical_matcher import LogicalMatcher

__all__ = ("AnyMatcher",)


class AnyMatcher(LogicalMatcher):
    async def match(self, request: Request) -> bool:
        for matcher in self._matchers:
            if await matcher.match(request):
                return True
        return False
