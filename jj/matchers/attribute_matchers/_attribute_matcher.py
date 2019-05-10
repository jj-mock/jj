from typing import Any

__all__ = ("AttributeMatcher",)


class AttributeMatcher:
    def match(self, actual: Any) -> bool:
        raise NotImplementedError()
