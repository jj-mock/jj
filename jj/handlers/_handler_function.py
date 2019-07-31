from typing import Any, Callable, Coroutine, Union

from ..requests import Request
from ..responses import Response

__all__ = ("HandlerFunction",)


HandlerFunction = Union[
    Callable[[Request], Coroutine[Any, Any, Response]],
    Callable[[Any, Request], Coroutine[Any, Any, Response]],
]
