import asyncio
import threading
from asyncio import Future
from typing import Any, Callable, Coroutine, TypeVar

__all__ = ("Thread",)

T = TypeVar("T")
TargetType = Callable[..., Coroutine[None, None, T]]


class Thread(threading.Thread):
    def __init__(self, future: "Future[T]", target: TargetType[T],
                 *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self._future = future
        self._target = target
        self._args = args
        self._kwargs = kwargs

    def run(self) -> None:
        try:
            result = asyncio.run(self._target(*self._args, **self._kwargs))
        except BaseException as e:
            self._future.set_exception(e)
        else:
            self._future.set_result(result)


def run_async(target: TargetType[T], *args: Any, **kwargs: Any) -> T:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(target(*args, **kwargs))
    else:
        future: "Future[T]" = Future()
        thread = Thread(future, target, *args, **kwargs)
        thread.start()
        thread.join()
        return future.result()
