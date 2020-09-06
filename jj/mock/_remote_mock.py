from typing import Any, Union

from aiohttp import ClientSession
from packed import pack, unpack

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
            "id": str(handler.id),
            "request": handler.matcher,
            "response": handler.response,
        }
        binary = pack(payload)

        async with ClientSession() as session:
            async with session.post(self._url, data=binary, headers=headers) as response:
                assert response.status == OK, response
        return self

    async def deregister(self, handler: RemoteHandler) -> "RemoteMock":
        headers = {"x-jj-remote-mock": ""}
        payload = {
            "id": str(handler.id),
            "request": handler.matcher,
            "response": handler.response,
        }
        binary = pack(payload)

        async with ClientSession() as session:
            async with session.delete(self._url, data=binary, headers=headers) as response:
                assert response.status == OK, response
        return self

    async def history(self, handler: RemoteHandler) -> Any:
        headers = {"x-jj-remote-mock": ""}
        payload = {
            "id": str(handler.id),
            "request": handler.matcher,
            "response": handler.response,
        }
        binary = pack(payload)

        async with ClientSession() as session:
            async with session.get(self._url, data=binary, headers=headers) as response:
                assert response.status == OK, response
                body = await response.read()
                unpacked = unpack(body)
                return unpacked
