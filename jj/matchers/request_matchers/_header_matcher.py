from typing import Union

from ...requests import Request
from ...resolvers import Resolver
from ..attribute_matchers import AttributeMatcher, DictOrTupleList, MultiDictMatcher
from ._request_matcher import RequestMatcher

__all__ = ("HeaderMatcher",)


DictOrTupleListOrAttrMatcher = Union[DictOrTupleList, AttributeMatcher]


class HeaderMatcher(RequestMatcher):
    def __init__(self, resolver: Resolver, headers: DictOrTupleListOrAttrMatcher) -> None:
        super().__init__(resolver)
        if isinstance(headers, AttributeMatcher):
            self._matcher = headers
        else:
            self._matcher = MultiDictMatcher(headers)

    async def match(self, request: Request) -> bool:
        return self._matcher.match(request.headers)
