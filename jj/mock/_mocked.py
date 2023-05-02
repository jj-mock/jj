from types import TracebackType
from typing import List, Optional, Type, Union

from rtry import CancelledError, retry
from rtry.types import AttemptValue, DelayCallable, DelayValue, LoggerCallable, TimeoutValue

from ._history import HistoryItem, HistoryRepr
from ._remote_handler import RemoteHandler
from ._utils import run_async

__all__ = ("Mocked",)


class Mocked:
    def __init__(self, handler: RemoteHandler, *,
                 disposable: bool = True,
                 prefetch_history: bool = True,
                 history_repr: Optional[HistoryRepr] = None) -> None:
        self._handler = handler
        self._disposable = disposable
        self._prefetch_history = prefetch_history
        self._history_repr = history_repr
        self._history: Union[List[HistoryItem], None] = None

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

    @property
    def parsed_history(self) -> Union[List[HistoryItem], List[str], None]:
        return self._history_repr.parse_history(self.history) if self._history_repr \
            else self.history

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
        return (f"Mocked<{self._handler}, "
                f"disposable={self._disposable}, "
                f"prefetch_history={self._prefetch_history}, "
                f"history={self.parsed_history}>")
