from typing import Any, Dict, Union

from packed import packable

from ...requests import Request
from ...resolvers import Resolver
from ..attribute_matchers import AttributeMatcher, DictOrTupleList, MultiDictMatcher
from ._request_matcher import RequestMatcher

__all__ = ("HeaderMatcher", "DictOrTupleListOrAttrMatcher",)

DictOrTupleListOrAttrMatcher = Union[DictOrTupleList, AttributeMatcher]


@packable("jj.matchers.HeaderMatcher")
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

    def __packed__(self) -> Dict[str, Any]:
        return {"headers": self._matcher}

    @classmethod
    def __unpacked__(cls, *,
                     headers: DictOrTupleListOrAttrMatcher,
                     resolver: Resolver,
                     **kwargs: Any) -> "HeaderMatcher":
        return cls(headers, resolver=resolver)
