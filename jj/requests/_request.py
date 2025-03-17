import json
from typing import Any, Dict, Optional, Union

from aiohttp import web
from aiohttp.web_request import FileField
from multidict import MultiDictProxy, MultiMapping

from ..responses import StreamResponse

__all__ = ("Request",)


class Request(web.Request):
    """
    Extends aiohttp's `web.Request` to add support for URL path segments and custom parameters.

    This class enhances the base `web.Request` by adding a `segments` attribute for handling
    dynamic URL path segments and provides a shorthand property for accessing query parameters.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the Request object.

        :param args: Positional arguments to pass to the base `web.Request`.
        :param kwargs: Keyword arguments to pass to the base `web.Request`.
        """
        super().__init__(*args, **kwargs)
        self._segments: Optional[Dict[str, str]] = None

    @property
    def params(self) -> "MultiMapping[str]":
        """
        Get the query parameters of the request.

        This is a shorthand property that returns the same result as `self.query`.

        :return: A `MultiMapping` object containing the query parameters.
        """
        return self.query

    @property
    def segments(self) -> Dict[str, str]:
        """
        Get the URL path segments.

        This property holds dynamic URL segments that can be set and retrieved for the request.
        If no segments are set, an empty dictionary is returned.

        :return: A dictionary containing the path segments of the request,
                 or an empty dictionary if not set.
        """
        if self._segments is None:
            return {}
        return self._segments

    @segments.setter
    def segments(self, segments: Optional[Dict[str, str]]) -> None:
        """
        Set the URL path segments.

        This allows setting a dictionary of path segments for the request. Path segments
        are often used when dealing with dynamic URL paths that contain variable placeholders.

        :param segments: A dictionary of path segments, or `None` to reset the segments.
        """
        self._segments = segments

    @property
    def raw_data(self) -> Union[bytes, None]:
        """
        Get the raw request body as bytes.

        :return: The raw request body as bytes, or `None` if not available.
        """
        return self._read_bytes

    @property
    def post_data(self) -> Union[MultiDictProxy[Union[str, bytes, FileField]], None]:
        """
        Get the parsed form data from the request.

        This property provides access to the form-encoded body of the request if available.

        :return: A `MultiDictProxy` containing the form data, or `None` if not available.
        """
        return self._post

    @property
    def json_data(self) -> Union[Any, None]:
        """
        Get the request body as a parsed JSON object.

        This property decodes the request body using the specified charset (defaulting to UTF-8)
        and parses it as JSON.

        :return: The parsed JSON data, or `None` if the request body is empty.
        :raises json.JSONDecodeError: If the request body is not valid JSON.
        """
        if self._read_bytes is None:
            return None
        encoding = self.charset or "utf-8"
        return json.loads(self._read_bytes.decode(encoding))

    async def _prepare_hook(self, response: StreamResponse) -> None:  # type: ignore
        """
        Prepare the request before it is processed by the server.

        This hook method can be used to perform any custom preparation or pre-processing
        on the request object before it is sent for handling.

        :param response: The response object associated with the request.
        """
        pass
