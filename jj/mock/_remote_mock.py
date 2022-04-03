from typing import List, Optional, Union, cast

from aiohttp import ClientSession
from packed import pack, unpack

from jj import version
from jj.expiration_policy import ExpirationPolicy
from jj.http.codes import OK
from jj.matchers import LogicalMatcher, RequestMatcher

from ._history import HistoryAdapterType, HistoryItem, default_history_adapter
from ._remote_handler import RemoteHandler
from ._remote_response import RemoteResponseType

__all__ = ("RemoteMock",)


class RemoteMock:
    def __init__(self, url: str) -> None:
        self._url = url

    def create_handler(self,
                       matcher: Union[RequestMatcher, LogicalMatcher],
                       response: RemoteResponseType,
                       expiration_policy: Optional[ExpirationPolicy] = None,
                       *,
                       history_adapter: Optional[HistoryAdapterType] = default_history_adapter
                       ) -> RemoteHandler:
        return RemoteHandler(
            self,
            matcher,
            response,
            expiration_policy=expiration_policy,
            history_adapter=history_adapter,
        )

    def _pack_payload(self, handler: RemoteHandler) -> bytes:
        payload = {
            "id": str(handler.id),
            "request": handler.matcher,
            "response": handler.response,
            "expiration_policy": handler.expiration_policy,
        }
        return pack(payload)

    async def register(self, handler: RemoteHandler) -> "RemoteMock":
        url = f"{self._url}/__jj__/register"
        headers = {"x-jj-remote-mock": f"v{version}"}
        binary = self._pack_payload(handler)

        async with ClientSession() as session:
            async with session.post(url, data=binary, headers=headers) as response:
                assert response.status == OK, response
        return self

    async def deregister(self, handler: RemoteHandler) -> "RemoteMock":
        url = f"{self._url}/__jj__/deregister"
        headers = {"x-jj-remote-mock": f"v{version}"}
        binary = self._pack_payload(handler)

        async with ClientSession() as session:
            async with session.delete(url, data=binary, headers=headers) as response:
                assert response.status == OK, response
        return self

    async def fetch_history(self, handler: RemoteHandler) -> List[HistoryItem]:
        url = f"{self._url}/__jj__/history"
        headers = {"x-jj-remote-mock": f"v{version}"}
        binary = self._pack_payload(handler)

        async with ClientSession() as session:
            async with session.get(url, data=binary, headers=headers) as response:
                assert response.status == OK, response
                body = await response.read()

        unpacked = unpack(body)
        return cast(List[HistoryItem], unpacked)
