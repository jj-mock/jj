import mimetypes

from ._response import Response
from ._static_response import StaticResponse
from ._stream_response import StreamResponse
from ._tunnel_response import TunnelResponse


__all__ = ("Response", "StaticResponse", "StreamResponse", "TunnelResponse")


mimetypes.add_type("application/json", ".json")
