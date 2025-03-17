from typing import Any, Dict, List, Optional, Tuple, Union, cast
import json

from aiohttp.typedefs import LooseHeaders
from aiohttp.web_request import BaseRequest
from multidict import CIMultiDict
from packed import packable

from .._version import server_version

try:
    import jinja2
except ImportError:  # pragma: no cover
    jinja2 = None  # type: ignore


from ._response import Response

__all__ = ("TemplateResponse",)


@packable("jj.responses.TemplateResponse")
class TemplateResponse(Response):
    """
    Represents an HTTP response where the body, headers, and status can be templated.

    The `TemplateResponse` class extends the `Response` class and allows for the use
    of Jinja2 templates to dynamically render the response body, headers, and status
    based on the request context. It relies on Jinja2 as an optional dependency.
    """

    def __init__(self, body: Optional[str] = None, *,
                 headers: Optional[LooseHeaders] = None,
                 status: Union[int, str] = 200,
                 context: Union[Any, None] = None) -> None:
        """
        Initialize the TemplateResponse with optional templated body, headers, status, and context.

        :param body: The template string for the response body. Defaults to an empty string.
        :param headers: A dictionary of headers, which can also contain templates.
        :param status: The HTTP status code, which can be templated as well (default is 200).
        :param context: The additional context data to be used in template rendering.
        """
        super().__init__()
        self._tmpl_body = body or ""
        self._tmpl_headers = CIMultiDict(headers or {})
        self._tmpl_status = str(status)
        self._tmpl_context = context
        self._jinja_env: Any = None
        self._prepare_hook_called = False

    async def _prepare_hook(self, request: BaseRequest) -> "TemplateResponse":
        """
        Prepare the response by rendering the templates for body, headers, and status.

        This method is called before sending the response to the client. It renders
        the templated body, headers, and status code using the request and context data.

        :param request: The incoming HTTP request object used for rendering templates.
        :return: The `TemplateResponse` object after template rendering is complete.
        :raises ImportError: If Jinja2 is not installed.
        """
        if self._prepare_hook_called:
            return self

        if jinja2 is None:  # pragma: no cover
            raise ImportError(
                "Jinja2 is an optional dependency. "
                "To use TemplateResponse, please install Jinja2 via 'pip install jinja2'"
            )
        self._jinja_env = jinja2.environment.Environment()
        # 'tojson' is a default filter provided by Jinja2
        self._jinja_env.filters["fromjson"] = json.loads

        context = {
            "request": request,
            "context": self._tmpl_context,
        }

        self._headers = CIMultiDict({
            "Server": self._tmpl_headers.get("Server", server_version)
        })
        self._headers.extend(
            (self._render_value(key, context), self._render_value(value, context))
            for key, value in self._tmpl_headers.items()
            if key.lower() != "server"
        )
        self.body = self._render_value(self._tmpl_body, context)  # type: ignore
        self.set_status(int(self._render_value(self._tmpl_status, context)))

        self._prepare_hook_called = True
        return self

    def _render_value(self, value: str, context: Dict[str, Any]) -> str:
        """
        Render a single template value using the request and context data.

        This method renders a given string value as a Jinja2 template, passing the
        request and additional context into the template rendering.

        :param value: The string value to be rendered as a template.
        :param context: The dictionary containing request and additional context data.
        :return: The rendered template as a string.
        """
        template = self._jinja_env.from_string(value)
        rendered = template.render(context)
        return cast(str, rendered)

    def copy(self) -> "TemplateResponse":
        """
        Create a copy of the TemplateResponse object.

        :return: A new instance of `TemplateResponse` with the same template configuration.
        :raises AssertionError: If the response is already prepared.
        """
        assert not self.prepared
        return self.__class__.__unpacked__(**self.__packed__())

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the TemplateResponse into a dictionary for serialization.

        This method prepares the response for serialization by packing its templated
        body, headers, status, and context into a dictionary.

        :return: A dictionary representing the packed TemplateResponse.
        """
        return {
            "body": self._tmpl_body,
            "headers": [
                [key, val] for key, val in self._tmpl_headers.items()
            ],
            "status": self._tmpl_status,
            "context": self._tmpl_context,
        }

    @classmethod
    def __unpacked__(cls, *,  # type: ignore
                     body: str,
                     headers: List[Tuple[str, str]],
                     status: Union[int, str],
                     context: Optional[Any] = None,
                     **kwargs: Any) -> "TemplateResponse":
        """
        Reconstruct a TemplateResponse instance from unpacked parameters.

        :param body: The template string for the response body.
        :param headers: A list of headers, each represented as a tuple of (key, value).
        :param status: The HTTP status code as a string or integer.
        :param context: The additional context data to be used in template rendering.
        :param kwargs: Additional keyword arguments (ignored).
        :return: A new instance of `TemplateResponse`.
        """
        return cls(status=status, headers=headers, body=body, context=context)
