from typing import Any, Union
from uuid import UUID, uuid4

from jj.matchers import LogicalMatcher, RequestMatcher
from jj.responses import Response

__all__ = ("RemoteHandler",)


class RemoteHandler:
    def __init__(self,
                 mock: Any,
                 matcher: Union[RequestMatcher, LogicalMatcher],
                 response: Response) -> None:
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
    def response(self) -> Response:
        return self._response

    async def register(self) -> None:
        await self._mock.register(self)

    async def deregister(self) -> None:
        await self._mock.deregister(self)

    async def history(self) -> Any:
        return await self._mock.history(self)
