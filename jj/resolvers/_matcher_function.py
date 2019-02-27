from typing import Callable, Any, Coroutine

from ..requests import Request


__all__ = ("MatcherFunction",)


MatcherFunction = Callable[[Request], Coroutine[Any, Any, bool]]
