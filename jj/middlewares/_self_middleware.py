from inspect import signature

from ..apps import AbstractApp
from ..handlers import HandlerFunction
from ..requests import Request
from ..responses import StreamResponse
from ._root_middleware import RootMiddleware

__all__ = ("SelfMiddleware",)


class SelfMiddleware(RootMiddleware):
    async def do(self, request: Request, handler: HandlerFunction,
                 app: AbstractApp) -> StreamResponse:
        unwrapped = self._resolver.unwrap(handler)
        sig = signature(unwrapped)
        if len(sig.parameters) == 2:
            response = await handler(app, request)
        else:
            response = await handler(request)
        return response
