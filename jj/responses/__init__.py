import mimetypes

from ._relay_response import RelayResponse
from ._response import Response
from ._static_response import StaticResponse
from ._stream_response import StreamResponse

__all__ = ("Response", "StaticResponse", "StreamResponse", "RelayResponse")


mimetypes.add_type("application/json", ".json")
