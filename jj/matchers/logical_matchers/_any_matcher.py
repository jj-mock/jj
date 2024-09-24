from typing import Any, Dict, List

from packed import packable

from ...requests import Request
from ...resolvers import Resolver
from .._resolvable_matcher import ResolvableMatcher
from ._logical_matcher import LogicalMatcher

__all__ = ("AnyMatcher",)


@packable("jj.matchers.AnyMatcher")
class AnyMatcher(LogicalMatcher):
    """
    Matches an HTTP request if any one of the provided matchers succeeds.

    This matcher combines multiple `ResolvableMatcher` instances, and it
    returns `True` as soon as one of them successfully matches the incoming
    HTTP request.
    """

    def __init__(self, matchers: List[ResolvableMatcher], *, resolver: Resolver) -> None:
        """
        Initialize an AnyMatcher with a list of matchers and a resolver.

        :param matchers: A list of matchers to evaluate. Matching succeeds if at least
                         one matcher in this list returns `True`.
        :param resolver: The resolver responsible for registering this matcher.
        :raises AssertionError: If the matchers list is empty.
        """
        super().__init__(resolver=resolver)
        assert len(matchers) > 0
        self._matchers = matchers

    @property
    def sub_matchers(self) -> List[ResolvableMatcher]:
        """
        Return the list of matchers used by this `AnyMatcher`.

        :return: A copy of the list of matchers.
        """
        return self._matchers[:]

    async def match(self, request: Request) -> bool:
        """
        Determine if any matcher in the list matches the given request.

        :param request: The HTTP request to evaluate.
        :return: `True` if any of the matchers in the list returns `True`, otherwise `False`.
        """
        for matcher in self._matchers:
            if await matcher.match(request):
                return True
        return False

    def __repr__(self) -> str:
        """
        Return a string representation of the AnyMatcher instance.

        :return: A string describing the class, matchers, and resolver.
        """
        return (f"{self.__class__.__qualname__}"
                f"({self._matchers!r}, resolver={self._resolver!r})")

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the AnyMatcher instance for serialization.

        :return: A dictionary containing the serialized matchers.
        """
        return {"matchers": self._matchers}

    @classmethod
    def __unpacked__(cls, *,
                     matchers: List[ResolvableMatcher],
                     resolver: Resolver,
                     **kwargs: Any) -> "AnyMatcher":
        """
        Unpack an AnyMatcher instance from its serialized form.

        :param matchers: The list of matchers to use for this instance.
        :param resolver: The resolver to bind this matcher to.
        :param kwargs: Additional arguments (unused in this case).
        :return: A new instance of AnyMatcher.
        """
        return cls(matchers, resolver=resolver)
