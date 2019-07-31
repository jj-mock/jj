from typing import Any, Callable, Coroutine, Union

from ..requests import Request
from ..responses import Response

__all__ = ("HandlerFunction",)


HandlerFunction = Callable[..., Coroutine[Any, Any, Response]]
