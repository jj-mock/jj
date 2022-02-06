import json
from typing import Any

from jj.http.headers import CONTENT_TYPE

from ._history_item import HistoryItem
from ._history_request import HistoryRequest
from ._history_response import HistoryResponse

__all__ = ("BodyParser",)


class BodyParser:
    def _parse_by_content_type(self, content_type: str, body: bytes) -> Any:
        if content_type.lower().startswith("application/json"):
            try:
                return json.loads(body)
            except:  # noqa: E722
                pass
        elif content_type.lower().startswith("text/plain"):
            try:
                return body.decode()
            except:  # noqa: E722
                pass
        return body

    def _parse_request_body(self, request: HistoryRequest) -> Any:
        content_type = request.headers.get(CONTENT_TYPE, "")
        return self._parse_by_content_type(content_type, request.body)

    def _parse_response_body(self, response: HistoryResponse) -> Any:
        content_type = response.headers.get(CONTENT_TYPE, "")
        return self._parse_by_content_type(content_type, response.body)

    def parse(self, history_item: HistoryItem) -> HistoryItem:
        request = history_item["request"].to_dict()
        request["body"] = self._parse_request_body(history_item["request"])
        history_item["request"] = history_item["request"].from_dict(request)

        response = history_item["response"].to_dict()
        response["body"] = self._parse_response_body(history_item["response"])
        history_item["response"] = history_item["response"].from_dict(response)

        return history_item
