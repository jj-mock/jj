import asyncio
import threading
from concurrent.futures import Future
from typing import Any, Callable, Coroutine, TypeVar

__all__ = ("Thread", "run_async",)

T = TypeVar("T")
TargetType = Callable[..., Coroutine[None, None, T]]


class Thread(threading.Thread):
    """
    Thread that runs an async function in a new event loop.

    Uses a thread-safe concurrent.futures.Future to communicate results
    between threads.
    """

    def __init__(self, future: "Future[T]", target: TargetType[T],
                 *args: Any, **kwargs: Any) -> None:
        """
        Initialize the thread with target async function and arguments.

        :param future: Thread-safe future to set the result on completion.
        :param target: Async function to run in the new event loop.
        :param args: Positional arguments for the target function.
        :param kwargs: Keyword arguments for the target function.
        """
        super().__init__()
        self._future = future
        self._target = target
        self._args = args
        self._kwargs = kwargs

    def run(self) -> None:
        """
        Run the async function in a new event loop and set the result.

        Creates a new event loop for this thread and safely sets the result
        using the thread-safe concurrent.futures.Future.
        """
        try:
            result = asyncio.run(self._target(*self._args, **self._kwargs))
        except Exception as e:
            self._future.set_exception(e)
        else:
            self._future.set_result(result)


def run_async(target: TargetType[T], *args: Any, **kwargs: Any) -> T:
    """
    Run an async function, handling both sync and async contexts safely.

    If called from a synchronous context (no running loop), runs the target
    directly. If called from an async context (with a running loop), runs
    the target in a separate thread with its own event loop to avoid blocking.

    :param target: Async function to execute.
    :param args: Positional arguments for the target function.
    :param kwargs: Keyword arguments for the target function.
    :return: The result of the async function.
    """
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
