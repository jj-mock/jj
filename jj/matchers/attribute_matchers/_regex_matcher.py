import re
from typing import Any, Dict

from packed import packable

from ._attribute_matcher import AttributeMatcher

__all__ = ("RegexMatcher",)


@packable("jj.matchers.RegexMatcher")
class RegexMatcher(AttributeMatcher):
    def __init__(self, pattern: str, flags: int = 0) -> None:
        self._pattern = pattern
        self._flags = flags
        self._compiled = re.compile(self._pattern, self._flags)

    async def match(self, actual: Any) -> bool:
        return self._compiled.search(actual) is not None

    def __repr__(self) -> str:
        if self._flags == 0:
            return f"{self.__class__.__qualname__}({self._pattern!r})"
        return f"{self.__class__.__qualname__}({self._pattern!r}, {self._flags!r})"

    def __packed__(self) -> Dict[str, Any]:
        return {"pattern": self._pattern, "flags": self._flags}

    @classmethod
    def __unpacked__(cls, *, pattern: str, flags: int = 0, **kwargs: Any) -> "RegexMatcher":
        return cls(pattern, flags)
