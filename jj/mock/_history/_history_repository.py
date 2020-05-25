from typing import Any, Dict, List, Optional

from ...requests import Request
from ...responses import Response
from ._history_request import HistoryRequest
from ._history_response import HistoryResponse

__all__ = ("HistoryRepository",)


class HistoryRepository:
    def __init__(self) -> None:
        self._storage: List[Dict[str, Any]] = []

    async def add(self,
                  request: Request,
                  response: Response,
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

    async def get_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        return [x for x in self._storage if tag in x["tags"]]
