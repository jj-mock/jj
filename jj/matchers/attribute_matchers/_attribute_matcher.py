from typing import Any

__all__ = ("AttributeMatcher",)


class AttributeMatcher:
    async def match(self, actual: Any) -> bool:
        raise NotImplementedError()
