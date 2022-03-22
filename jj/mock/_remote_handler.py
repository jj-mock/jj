from types import TracebackType
from typing import TYPE_CHECKING, Any, List, Optional, Type, Union
from uuid import UUID, uuid4

from jj.expiration_policy import ExpirationPolicy, ExpireNever
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
                 expiration_policy: Optional[ExpirationPolicy] = None,
                 *,
                 history_adapter: Optional[HistoryAdapterType] = default_history_adapter) -> None:
        self._id = uuid4()
        self._mock = mock
        self._matcher = matcher
        self._response = response
        self._history_adapter = history_adapter

        if expiration_policy is None:
            self._expiration_policy = ExpireNever()
        else:
            self._expiration_policy = expiration_policy

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
    def expiration_policy(self) -> ExpirationPolicy:
        return self._expiration_policy

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
