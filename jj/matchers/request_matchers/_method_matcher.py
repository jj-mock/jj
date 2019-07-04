from typing import Any, Dict

from packed import packable

from ...requests import Request
from ...resolvers import Resolver
from ..attribute_matchers import AttributeMatcher, EqualMatcher, StrOrAttrMatcher
from ._request_matcher import RequestMatcher

__all__ = ("MethodMatcher",)


@packable("jj.matchers.MethodMatcher")
class MethodMatcher(RequestMatcher):
    def __init__(self, method: StrOrAttrMatcher, *, resolver: Resolver) -> None:
        super().__init__(resolver=resolver)
        if isinstance(method, AttributeMatcher):
            self._matcher = method
        else:
            self._matcher = EqualMatcher(str.upper(method))

    async def match(self, request: Request) -> bool:
        return await self._matcher.match("*") or await self._matcher.match(request.method)

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({self._matcher!r}, resolver={self._resolver!r})"

    def __packed__(self) -> Dict[str, Any]:
        return {"method": self._matcher}

    @classmethod
    def __unpacked__(cls, *,
                     method: StrOrAttrMatcher,
                     resolver: Resolver,
                     **kwargs: Any) -> "MethodMatcher":
        return cls(method, resolver=resolver)
