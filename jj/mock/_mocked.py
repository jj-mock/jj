from types import TracebackType
from typing import List, Optional, Type, Union

from rtry import CancelledError, retry
from rtry.types import AttemptValue, DelayCallable, DelayValue, LoggerCallable, TimeoutValue

from ._history import HistoryItem
from ._remote_handler import RemoteHandler

__all__ = ("Mocked",)


class Mocked:
    def __init__(self, handler: RemoteHandler, *,
                 disposable: bool = True,
                 prefetch_history: bool = True) -> None:
        self._handler = handler
        self._disposable = disposable
        self._prefetch_history = prefetch_history
        self._history: Union[List[HistoryItem], None] = None

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

    def __repr__(self) -> str:
        return (f"Mocked<{self._handler}, "
                f"disposable={self._disposable}, "
                f"prefetch_history={self._prefetch_history}>")
