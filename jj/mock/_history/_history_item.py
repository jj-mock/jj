import sys

__all__ = ("HistoryItem",)


if sys.version_info >= (3, 8):
    from typing import List, TypedDict

    from ._history_request import HistoryRequest
    from ._history_response import HistoryResponse

    class HistoryItem(TypedDict):
        request: HistoryRequest
        response: HistoryResponse
        tags: List[str]
else:
    from typing import Any, Dict
    HistoryItem = Dict[str, Any]
