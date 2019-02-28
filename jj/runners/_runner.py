from asyncio import AbstractEventLoop
from typing import Any, List, Iterator
from functools import partial
from collections import OrderedDict

from aiohttp.web import Server as WebServer, BaseRunner
from aiohttp.web_exceptions import HTTPExpectationFailed
from aiohttp.http_writer import HttpVersion11

from ..apps import AbstractApp
from ..middlewares import RootMiddleware
from ..requests import Request
from ..resolvers import Resolver
from ..responses import Response


__all__ = ("AppRunner",)


class AppRunner(BaseRunner):
    def __init__(self, app: AbstractApp,
                 resolver: Resolver,
                 middlewares: List[RootMiddleware],
                 loop: AbstractEventLoop,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._app = app
        self._resolver = resolver
        self._middlewares = middlewares
        self._loop = loop

    def _merge_middlewares(self, root_middlewares: List[Any],
                           app_middlewares: List[Any],
                           handler_middlewares: List[Any]) -> Iterator[Any]:
        middlewares: OrderedDict = OrderedDict()

        for middleware in app_middlewares:
            middlewares[type(middleware.__self__)] = middleware

        for middleware in handler_middlewares:
            middlewares[type(middleware.__self__)] = middleware

        for middleware in root_middlewares:
            unique_key = type(middleware.__self__)
            if unique_key not in middlewares:
                middlewares[unique_key] = middleware

        return reversed(middlewares.values())

    async def _handle(self, request: Request) -> Response:
        expect = request.headers.get("EXPECT")
        if (expect is not None) and (request.version == HttpVersion11):
            if expect.lower() == "100-continue":
                await request.writer.write(b"HTTP/1.1 100 Continue\r\n\r\n")
            else:
                raise HTTPExpectationFailed()

        try:
            resolver = self._app.resolver  # type: ignore
        except (AttributeError, NotImplementedError):
            resolver = self._resolver

        handler = await resolver.resolve(request, self._app)
        unwrapped = resolver.unwrap(handler)

        root_middlewares = [middleware(handler) for middleware in self._middlewares]
        app_middlewares = resolver.get_attribute("middlewares", type(self._app), [])
        handler_middlewares = resolver.get_attribute("middlewares", unwrapped, [])

        middlewares = self._merge_middlewares(root_middlewares,
                                              app_middlewares, handler_middlewares)
        for middleware in middlewares:
            handler = partial(middleware, handler=handler, app=self._app)

        response = await handler(request)
        return response

    def _make_request(self, *args, **kwargs) -> Request:
        return Request(*args, **kwargs, loop=self._loop)

    async def _make_server(self) -> WebServer:
        return WebServer(self._handle, request_factory=self._make_request)  # type: ignore

    async def shutdown(self) -> None:
        pass

    async def _cleanup_server(self) -> None:
        pass
