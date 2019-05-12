from typing import Any

from ._attribute_matcher import AttributeMatcher

__all__ = ("ExistMatcher",)


class ExistMatcher(AttributeMatcher):
    async def match(self, actual: Any) -> bool:
        return True
