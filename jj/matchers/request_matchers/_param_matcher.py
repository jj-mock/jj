from typing import Union

from ...requests import Request
from ...resolvers import Resolver
from ..attribute_matchers import AttributeMatcher, DictOrTupleList, MultiDictMatcher
from ._request_matcher import RequestMatcher

__all__ = ("ParamMatcher",)


DictOrTupleListOrAttrMatcher = Union[DictOrTupleList, AttributeMatcher]


class ParamMatcher(RequestMatcher):
    def __init__(self, params: DictOrTupleListOrAttrMatcher, *, resolver: Resolver) -> None:
        super().__init__(resolver=resolver)
        if isinstance(params, AttributeMatcher):
            self._matcher = params
        else:
            self._matcher = MultiDictMatcher(params)

    async def match(self, request: Request) -> bool:
        return await self._matcher.match(request.query)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self._matcher!r}, resolver={self._resolver!r})"
