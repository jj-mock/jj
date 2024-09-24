from typing import Any, Dict

from packed import packable

from ...requests import Request
from ...resolvers import Resolver
from ..attribute_matchers import AttributeMatcher, RouteMatcher, StrOrAttrMatcher
from ._request_matcher import RequestMatcher

__all__ = ("PathMatcher",)


@packable("jj.matchers.PathMatcher")
class PathMatcher(RequestMatcher):
    """
    Matches HTTP requests based on the URL path.

    This matcher checks if the incoming request's URL path matches a specific
    string or pattern, and can extract segments from the path if needed.
    """

    def __init__(self, path: StrOrAttrMatcher, *, resolver: Resolver) -> None:
        """
        Initialize a PathMatcher with the URL path and resolver.

        :param path: The path or pattern to match against, or a matcher that can
                     evaluate the path dynamically.
        :param resolver: The resolver responsible for registering this matcher.
        """
        super().__init__(resolver=resolver)
        if isinstance(path, AttributeMatcher):
            self._matcher = path
        else:
            self._matcher = RouteMatcher(path)

    @property
    def sub_matcher(self) -> AttributeMatcher:
        """
        Return the underlying attribute matcher used for the path matching.

        :return: The matcher that evaluates the path condition.
        """
        return self._matcher

    async def match(self, request: Request) -> bool:
        """
        Determine if the request path matches the expected path or pattern.

        :param request: The HTTP request containing the path to match.
        :return: `True` if the request path matches the expected path or pattern,
                 otherwise `False`.
        """
        matched = await self._matcher.match(request.path)
        if matched and isinstance(self._matcher, RouteMatcher):
            request.segments = self._matcher.get_segments(request.path)
        else:
            request.segments = None  # type: ignore
        return matched

    def __repr__(self) -> str:
        """
        Return a string representation of the PathMatcher instance.

        :return: A string describing the class, matcher, and resolver.
        """
        return f"{self.__class__.__qualname__}({self._matcher!r}, resolver={self._resolver!r})"

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the PathMatcher instance for serialization.

        :return: A dictionary containing the serialized form of the matcher.
        """
        return {"path": self._matcher}

    @classmethod
    def __unpacked__(cls, *,
                     path: StrOrAttrMatcher,
                     resolver: Resolver,
                     **kwargs: Any) -> "PathMatcher":
        """
        Unpack a PathMatcher instance from its serialized form.

        :param path: The path matcher to use for this instance.
        :param resolver: The resolver to bind this matcher to.
        :param kwargs: Additional keyword arguments (ignored).
        :return: A new instance of PathMatcher.
        """
        return cls(path, resolver=resolver)
