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
    """
    Matches HTTP requests based on headers.

    This matcher checks if the incoming request's headers match
    a specified set of headers, or a dynamic attribute-based matcher.
    """

    def __init__(self, headers: DictOrTupleListOrAttrMatcher, *, resolver: Resolver) -> None:
        """
        Initialize a HeaderMatcher with the specified headers and resolver.

        :param headers: The headers to match against, either as a dictionary,
                        list of tuples, or a dynamic attribute matcher.
        :param resolver: The resolver responsible for registering this matcher.
        """
        super().__init__(resolver=resolver)
        if isinstance(headers, AttributeMatcher):
            self._matcher = headers
        else:
            self._matcher = MultiDictMatcher(headers)

    @property
    def sub_matcher(self) -> AttributeMatcher:
        """
        Return the underlying attribute matcher used for header matching.

        :return: The matcher that evaluates the headers.
        """
        return self._matcher

    async def match(self, request: Request) -> bool:
        """
        Determine if the request's headers match the expected headers.

        :param request: The HTTP request containing the headers to match.
        :return: `True` if the request's headers match the expected values, otherwise `False`.
        """
        return await self._matcher.match(request.headers)

    def __repr__(self) -> str:
        """
        Return a string representation of the HeaderMatcher instance.

        :return: A string describing the class, matcher, and resolver.
        """
        return f"{self.__class__.__qualname__}({self._matcher!r}, resolver={self._resolver!r})"

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the HeaderMatcher instance for serialization.

        :return: A dictionary containing the serialized form of the matcher.
        """
        return {"headers": self._matcher}

    @classmethod
    def __unpacked__(cls, *,
                     headers: DictOrTupleListOrAttrMatcher,
                     resolver: Resolver,
                     **kwargs: Any) -> "HeaderMatcher":
        """
        Unpack a HeaderMatcher instance from its serialized form.

        :param headers: The headers matcher to use for this instance.
        :param resolver: The resolver to bind this matcher to.
        :param kwargs: Additional arguments (unused in this case).
        :return: A new instance of HeaderMatcher.
        """
        return cls(headers, resolver=resolver)
