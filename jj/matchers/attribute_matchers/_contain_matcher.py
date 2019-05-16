from typing import Any, Dict

from ._attribute_matcher import AttributeMatcher

__all__ = ("ContainMatcher", "NotContainMatcher",)


class ContainMatcher(AttributeMatcher):
    def __init__(self, expected: Any) -> None:
        self._expected = expected

    async def match(self, actual: Any) -> bool:
        return self._expected in actual

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self._expected!r})"

    def __jjpack__(self) -> Dict[str, Any]:
        return {"expected": self._expected}

    @classmethod
    def __jjunpack__(cls, *, expected: Any, **kwargs: Any) -> "ContainMatcher":
        return cls(expected)


class NotContainMatcher(ContainMatcher):
    async def match(self, actual: Any) -> bool:
        return self._expected not in actual

    def __jjpack__(self) -> Dict[str, Any]:
        return {"expected": self._expected}

    @classmethod
    def __jjunpack__(cls, *, expected: Any, **kwargs: Any) -> "NotContainMatcher":
        return cls(expected)
