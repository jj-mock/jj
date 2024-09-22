from typing import Any, Dict, List, Optional, Tuple, Union

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
    def __init__(self, body: Optional[str] = None, *,
                 headers: Optional[LooseHeaders] = None,
                 status: Union[int, str] = 200) -> None:
        super().__init__()

        self._tmpl_body = body or ""
        self._tmpl_headers = CIMultiDict(headers or {})
        self._tmpl_status = str(status)
        self._prepare_hook_called = False

        if jinja2 is None:  # pragma: no cover
            raise ImportError(
                "Jinja2 is an optional dependency. "
                "To use TemplateResponse, please install Jinja2 via 'pip install jinja2'"
            )
        self._jinja_env = jinja2.environment.Environment()

    async def _prepare_hook(self, request: BaseRequest) -> "TemplateResponse":
        if self._prepare_hook_called:
            return self

        self._headers = CIMultiDict({
            "Server": self._tmpl_headers.get("Server", server_version)
        })
        self._headers.extend(
            (self._render_value(key, request), self._render_value(value, request))
            for key, value in self._tmpl_headers.items()
            if key.lower() != "server"
        )
        self.body = self._render_value(self._tmpl_body, request)  # type: ignore
        self.set_status(int(self._render_value(self._tmpl_status, request)))

        self._prepare_hook_called = True
        return self

    def _render_value(self, value: str, request: BaseRequest) -> str:
        template = self._jinja_env.from_string(value)
        return template.render({"request": request})

    def copy(self) -> "TemplateResponse":
        assert not self.prepared
        return self.__class__.__unpacked__(**self.__packed__())

    def __packed__(self) -> Dict[str, Any]:
        return {
            "body": self._tmpl_body,
            "headers": [
                [key, val] for key, val in self._tmpl_headers.items()
            ],
            "status": self._tmpl_status,
        }

    @classmethod
    def __unpacked__(cls, *,  # type: ignore
                     body: str,
                     headers: List[Tuple[str, str]],
                     status: Union[int, str],
                     **kwargs: Any) -> "TemplateResponse":
        return cls(status=status, headers=headers, body=body)
