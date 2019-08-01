from typing import Any, Union
from uuid import uuid4

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

    async def register(self) -> None:
        await self._mock.register(self)

    async def deregister(self) -> None:
        await self._mock.deregister(self)
