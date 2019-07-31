from typing import Union

from aiohttp import ClientSession
from packed import pack

from jj.http.codes import OK
from jj.matchers import LogicalMatcher, RequestMatcher
from jj.responses import Response

from ._remote_handler import RemoteHandler

__all__ = ("RemoteMock",)


class RemoteMock:
    def __init__(self, url: str) -> None:
        self._url = url

    def create_handler(self,
                       matcher: Union[RequestMatcher, LogicalMatcher],
                       response: Response) -> RemoteHandler:
        return RemoteHandler(self, matcher, response)

    async def register(self, handler: RemoteHandler) -> "RemoteMock":
        headers = {"x-jj-remote-mock": ""}
        payload = {
            "id": str(handler._id),
            "request": handler._matcher,
            "response": handler._response,
        }
        binary = pack(payload)

        async with ClientSession() as session:
            response = await session.post(self._url, data=binary, headers=headers)
            assert response.status == OK
        return self

    async def deregister(self, handler: RemoteHandler) -> "RemoteMock":
        headers = {"x-jj-remote-mock": ""}
        payload = {
            "id": str(handler._id),
            "request": handler._matcher,
            "response": handler._response,
        }
        binary = pack(payload)

        async with ClientSession() as session:
            response = await session.delete(self._url, data=binary, headers=headers)
            assert response.status == OK
        return self
