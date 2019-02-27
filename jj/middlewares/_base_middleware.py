from typing import Type, Union, Callable

from ..apps import AbstractApp
from ..handlers import HandlerFunction
from ._abstract_middleware import AbstractMiddleware


__all__ = ("BaseMiddleware",)


AppOrHandler = Union[Type[AbstractApp], HandlerFunction]


class BaseMiddleware(AbstractMiddleware):
    def on_app(self, app: Type[AbstractApp]) -> None:
        pass

    def on_handler(self, handler: HandlerFunction) -> None:
        pass

    def _call_hooks(self, app_or_handler: AppOrHandler) -> None:
        if isinstance(app_or_handler, type) and issubclass(app_or_handler, AbstractApp):
            return self.on_app(app_or_handler)
        return self.on_handler(app_or_handler)  # type: ignore

    def _register_middleware(self, app_or_handler: AppOrHandler, middleware: Callable) -> None:
        old_middlewares = self._resolver.get_attribute("middlewares", app_or_handler, [])
        new_middlewares = old_middlewares + [middleware]
        self._resolver.register_attribute("middlewares", new_middlewares, app_or_handler)

    def __call__(self, app_or_handler: AppOrHandler) -> AppOrHandler:
        self._call_hooks(app_or_handler)
        self._register_middleware(app_or_handler, self._do)
        return app_or_handler
