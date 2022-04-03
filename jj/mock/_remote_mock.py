from typing import List, Optional, Tuple, Union, cast

from aiohttp import ClientSession
from packed import pack, unpack

from jj import version
from jj.expiration_policy import ExpirationPolicy
from jj.http.codes import OK
from jj.http.methods import DELETE, GET, POST
from jj.matchers import LogicalMatcher, RequestMatcher

from ._history import HistoryAdapterType, HistoryItem, default_history_adapter
from ._remote_handler import RemoteHandler
from ._remote_response import RemoteResponseType

__all__ = ("RemoteMock",)


class _RemoteMockError(Exception):
    pass


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

    async def _do_request(self, method: str, url: str, data: bytes) -> Tuple[int, bytes]:
        headers = {"x-jj-remote-mock": f"v{version}"}
        async with ClientSession() as session:
            async with session.request(method, url, data=data, headers=headers) as response:
                body = await response.read()
                return response.status, body

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
        status, body = await self._do_request(POST, url, self._pack_payload(handler))
        if status != OK:
            raise _RemoteMockError(f"Can't register mock ({body!r})")
        return self

    async def deregister(self, handler: RemoteHandler) -> "RemoteMock":
        url = f"{self._url}/__jj__/deregister"
        status, body = await self._do_request(DELETE, url, self._pack_payload(handler))
        if status != OK:
            raise _RemoteMockError(f"Can't deregister mock ({body!r})")
        return self

    async def fetch_history(self, handler: RemoteHandler) -> List[HistoryItem]:
        url = f"{self._url}/__jj__/history"
        status, body = await self._do_request(GET, url, self._pack_payload(handler))
        if status != OK:
            raise _RemoteMockError(f"Can't retrieve mock history ({body!r})")
        return cast(List[HistoryItem], unpack(body))
