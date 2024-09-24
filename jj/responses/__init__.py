import mimetypes

from ._delayed_response import DelayedResponse
from ._relay_response import RelayResponse
from ._response import Response
from ._static_response import StaticResponse
from ._stream_response import StreamResponse
from ._template_response import TemplateResponse

__all__ = ("Response", "StaticResponse", "StreamResponse", "RelayResponse",
           "DelayedResponse", "TemplateResponse",)


mimetypes.add_type("application/json", ".json")
