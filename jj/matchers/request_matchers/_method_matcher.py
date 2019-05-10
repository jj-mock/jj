from ...requests import Request
from ...resolvers import Resolver
from ..attribute_matchers import AttributeMatcher, EqualMatcher, StrOrAttrMatcher
from ._request_matcher import RequestMatcher

__all__ = ("MethodMatcher",)


class MethodMatcher(RequestMatcher):
    def __init__(self, resolver: Resolver, method: StrOrAttrMatcher) -> None:
        super().__init__(resolver)
        if isinstance(method, AttributeMatcher):
            self._matcher = method
        else:
            self._matcher = EqualMatcher(method)

    async def match(self, request: Request) -> bool:
        return self._matcher.match("*") or self._matcher.match(request.method)