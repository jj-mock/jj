from types import TracebackType
from typing import TYPE_CHECKING, Any, List, Optional, Type, Union
from uuid import UUID, uuid4

from jj.matchers import LogicalMatcher, RequestMatcher

if TYPE_CHECKING:
    from ._remote_mock import RemoteMock
    MockType = RemoteMock
else:
    MockType = Any

from ._history import HistoryAdapterType, HistoryItem, default_history_adapter
from ._remote_response import RemoteResponseType

__all__ = ("RemoteHandler",)


class RemoteHandler:
    def __init__(self,
                 mock: MockType,
                 matcher: Union[RequestMatcher, LogicalMatcher],
                 response: RemoteResponseType,
                 *,
                 allowed_number_of_requests: Union[int, None],
                 history_adapter: Optional[HistoryAdapterType] = default_history_adapter,
                 ) -> None:
        self._id = uuid4()
        self._mock = mock
        self._matcher = matcher
        self._response = response
        self._history_adapter = history_adapter
        self._allowed_number_of_requests = allowed_number_of_requests

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def matcher(self) -> Union[RequestMatcher, LogicalMatcher]:
        return self._matcher

    @property
    def response(self) -> RemoteResponseType:
        return self._response

    @property
    def allowed_number_of_requests(self) -> Union[int, None]:
        return self._allowed_number_of_requests

    async def register(self) -> None:
        await self._mock.register(self)

    async def deregister(self) -> None:
        await self._mock.deregister(self)

    async def fetch_history(self) -> List[HistoryItem]:
        history = await self._mock.fetch_history(self)
        if self._history_adapter:
            return [self._history_adapter(x) for x in history]
        return history

    async def __aenter__(self) -> None:
        await self.register()

    async def __aexit__(self,
                        exc_type: Optional[Type[BaseException]],
                        exc_val: Optional[BaseException],
                        exc_tb: Optional[TracebackType]) -> None:
        await self.deregister()
