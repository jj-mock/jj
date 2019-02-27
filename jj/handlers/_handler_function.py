from typing import Callable, Any, Coroutine

from ..requests import Request
from ..responses import Response


__all__ = ("HandlerFunction",)


HandlerFunction = Callable[[Request], Coroutine[Any, Any, Response]]
