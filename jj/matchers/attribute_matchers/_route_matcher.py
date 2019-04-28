from typing import Dict, Union

from aiohttp.web_urldispatcher import DynamicResource

from ._attribute_matcher import AttributeMatcher

__all__ = ("RouteMatcher",)


class RouteMatcher(AttributeMatcher):
    class Resource(DynamicResource):
        def match(self, path: str) -> Union[Dict[str, str], None]:
            return self._match(path)

    def __init__(self, path: str) -> None:
        self._resource = self.Resource(path)

    def get_segments(self, path: str) -> Dict[str, str]:
        return self._resource.match(path) or {}

    def match(self, path: str) -> bool:
        return self._resource.match(path) is not None
