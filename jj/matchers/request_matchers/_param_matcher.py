from typing import Any, Dict, Union

from packed import packable

from ...requests import Request
from ...resolvers import Resolver
from ..attribute_matchers import AttributeMatcher, DictOrTupleList, MultiDictMatcher
from ._request_matcher import RequestMatcher

__all__ = ("ParamMatcher", "DictOrTupleListOrAttrMatcher",)


DictOrTupleListOrAttrMatcher = Union[DictOrTupleList, AttributeMatcher]


@packable("jj.matchers.ParamMatcher")
class ParamMatcher(RequestMatcher):
    """
    Matches HTTP requests based on query parameters.

    This matcher checks if the incoming request's query parameters match
    a specified set of parameters, or a dynamic attribute-based matcher.
    """

    def __init__(self, params: DictOrTupleListOrAttrMatcher, *, resolver: Resolver) -> None:
        """
        Initialize a ParamMatcher with the specified query parameters and resolver.

        :param params: The query parameters to match against, either as a dictionary,
                       list of tuples, or a dynamic attribute matcher.
        :param resolver: The resolver responsible for registering this matcher.
        """
        super().__init__(resolver=resolver)
        if isinstance(params, AttributeMatcher):
            self._matcher = params
        else:
            self._matcher = MultiDictMatcher(params)

    @property
    def sub_matcher(self) -> AttributeMatcher:
        """
        Return the underlying attribute matcher used for parameter matching.

        :return: The matcher that evaluates the query parameters.
        """
        return self._matcher

    async def match(self, request: Request) -> bool:
        """
        Determine if the request's query parameters match the expected parameters.

        :param request: The HTTP request containing the query parameters to match.
        :return: `True` if the request's parameters match the expected values, otherwise `False`.
        """
        return await self._matcher.match(request.query)

    def __repr__(self) -> str:
        """
        Return a string representation of the ParamMatcher instance.

        :return: A string describing the class, matcher, and resolver.
        """
        return f"{self.__class__.__qualname__}({self._matcher!r}, resolver={self._resolver!r})"

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the ParamMatcher instance for serialization.

        :return: A dictionary containing the serialized form of the matcher.
        """
        return {"params": self._matcher}

    @classmethod
    def __unpacked__(cls, *,
                     params: DictOrTupleListOrAttrMatcher,
                     resolver: Resolver,
                     **kwargs: Any) -> "ParamMatcher":
        """
        Unpack a ParamMatcher instance from its serialized form.

        :param params: The query parameters matcher to use for this instance.
        :param resolver: The resolver to bind this matcher to.
        :param kwargs: Additional keyword arguments (ignored).
        :return: A new instance of ParamMatcher.
        """
        return cls(params, resolver=resolver)
