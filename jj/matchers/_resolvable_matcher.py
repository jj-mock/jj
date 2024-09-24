from ..handlers import HandlerFunction
from ..requests import Request
from ..resolvers import Resolver

__all__ = ("ResolvableMatcher",)


class ResolvableMatcher:
    """
    Provides a base class for matchers that can resolve HTTP requests.

    This class defines the interface for a matcher that checks if an HTTP
    request meets certain conditions. It registers the matcher to a resolver
    and can be used to bind a handler function to matching requests.
    """

    def __init__(self, *, resolver: Resolver) -> None:
        """
        Initialize a ResolvableMatcher with a given resolver.

        :param resolver: The resolver responsible for handling the registration
                         of the matcher and its corresponding handler.
        """
        self._resolver = resolver

    async def match(self, request: Request) -> bool:
        """
        Determine if the incoming HTTP request matches the conditions of this matcher.

        :param request: The HTTP request to evaluate against the matcher.
        :return: `True` if the request matches, otherwise `False`.
        :raises NotImplementedError: This method must be implemented in a subclass.
        """
        raise NotImplementedError()

    def __call__(self, handler: HandlerFunction) -> HandlerFunction:
        """
        Register a handler function to be executed when a request matches.

        :param handler: The function that will handle requests matching this matcher.
        :return: The handler function, which is registered to the resolver.
        """
        self._resolver.register_matcher(self.match, handler)
        return handler

    def __repr__(self) -> str:
        """
        Return a string representation of the ResolvableMatcher instance.

        :return: A string describing the class and its resolver.
        """
        return f"{self.__class__.__qualname__}(resolver={self._resolver!r})"
