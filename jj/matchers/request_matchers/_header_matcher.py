from typing import Union

from ...requests import Request
from ...resolvers import Resolver
from ..attribute_matchers import AttributeMatcher, DictOrTupleList, MultiDictMatcher
from ._request_matcher import RequestMatcher

__all__ = ("HeaderMatcher",)


DictOrTupleListOrAttrMatcher = Union[DictOrTupleList, AttributeMatcher]


class HeaderMatcher(RequestMatcher):
    def __init__(self, headers: DictOrTupleListOrAttrMatcher, *, resolver: Resolver) -> None:
        super().__init__(resolver=resolver)
        if isinstance(headers, AttributeMatcher):
            self._matcher = headers
        else:
            self._matcher = MultiDictMatcher(headers)

    async def match(self, request: Request) -> bool:
        return await self._matcher.match(request.headers)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self._matcher!r}, resolver={self._resolver!r})"
