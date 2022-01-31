from typing import Any, Callable, Coroutine

from ..responses import StreamResponse

__all__ = ("HandlerFunction",)


HandlerFunction = Callable[..., Coroutine[Any, Any, StreamResponse]]
