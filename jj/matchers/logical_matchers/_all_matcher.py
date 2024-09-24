from typing import Any, Dict, List

from packed import packable

from ...requests import Request
from ...resolvers import Resolver
from .._resolvable_matcher import ResolvableMatcher
from ._logical_matcher import LogicalMatcher

__all__ = ("AllMatcher",)


@packable("jj.matchers.AllMatcher")
class AllMatcher(LogicalMatcher):
    """
    Matches an HTTP request if all provided matchers succeed.

    This matcher combines multiple `ResolvableMatcher` instances, and it
    returns `True` only if every matcher in the list successfully matches
    the incoming HTTP request.
    """

    def __init__(self, matchers: List[ResolvableMatcher], *, resolver: Resolver) -> None:
        """
        Initialize an AllMatcher with a list of matchers and a resolver.

        :param matchers: A list of matchers to evaluate. Matching succeeds only if
                         every matcher in this list returns `True`.
        :param resolver: The resolver responsible for registering this matcher.
        :raises AssertionError: If the matchers list is empty.
        """
        super().__init__(resolver=resolver)
        assert len(matchers) > 0
        self._matchers = matchers

    @property
    def sub_matchers(self) -> List[ResolvableMatcher]:
        """
        Return the list of matchers used by this `AllMatcher`.

        :return: A copy of the list of matchers.
        """
        return self._matchers[:]

    async def match(self, request: Request) -> bool:
        """
        Determine if all matchers in the list match the given request.

        :param request: The HTTP request to evaluate.
        :return: `True` only if every matcher in the list returns `True`, otherwise `False`.
        """
        for matcher in self._matchers:
            if not await matcher.match(request):
                return False
        return True

    def __repr__(self) -> str:
        """
        Return a string representation of the AllMatcher instance.

        :return: A string describing the class, matchers, and resolver.
        """
        return (f"{self.__class__.__qualname__}"
                f"({self._matchers!r}, resolver={self._resolver!r})")

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the AllMatcher instance for serialization.

        :return: A dictionary containing the serialized matchers.
        """
        return {"matchers": self._matchers}

    @classmethod
    def __unpacked__(cls, *,
                     matchers: List[ResolvableMatcher],
                     resolver: Resolver,
                     **kwargs: Any) -> "AllMatcher":
        """
        Unpack an AllMatcher instance from its serialized form.

        :param matchers: The list of matchers to use for this instance.
        :param resolver: The resolver to bind this matcher to.
        :param kwargs: Additional arguments (unused in this case).
        :return: A new instance of AllMatcher.
        """
        return cls(matchers, resolver=resolver)
