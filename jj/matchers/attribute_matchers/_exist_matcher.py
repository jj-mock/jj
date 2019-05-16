from typing import Any, Dict

from ._attribute_matcher import AttributeMatcher

__all__ = ("ExistMatcher",)


class ExistMatcher(AttributeMatcher):
    async def match(self, actual: Any) -> bool:
        return True

    def __jjpack__(self) -> Dict[str, Any]:
        return {}

    @classmethod
    def __jjunpack__(cls, **kwargs: Any) -> "ExistMatcher":
        return cls()
