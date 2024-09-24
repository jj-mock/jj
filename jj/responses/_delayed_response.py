import asyncio
import io
from http.cookies import Morsel
from json import dumps
from typing import Any, Dict, List, Optional, Tuple, Union
from unittest.mock import sentinel as nil

from aiohttp import web
from aiohttp.abc import AbstractStreamWriter
from aiohttp.typedefs import LooseHeaders
from aiohttp.web import ContentCoding
from aiohttp.web_request import BaseRequest
from multidict import CIMultiDict
from packed import packable

from ..http.headers import CONTENT_DISPOSITION, CONTENT_TYPE
from ._stream_response import StreamResponse
from ._utils import cookie_to_dict, get_response_body

__all__ = ("DelayedResponse",)


@packable("jj.responses.DelayedResponse")
class DelayedResponse(web.Response, StreamResponse):
    """
    Represents an HTTP response that can be delayed before sending.

    The `DelayedResponse` class is an extension of aiohttp's `web.Response`,
    allowing a delay to be added before the response is sent back to the client.
    This is useful for simulating latency or testing timeouts in a client-server architecture.
    """

    def __init__(self, *,
                 json: Any = nil,
                 body: Optional[Union[str, bytes]] = None,
                 text: Optional[str] = None,
                 status: int = 200,
                 reason: Optional[str] = None,
                 headers: Optional[LooseHeaders] = None,
                 delay: Optional[float] = None) -> None:
        """
        Initialize the DelayedResponse object.

        :param json: The JSON object to be used as the response body.
                     Overrides `body` and `text` if provided.
        :param body: The raw body content of the response as a string or bytes.
        :param text: The plain text content of the response.
        :param status: The HTTP status code for the response (default is 200).
        :param reason: The reason phrase for the response status code.
        :param headers: A dictionary or list of headers to include in the response.
        :param delay: The time in seconds to delay the response before sending (optional).
        """
        headers = CIMultiDict(headers or {})

        if json is not nil:
            assert (body is None) and (text is None)
            body = dumps(json)
            if CONTENT_TYPE not in headers:
                headers[CONTENT_TYPE] = "application/json"

        if (body is None) and (text is None):
            body = ""

        if isinstance(body, io.IOBase):
            if CONTENT_DISPOSITION not in headers:
                headers[CONTENT_DISPOSITION] = "inline"

        super().__init__(body=body, text=text, status=status, reason=reason, headers=headers)
        self._delay = delay  # seconds

    @property
    def content_coding(self) -> Optional[ContentCoding]:
        """
        Get the content encoding for the response.

        :return: The content encoding if compression is enabled, otherwise None.
        """
        return self._compression_force

    @property
    def delay(self) -> Union[float, None]:
        """
        Get the delay time for the response.

        :return: The delay time in seconds or None if no delay is set.
        """
        return self._delay

    def _cookie_to_dict(self, cookie: "Morsel[str]") -> Dict[str, Union[str, None]]:
        """
        Convert a Morsel cookie object to a dictionary.

        :param cookie: The Morsel object representing the cookie.
        :return: A dictionary representing the cookie's attributes.
        """
        return cookie_to_dict(cookie)

    def copy(self) -> "DelayedResponse":
        """
        Create a copy of the DelayedResponse object.

        This method clones the current response including its status, reason, headers,
        cookies, and compression settings, while ensuring the delay is preserved.

        :return: A new instance of the DelayedResponse object.
        :raises AssertionError: If the response is already prepared.
        """
        assert not self.prepared

        response = self.__class__(status=self.status, reason=self.reason, delay=self._delay,
                                  headers=self.headers, body=self.body)  # type: ignore
        for cookie in self.cookies.values():
            response.set_cookie(**cookie_to_dict(cookie))  # type: ignore
        if self.chunked:
            response.enable_chunked_encoding()
        if self._compression_force:
            response.enable_compression(self._compression_force)
        return response

    def get_body(self) -> bytes:
        """
        Get the body of the response.

        This method provides backward compatibility for retrieving the response body as bytes.

        :return: The response body as bytes.
        """
        return get_response_body(self.body)

    async def _prepare_hook(self, request: BaseRequest) -> "DelayedResponse":
        """
        Hook method to be executed before preparing the response.

        This method checks for a configured delay and if present, waits for the specified
        time before allowing the response to be prepared.

        :param request: The request object associated with the response.
        :return: The DelayedResponse object itself.
        """
        if self._delay:
            await asyncio.sleep(self._delay)
        return self

    async def prepare(self, request: BaseRequest) -> Optional[AbstractStreamWriter]:
        """
        Prepare the response for sending to the client.

        This method finalizes the response, taking into account any delay specified before
        sending the response to the client.

        :param request: The incoming HTTP request.
        :return: The stream writer used to send the response.
        """
        await self._prepare_hook(request)
        return await super().prepare(request)

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the DelayedResponse object into a dictionary for serialization.

        This method is used for converting the DelayedResponse object into a serializable
        format that can be transmitted or stored remotely.

        :return: A dictionary containing the packed response data.
        :raises AssertionError: If the response is already prepared.
        """
        assert not self.prepared

        headers = [[key, val] for key, val in self.headers.items()]
        cookies = [cookie_to_dict(cookie) for cookie in self.cookies.values()]

        body = get_response_body(self.body)

        compression: Optional[str] = None
        if isinstance(self._compression_force, ContentCoding):
            compression = self._compression_force.value
        else:
            compression = self._compression_force

        return {
            "status": self.status,
            "reason": self.reason,
            "headers": headers,
            "cookies": cookies,
            "body": body,
            "chunked": self.chunked,
            "compression": compression,
            "delay": self._delay,
        }

    @classmethod
    def __unpacked__(cls, *,
                     status: int,
                     reason: Optional[str],
                     headers: List[Tuple[str, str]],
                     cookies: List[Dict[str, Union[str, None]]],
                     body: Optional[bytes],
                     chunked: bool,
                     compression: Optional[ContentCoding],
                     delay: Optional[float],
                     **kwargs: Any) -> "DelayedResponse":
        """
        Reconstruct a DelayedResponse instance from unpacked parameters.

        :param status: The HTTP status code.
        :param reason: The reason phrase for the HTTP status.
        :param headers: A list of headers for the response.
        :param cookies: A list of cookie dictionaries.
        :param body: The response body as bytes.
        :param chunked: A flag indicating whether chunked encoding is enabled.
        :param compression: The content compression coding.
        :param delay: The delay in seconds before the response is sent.
        :param kwargs: Additional keyword arguments (ignored).
        :return: A new DelayedResponse object.
        """
        response = cls(status=status, reason=reason, headers=headers, body=body, delay=delay)
        for cookie in cookies:
            response.set_cookie(**cookie)  # type: ignore
        if compression:
            response.enable_compression(ContentCoding(compression))
        if chunked:
            response.enable_chunked_encoding()
        return response
