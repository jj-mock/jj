from typing import Any, Dict

from aiohttp.web_request import BaseRequest
from multidict import CIMultiDict
from packed import packable

try:
    import jinja2
except ImportError:  # pragma: no cover
    jinja2 = None  # type: ignore


from ._response import Response

__all__ = ("TemplateResponse",)


@packable("jj.responses.TemplateResponse")
class TemplateResponse(Response):
    def __init__(self, template: str) -> None:
        super().__init__()
        self._template = template
        self._prepare_hook_called = False

        if jinja2 is None:
            raise ImportError(
                "Jinja2 is an optional dependency. "
                "To use TemplateResponse, please install Jinja2 via 'pip install jinja2'"
            )
        self._jinja_env = jinja2.environment.Environment()

    async def _prepare_hook(self, request: BaseRequest) -> "TemplateResponse":
        if self._prepare_hook_called:
            return self
        self.set_status(status=200, reason="OK")
        self._headers = CIMultiDict({})

        template = self._jinja_env.from_string(self._template)
        rendered = template.render({"request": request})
        self.body = rendered.encode("utf-8")

        self._prepare_hook_called = True
        return self

    def copy(self) -> "TemplateResponse":
        assert not self.prepared
        return self.__class__(template=self._template)

    def __packed__(self) -> Dict[str, Any]:
        return {"template": self._template}

    @classmethod
    def __unpacked__(cls, *, template: str, **kwargs: Any) -> "TemplateResponse":  # type: ignore
        return cls(template=template)
