from typing import Any

__all__ = ("AttributeMatcher",)


class AttributeMatcher:
    def match(self, expected: Any) -> bool:
        raise NotImplementedError()
