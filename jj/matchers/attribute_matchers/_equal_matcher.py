from typing import Any

from ._attribute_matcher import AttributeMatcher

__all__ = ("EqualMatcher", "NotEqualMatcher",)


class EqualMatcher(AttributeMatcher):
    def __init__(self, expected: Any) -> None:
        self._expected = expected

    def match(self, actual: Any) -> bool:
        return bool(self._expected == actual)  # type casting for mypy


class NotEqualMatcher(EqualMatcher):
    def match(self, actual: Any) -> bool:
        return bool(self._expected != actual)  # type casting for mypy
