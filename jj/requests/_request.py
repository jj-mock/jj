from typing import Optional, Dict, Any

from aiohttp import web
from multidict import MultiDictProxy

from ..responses import StreamResponse


__all__ = ("Request",)


class Request(web.Request):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._segments: Optional[Dict[str, str]] = None

    @property
    def params(self) -> "MultiDictProxy[str]":
        return self.query

    @property
    def segments(self) -> Dict[str, str]:
        if self._segments is None:
            return {}
        return self._segments

    @segments.setter
    def segments(self, segments: Optional[Dict[str, str]]) -> None:
        self._segments = segments

    async def _prepare_hook(self, response: StreamResponse) -> None:  # type: ignore
        pass
