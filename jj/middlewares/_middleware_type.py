from typing import Any, Callable, Coroutine

from ..responses import StreamResponse

MiddlewareType = Callable[..., Coroutine[Any, Any, StreamResponse]]

__all__ = ("MiddlewareType",)
