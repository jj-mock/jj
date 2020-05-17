from ..handlers import HandlerFunction
from ._abstract_middleware import AbstractMiddleware
from ._middleware_type import MiddlewareType

__all__ = ("RootMiddleware",)


class RootMiddleware(AbstractMiddleware):
    def __call__(self, handler: HandlerFunction) -> MiddlewareType:
        return self._do
