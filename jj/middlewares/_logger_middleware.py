from typing import Type, Callable

from ..apps import AbstractApp
from ..handlers import HandlerFunction
from ..logs import Logger
from ..requests import Request
from ..resolvers import Resolver
from ..responses import Response

from ._base_middleware import BaseMiddleware, AppOrHandler


__all__ = ("LoggerMiddleware",)


class LoggerMiddleware(BaseMiddleware):
    def __init__(self, resolver: Resolver, logger: Logger) -> None:
        super().__init__(resolver)
        self._logger = logger

    def on_app(self, app: Type[AbstractApp]) -> None:
        super().on_app(app)
        self._resolver.register_attribute("logger", self._logger, app)

    def on_handler(self, handler: HandlerFunction) -> None:
        super().on_handler(handler)
        self._resolver.register_attribute("logger", self._logger, handler)

    def _register_middleware(self, app_or_handler: AppOrHandler, middleware: Callable):
        old_middlewares = self._resolver.get_attribute("middlewares", app_or_handler, [])
        new_middlewares = [middleware] + old_middlewares
        self._resolver.register_attribute("middlewares", new_middlewares, app_or_handler)

    async def do(self, request: Request, handler: HandlerFunction, app: AbstractApp) -> Response:
        logger = self._resolver.get_attribute("logger", handler, None)
        if logger is None:
            logger = self._resolver.get_attribute("logger", type(app), None)

        if logger:
            logger.info(request, extra={"jj_request": request})

        response = await handler(request)

        if logger:
            logger.info(response, extra={"jj_request": request, "jj_response": response})

        return response
