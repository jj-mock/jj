from ..handlers import HandlerFunction
from ..requests import Request
from ..resolvers import Resolver

__all__ = ("ResolvableMatcher",)


class ResolvableMatcher:
    def __init__(self, *, resolver: Resolver) -> None:
        self._resolver = resolver

    async def match(self, request: Request) -> bool:
        raise NotImplementedError()

    def __call__(self, handler: HandlerFunction) -> HandlerFunction:
        self._resolver.register_matcher(self.match, handler)
        return handler

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(resolver={self._resolver!r})"
