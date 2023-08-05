from typing import List, Optional

from ...requests import Request
from ...responses import StreamResponse
from ._history_item import HistoryItem
from ._history_request import HistoryRequest
from ._history_response import HistoryResponse

__all__ = ("HistoryRepository",)


class HistoryRepository:
    def __init__(self) -> None:
        self._storage: List[HistoryItem] = []

    async def add(self,
                  request: Request,
                  response: StreamResponse,
                  tags: Optional[List[str]] = None) -> None:
        req = await HistoryRequest.from_request(request)
        res = await HistoryResponse.from_response(response)
        self._storage.insert(0, {
            "request": req,
            "response": res,
            "tags": tags or [],
        })

    async def delete_by_tag(self, tag: str) -> None:
        self._storage = [x for x in self._storage if tag not in x["tags"]]

    async def get_by_tag(self, tag: str) -> List[HistoryItem]:
        return [x for x in self._storage if tag in x["tags"]]

    async def clear(self) -> None:
        self._storage.clear()
