from typing import Any

__all__ = ("AttributeMatcher",)


class AttributeMatcher:
    async def match(self, actual: Any) -> bool:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}()"
