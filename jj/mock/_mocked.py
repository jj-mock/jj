from types import TracebackType
from typing import Any, Generator, List, Optional, Type, Union

from rtry import CancelledError, retry
from rtry.types import AttemptValue, DelayCallable, DelayValue, LoggerCallable, TimeoutValue

from ._history import HistoryFormatter, HistoryItem
from ._remote_handler import RemoteHandler
from ._utils import run_async

__all__ = ("Mocked",)


class Mocked:
    def __init__(self, handler: RemoteHandler, *,
                 disposable: bool = True,
                 prefetch_history: bool = True,
                 history_formatter: Optional[HistoryFormatter] = None
                 ) -> None:
        self._handler = handler
        self._disposable = disposable
        self._prefetch_history = prefetch_history
        self._history: Union[List[HistoryItem], None] = None
        self._history_formatter = history_formatter

    @property
    def handler(self) -> RemoteHandler:
        return self._handler

    @property
    def disposable(self) -> bool:
        return self._disposable

    @property
    def prefetch_history(self) -> bool:
        return self._prefetch_history

    @property
    def history(self) -> Union[List[HistoryItem], None]:
        return self._history

    async def fetch_history(self) -> List[HistoryItem]:
        self._history = await self._handler.fetch_history()
        return self._history

    async def wait_for_requests(self, count: int = 1, *,
                                timeout: TimeoutValue = 0,
                                attempts: Optional[AttemptValue] = None,
                                delay: Optional[Union[DelayValue, DelayCallable]] = None,
                                logger: Optional[LoggerCallable] = None) -> None:
        try:
            await retry(until=lambda x: len(x) < count,
                        attempts=attempts,
                        timeout=timeout,
                        delay=delay,
                        logger=logger)(self.fetch_history)()
        except CancelledError:
            pass

    def __await__(self) -> Generator[Any, None, "Mocked"]:
        yield from self._handler.register().__await__()
        return self

    async def __aenter__(self) -> "Mocked":
        self._history = None
        await self._handler.register()
        return self

    async def __aexit__(self,
                        exc_type: Optional[Type[BaseException]],
                        exc_val: Optional[BaseException],
                        exc_tb: Optional[TracebackType]) -> None:
        if self._prefetch_history:
            await self.fetch_history()

        if self._disposable:
            await self._handler.deregister()

    def __enter__(self) -> "Mocked":
        return run_async(self.__aenter__)

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> None:
        return run_async(self.__aexit__, exc_type, exc_val, exc_tb)

    def __repr__(self) -> str:
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
