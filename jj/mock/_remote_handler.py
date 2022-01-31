from types import TracebackType
from typing import TYPE_CHECKING, Any, List, Optional, Type, Union
from uuid import UUID, uuid4

from jj.matchers import LogicalMatcher, RequestMatcher

if TYPE_CHECKING:
    from ._remote_mock import RemoteMock
    MockType = RemoteMock
else:
    MockType = Any

from ._history import HistoryItem
from ._remote_response import RemoteResponseType

__all__ = ("RemoteHandler",)


class RemoteHandler:
    def __init__(self,
                 mock: MockType,
                 matcher: Union[RequestMatcher, LogicalMatcher],
                 response: RemoteResponseType) -> None:
        self._id = uuid4()
        self._mock = mock
        self._matcher = matcher
        self._response = response

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def matcher(self) -> Union[RequestMatcher, LogicalMatcher]:
        return self._matcher

    @property
    def response(self) -> RemoteResponseType:
        return self._response

    async def register(self) -> None:
        await self._mock.register(self)

    async def deregister(self) -> None:
        await self._mock.deregister(self)

    async def fetch_history(self) -> List[HistoryItem]:
        return await self._mock.fetch_history(self)

    async def __aenter__(self) -> None:
        await self.register()

    async def __aexit__(self,
                        exc_type: Optional[Type[BaseException]],
                        exc_val: Optional[BaseException],
                        exc_tb: Optional[TracebackType]) -> None:
        await self.deregister()
