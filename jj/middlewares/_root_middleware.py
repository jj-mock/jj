from ..handlers import HandlerFunction
from ._abstract_middleware import AbstractMiddleware


__all__ = ("RootMiddleware",)


class RootMiddleware(AbstractMiddleware):
    def __call__(self, handler: HandlerFunction):
        return self._do
