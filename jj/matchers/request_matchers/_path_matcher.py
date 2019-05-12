from ...requests import Request
from ...resolvers import Resolver
from ..attribute_matchers import AttributeMatcher, RouteMatcher, StrOrAttrMatcher
from ._request_matcher import RequestMatcher

__all__ = ("PathMatcher",)


class PathMatcher(RequestMatcher):
    def __init__(self, path: StrOrAttrMatcher, *, resolver: Resolver) -> None:
        super().__init__(resolver=resolver)
        if isinstance(path, AttributeMatcher):
            self._matcher = path
        else:
            self._matcher = RouteMatcher(path)

    async def match(self, request: Request) -> bool:
        matched = await self._matcher.match(request.path)
        if matched and isinstance(self._matcher, RouteMatcher):
            request.segments = self._matcher.get_segments(request.path)
        else:
            request.segments = None  # type: ignore
        return matched

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self._matcher!r}, resolver={self._resolver!r})"
