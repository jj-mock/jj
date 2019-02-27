from typing import Optional

from ..apps import AbstractApp
from ..handlers import HandlerFunction
from ..requests import Request
from ..resolvers import Resolver
from ..responses import Response


__all__ = ("AbstractMiddleware",)


class AbstractMiddleware:
    def __init__(self, resolver: Optional[Resolver] = None) -> None:
        self._resolver = resolver if resolver else getattr(self, "resolver", None)
        assert self._resolver is not None

    async def _do(self, request: Request, *,
                  handler: HandlerFunction, app: AbstractApp) -> Response:
        return await self.do(request, handler, app)

    async def do(self, request: Request, handler: HandlerFunction, app: AbstractApp) -> Response:
        return await handler(request)
