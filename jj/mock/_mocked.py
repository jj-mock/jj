from asyncio import iscoroutinefunction
from functools import wraps
from types import TracebackType
from typing import Any, Callable, Generator, List, Optional, Type, TypeVar, Union, cast

from rtry import CancelledError, retry
from rtry.types import AttemptValue, DelayCallable, DelayValue, LoggerCallable, TimeoutValue

from ._history import HistoryFormatter, HistoryItem
from ._remote_handler import RemoteHandler
from ._utils import run_async

__all__ = ("Mocked",)

F = TypeVar("F", bound=Callable[..., Any])


class Mocked:
    """
    A context manager and decorator for mocking HTTP requests with remote handlers.

    This class provides multiple ways to mock HTTP requests:
    - As a context manager (sync or async) for scoped mocking
    - As a decorator to wrap entire functions with mocking
    - With the `with_mock` decorator to inject the mock instance into functions

    The class handles automatic registration/deregistration of mocks and can
    optionally fetch request history after use.
    """

    def __init__(self, handler: RemoteHandler, *,
                 disposable: bool = True,
                 prefetch_history: bool = True,
                 history_formatter: Optional[HistoryFormatter] = None
                 ) -> None:
        """
        Initialize a Mocked instance with a remote handler.

        :param handler: The remote handler that manages the mock registration and requests.
        :param disposable: Whether to automatically deregister the mock after use.
                          Defaults to `True`. Deprecated, will be removed in future versions.
        :param prefetch_history: Whether to automatically fetch request history when
                                exiting the context. Defaults to `True`.
        :param history_formatter: Optional formatter for displaying request/response history.
        """
        self._handler = handler
        self._disposable = disposable  # Deprecated, will be removed in future versions
        self._prefetch_history = prefetch_history  # Enable history prefetching in a `with` context
        self._history: Union[List[HistoryItem], None] = None
        self._history_formatter = history_formatter

    @property
    def handler(self) -> RemoteHandler:
        """
        Get the remote handler instance.

        :return: The remote handler managing this mock.
        """
        return self._handler

    @property
    def disposable(self) -> bool:
        """
        Check if the mock is disposable.

        :return: `True` if the mock will be automatically deregistered after use.
        """
        return self._disposable

    @property
    def prefetch_history(self) -> bool:
        """
        Check if history prefetching is enabled.

        :return: `True` if history will be automatically fetched when exiting context.
        """
        return self._prefetch_history

    @property
    def history(self) -> Union[List[HistoryItem], None]:
        """
        Get the fetched request/response history.

        :return: List of history items if fetched, otherwise `None`.
        """
        return self._history

    async def fetch_history(self) -> List[HistoryItem]:
        """
        Fetch the request/response history from the remote handler.

        This method retrieves all recorded interactions with the mock and stores
        them internally for later access via the `history` property.

        :return: List of history items containing request/response pairs.
        """
        self._history = await self._handler.fetch_history()
        return self._history

    async def wait_for_requests(self, count: int = 1, *,
                                timeout: TimeoutValue = 0,
                                attempts: Optional[AttemptValue] = None,
                                delay: Optional[Union[DelayValue, DelayCallable]] = None,
                                logger: Optional[LoggerCallable] = None) -> None:
        """
        Wait for a specified number of requests to be received by the mock.

        This method polls the history until the expected number of requests have been
        received or a timeout/retry limit is reached. Useful for testing async code
        that makes HTTP requests.

        :param count: The minimum number of requests to wait for. Defaults to 1.
        :param timeout: Maximum time to wait in seconds. 0 means no timeout.
        :param attempts: Maximum number of retry attempts. `None` means unlimited.
        :param delay: Delay between retry attempts. Can be a fixed value or callable.
        :param logger: Optional logger callable for retry attempts.
        """
        try:
            await retry(until=lambda x: len(x) < count,
                        attempts=attempts,
                        timeout=timeout,
                        delay=delay,
                        logger=logger)(self.fetch_history)()
        except CancelledError:
            pass

    def __call__(self, func: F) -> F:
        """
        Use the Mocked instance as a decorator.

        When used as a decorator, the mock will be active for the duration of
        the decorated function's execution.

        :param func: The function to wrap with mocking.
        :return: A wrapped function that executes with the mock active.
        :raises TypeError: If applied to a non-callable object.
        """
        if not callable(func):
            raise TypeError(
                f"mocked decorator can only be applied to functions or methods, "
                f"got {type(func).__name__}"
            )

        if iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                async with self:
                    return await func(*args, **kwargs)

            return cast(F, async_wrapper)
        else:
            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                with self:
                    return func(*args, **kwargs)

            return cast(F, sync_wrapper)

    def with_mock(self, func: F) -> F:
        """
        Decorator that injects the mock instance as the first argument to the function.

        This allows the decorated function to access the mock instance directly,
        useful for checking history or performing other mock operations.

        :param func: The function to wrap and inject the mock into.
        :return: A wrapped function that receives the mock as its first argument.
        :raises TypeError: If applied to a non-callable object.
        """
        if not callable(func):
            raise TypeError(
                f"mocked.with_mock decorator can only be applied to functions or methods, "
                f"got {type(func).__name__}"
            )

        if iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper() -> Any:
                async with self as mock:
                    return await func(mock)

            return cast(F, async_wrapper)
        else:
            @wraps(func)
            def sync_wrapper() -> Any:
                with self as mock:
                    return func(mock)

            return cast(F, sync_wrapper)

    def __await__(self) -> Generator[Any, None, "Mocked"]:
        """
        Support for awaiting the mock registration.

        :return: Generator that yields from handler registration.
        """
        yield from self._handler.register().__await__()
        return self

    async def __aenter__(self) -> "Mocked":
        """
        Async context manager entry.

        Registers the mock with the remote handler and clears any existing history.

        :return: The Mocked instance.
        """
        self._history = None
        await self._handler.register()
        return self

    async def __aexit__(self,
                        exc_type: Optional[Type[BaseException]],
                        exc_val: Optional[BaseException],
                        exc_tb: Optional[TracebackType]) -> None:
        """
        Async context manager exit.

        Optionally fetches history and deregisters the mock based on configuration.

        :param exc_type: Exception type if an exception was raised.
        :param exc_val: Exception value if an exception was raised.
        :param exc_tb: Exception traceback if an exception was raised.
        """
        if self._prefetch_history:
            await self.fetch_history()

        if self._disposable:
            await self._handler.deregister()

    def __enter__(self) -> "Mocked":
        """
        Sync context manager entry.

        Registers the mock with the remote handler using async-to-sync conversion.

        :return: The Mocked instance.
        """
        return run_async(self.__aenter__)

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> None:
        """
        Sync context manager exit.

        Handles cleanup using async-to-sync conversion.

        :param exc_type: Exception type if an exception was raised.
        :param exc_val: Exception value if an exception was raised.
        :param exc_tb: Exception traceback if an exception was raised.
        """
        return run_async(self.__aexit__, exc_type, exc_val, exc_tb)

    def __repr__(self) -> str:
        """
        String representation of the Mocked instance.

        Includes configuration details and formatted history if available.

        :return: A string representation showing disposable, prefetch_history settings,
                 and optionally the formatted history.
        """
        if self._history_formatter:
            formatted = None
            if self._history is not None:
                formatted = self._history_formatter.format_history(self._history)
            return (f"Mocked<disposable={self._disposable}, "
                    f"prefetch_history={self._prefetch_history} "
                    f"history={formatted}>")
        else:
            return (f"Mocked<disposable={self._disposable}, "
                    f"prefetch_history={self._prefetch_history}>")
