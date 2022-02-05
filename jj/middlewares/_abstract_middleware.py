from typing import Optional, cast

from ..apps import AbstractApp
from ..handlers import HandlerFunction
from ..requests import Request
from ..resolvers import Resolver
from ..responses import StreamResponse

__all__ = ("AbstractMiddleware",)


class AbstractMiddleware:
    def __init__(self, resolver: Optional[Resolver] = None) -> None:
        if resolver is None:
            resolver = getattr(self, "resolver", None)
            assert resolver is not None
        self._resolver = cast(Resolver, resolver)

    async def _do(self, request: Request, *,
                  handler: HandlerFunction, app: AbstractApp) -> StreamResponse:
        return await self.do(request, handler, app)

    async def do(self, request: Request, handler: HandlerFunction,
                 app: AbstractApp) -> StreamResponse:
        return await handler(request)
