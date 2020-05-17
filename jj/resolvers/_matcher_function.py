from typing import Any, Callable, Coroutine

from ..requests import Request

__all__ = ("MatcherFunction",)


MatcherFunction = Callable[[Request], Coroutine[Any, Any, bool]]
