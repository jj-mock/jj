from typing import Any, Dict, Tuple
from urllib.parse import urljoin

from aiohttp import ClientSession
from aiohttp.web_request import BaseRequest
from multidict import CIMultiDict, CIMultiDictProxy, MultiMapping
from packed import packable

from ._response import Response

__all__ = ("RelayResponse",)


# http://tools.ietf.org/html/rfc2616#section-13.5.1
_HOP_BY_HOP_HEADERS = (
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade")

_FILTERED_HEADERS = _HOP_BY_HOP_HEADERS + ("host", "content-length")

_TargetResponseType = Tuple[int, Any, CIMultiDictProxy[str], bytes]


@packable("jj.responses.RelayResponse")
class RelayResponse(Response):
    """
    Relays the request to a target server and returns the response.

    The `RelayResponse` class is a special kind of response that forwards incoming
    requests to a target server, retrieves the response from the target, and relays
    it back to the client.
    """

    def __init__(self, *, target: str) -> None:
        """
        Initialize the RelayResponse with a target URL.

        :param target: The base URL of the target server to which the request will be relayed.
        """
        super().__init__()
        self._target = target
        self._prepare_hook_called = False

    @property
    def target(self) -> str:
        """
        Get the target URL for the relayed request.

        :return: The base URL of the target server.
        """
        return self._target

    def _filter_headers(self, headers: MultiMapping[str]) -> CIMultiDict[str]:
        """
        Filter headers to exclude hop-by-hop and other headers not forwarded.

        This method removes headers that should not be forwarded to the target server,
        such as hop-by-hop headers (per RFC 2616, Section 13.5.1) and certain others
        like `host` and `content-length`.

        :param headers: The original headers of the incoming request.
        :return: A new `CIMultiDict` containing only the headers that should be forwarded.
        """
        filtered: CIMultiDict[str] = CIMultiDict()
        for key, value in headers.items():
            if key.lower() not in _FILTERED_HEADERS:
                filtered[key] = value
        return filtered

    async def _do_target_request(self, request: BaseRequest) -> _TargetResponseType:
        """
        Perform the request to the target server and retrieve the response.

        This method constructs a new request based on the incoming request, forwards it to
        the target server, and retrieves the response. It also handles reading the response
        body and returning necessary response details.

        :param request: The incoming client request to be relayed.
        :return: A tuple containing the status code, reason, filtered headers,
                 and the body of the target response.
        """
        url = urljoin(self._target, request.path)
        headers = self._filter_headers(request.headers)

        data = await request.read()

        async with ClientSession(auto_decompress=False) as session:
            async with session.request(request.method, url, params=request.query, headers=headers,
                                       data=data, allow_redirects=True) as response:
                body = await response.read()
        return response.status, response.reason, response.headers, body

    async def _prepare_hook(self, request: BaseRequest) -> "RelayResponse":
        """
        Prepare the relay response by performing the request to the target server.

        This method is called during the response preparation phase and ensures that
        the request is sent to the target server. It also processes the response from
        the target, including setting the appropriate status, headers, and body.

        :param request: The incoming request to be relayed.
        :return: The `RelayResponse` object after the target request is processed.
        """
        if self._prepare_hook_called:
            return self
        status, reason, headers, body = await self._do_target_request(request)
        self.set_status(status, reason)
        self._headers = CIMultiDict(self._filter_headers(headers))
        self.body = body
        self._prepare_hook_called = True
        return self

    def copy(self) -> "RelayResponse":
        """
        Create a copy of the RelayResponse object.

        This method clones the current `RelayResponse` object, ensuring that the target URL
        is preserved.

        :return: A new instance of `RelayResponse` with the same target URL.
        :raises AssertionError: If the response is already prepared.
        """
        assert not self.prepared
        return self.__class__(target=self._target)

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the RelayResponse object for serialization.

        This method packs the target URL into a dictionary, which can then be used for
        serialization or transmission.

        :return: A dictionary containing the target URL.
        """
        return {"target": self._target}

    @classmethod
    def __unpacked__(cls, *, target: str, **kwargs: Any) -> "RelayResponse":  # type: ignore
        """
        Reconstruct a RelayResponse instance from unpacked parameters.

        :param target: The target URL to relay requests to.
        :param kwargs: Additional keyword arguments (ignored).
        :return: A new `RelayResponse` instance with the specified target.
        """
        return cls(target=target)
