from typing import List, Type

from ..apps import AbstractApp
from ..handlers import HandlerFunction
from ._resolver import Resolver


__all__ = ("ReversedResolver",)


class ReversedResolver(Resolver):
    def get_handlers(self, app: Type[AbstractApp]) -> List[HandlerFunction]:
        handlers = super().get_handlers(app)
        return list(reversed(handlers))
