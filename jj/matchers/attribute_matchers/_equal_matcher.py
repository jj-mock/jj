from typing import Any, Dict

from packed import packable

from ._attribute_matcher import AttributeMatcher

__all__ = ("EqualMatcher", "NotEqualMatcher",)


@packable("jj.matchers.EqualMatcher")
class EqualMatcher(AttributeMatcher):
    def __init__(self, expected: Any) -> None:
        self._expected = expected

    async def match(self, actual: Any) -> bool:
        return bool(self._expected == actual)  # type casting for mypy

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self._expected!r})"

    def __packed__(self) -> Dict[str, Any]:
        return {"expected": self._expected}

    @classmethod
    def __unpacked__(cls, *, expected: Any, **kwargs: Any) -> "EqualMatcher":
        return cls(expected)


@packable("jj.matchers.NotEqualMatcher")
class NotEqualMatcher(EqualMatcher):
    async def match(self, actual: Any) -> bool:
        return bool(self._expected != actual)  # type casting for mypy

    def __packed__(self) -> Dict[str, Any]:
        return {"expected": self._expected}

    @classmethod
    def __unpacked__(cls, *, expected: Any, **kwargs: Any) -> "NotEqualMatcher":
        return cls(expected)
