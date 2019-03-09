from pathlib import Path
from typing import Optional, Union, MutableMapping

from aiohttp import web

from ._stream_response import StreamResponse


__all__ = ("StaticResponse",)


class StaticResponse(web.FileResponse, StreamResponse):
    def __init__(self, path: Union[str, Path], *,
                 chunk_size: int = 256 * 1024,
                 status: int = 200,
                 reason: Optional[str] = None,
                 headers: MutableMapping[str, str] = None) -> None:
        super().__init__(path, chunk_size, status, reason, headers)
