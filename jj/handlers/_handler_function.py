from typing import Any, Callable, Coroutine

from ..responses import Response

__all__ = ("HandlerFunction",)


HandlerFunction = Callable[..., Coroutine[Any, Any, Response]]
