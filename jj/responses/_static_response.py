from pathlib import Path
from typing import Union, Optional, MutableMapping

from aiohttp import web

from ._stream_response import StreamResponse


__all__ = ("StaticResponse",)


class StaticResponse(web.FileResponse, StreamResponse):
    def __init__(self, path: Union[str, Path], *,
                 chunk_size: int = 256 * 1024,
                 attachment: Union[bool, str] = False,
                 headers: Optional[MutableMapping[str, str]] = None) -> None:
        headers = headers or {}

        if isinstance(attachment, str):
            headers["Content-Disposition"] = "attachment; filename=\"{}\"".format(attachment)
        elif attachment is not False:
            headers["Content-Disposition"] = "attachment"

        super().__init__(path, chunk_size, headers=headers)
