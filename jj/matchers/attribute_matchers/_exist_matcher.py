from typing import Any, Dict

from packed import packable

from ._attribute_matcher import AttributeMatcher

__all__ = ("ExistMatcher",)


@packable("jj.matchers.ExistMatcher")
class ExistMatcher(AttributeMatcher):
    async def match(self, actual: Any) -> bool:
        return True

    def __packed__(self) -> Dict[str, Any]:
        return {}

    @classmethod
    def __unpacked__(cls, **kwargs: Any) -> "ExistMatcher":
        return cls()
