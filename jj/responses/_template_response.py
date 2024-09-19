from typing import Any, Dict

from packed import packable

from ._response import Response

__all__ = ("TemplateResponse",)


@packable("jj.responses.TemplateResponse")
class TemplateResponse(Response):
    def __init__(self) -> None:
        super().__init__()

    def copy(self) -> "TemplateResponse":
        assert not self.prepared
        return self.__class__()

    def __packed__(self) -> Dict[str, Any]:
        return {}

    @classmethod
    def __unpacked__(cls, **kwargs: Any) -> "TemplateResponse":
        return cls()
