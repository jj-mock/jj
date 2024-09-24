from typing import Any, Dict

from packed import packable

from ...requests import Request
from ...resolvers import Resolver
from ..attribute_matchers import AttributeMatcher, EqualMatcher, StrOrAttrMatcher
from ._request_matcher import RequestMatcher

__all__ = ("MethodMatcher",)


@packable("jj.matchers.MethodMatcher")
class MethodMatcher(RequestMatcher):
    """
    Matches HTTP requests based on the HTTP method.

    This matcher checks if the incoming request uses a specified HTTP method
    (e.g., GET, POST). It supports matching against a static method or an
    attribute-based matcher.
    """

    def __init__(self, method: StrOrAttrMatcher, *, resolver: Resolver) -> None:
        """
        Initialize a MethodMatcher with the HTTP method and resolver.

        :param method: The HTTP method to match against, or a matcher that can
                       evaluate the method dynamically.
        :param resolver: The resolver responsible for registering this matcher.
        """
        super().__init__(resolver=resolver)
        if isinstance(method, AttributeMatcher):
            self._matcher = method
        else:
            self._matcher = EqualMatcher(str.upper(method))

    @property
    def sub_matcher(self) -> AttributeMatcher:
        """
        Return the underlying attribute matcher used for the method matching.

        :return: The matcher that evaluates the method condition.
        """
        return self._matcher

    async def match(self, request: Request) -> bool:
        """
        Determine if the request method matches the expected method.

        :param request: The HTTP request containing the method to match.
        :return: `True` if the request method matches the expected method, otherwise `False`.
        """
        return await self._matcher.match("*") or await self._matcher.match(request.method)

    def __repr__(self) -> str:
        """
        Return a string representation of the MethodMatcher instance.

        :return: A string describing the class, matcher, and resolver.
        """
        return f"{self.__class__.__qualname__}({self._matcher!r}, resolver={self._resolver!r})"

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the MethodMatcher instance for serialization.

        :return: A dictionary containing the serialized form of the matcher.
        """
        return {"method": self._matcher}

    @classmethod
    def __unpacked__(cls, *,
                     method: StrOrAttrMatcher,
                     resolver: Resolver,
                     **kwargs: Any) -> "MethodMatcher":
        """
        Unpack a MethodMatcher instance from its serialized form.

        :param method: The method matcher to use for this instance.
        :param resolver: The resolver to bind this matcher to.
        :param kwargs: Additional keyword arguments (ignored).
        :return: A new instance of MethodMatcher.
        """
        return cls(method, resolver=resolver)
