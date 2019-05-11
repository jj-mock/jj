from typing import Any

from ._attribute_matcher import AttributeMatcher

__all__ = ("EqualMatcher", "NotEqualMatcher",)


class EqualMatcher(AttributeMatcher):
    def __init__(self, expected: Any) -> None:
        self._expected = expected

    async def match(self, actual: Any) -> bool:
        return bool(self._expected == actual)  # type casting for mypy


class NotEqualMatcher(EqualMatcher):
    async def match(self, actual: Any) -> bool:
        return bool(self._expected != actual)  # type casting for mypy
