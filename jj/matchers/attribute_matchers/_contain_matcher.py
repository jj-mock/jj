from typing import Any

from ._attribute_matcher import AttributeMatcher

__all__ = ("ContainMatcher", "NotContainMatcher",)


class ContainMatcher(AttributeMatcher):
    def __init__(self, expected: Any) -> None:
        self._expected = expected

    def match(self, actual: Any) -> bool:
        return self._expected in actual


class NotContainMatcher(ContainMatcher):
    def match(self, actual: Any) -> bool:
        return self._expected not in actual
