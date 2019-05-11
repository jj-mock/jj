from typing import Dict, Union

from aiohttp.web_urldispatcher import DynamicResource

from ._attribute_matcher import AttributeMatcher

__all__ = ("RouteMatcher",)


class _Resource(DynamicResource):
    def match(self, path: str) -> Union[Dict[str, str], None]:
        return self._match(path)


class RouteMatcher(AttributeMatcher):
    def __init__(self, path: str) -> None:
        self._path = path
        self._resource = _Resource(path)

    def get_segments(self, path: str) -> Dict[str, str]:
        return self._resource.match(path) or {}

    async def match(self, path: str) -> bool:
        return self._resource.match(path) is not None

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self._path!r})"
