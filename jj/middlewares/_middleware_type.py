from typing import Any, Callable, Coroutine

from ..responses import Response

MiddlewareType = Callable[..., Coroutine[Any, Any, Response]]

__all__ = ("MiddlewareType",)
