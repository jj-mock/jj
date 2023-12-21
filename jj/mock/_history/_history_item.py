from typing import List, TypedDict

from ._history_request import HistoryRequest
from ._history_response import HistoryResponse

__all__ = ("HistoryItem",)


class HistoryItem(TypedDict):
    request: HistoryRequest
    response: HistoryResponse
    tags: List[str]
