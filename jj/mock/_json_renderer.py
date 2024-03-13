import json
from typing import Any, List, Optional, TypedDict, Union, cast

from jj import DelayedResponse, RelayResponse, Response
from jj.expiration_policy import ExpirationPolicy
from jj.matchers import LogicalMatcher, RequestMatcher
from jj.mock import HistoryItem

from ._history import BodyParser

__all__ = ("JsonRenderer", "Handler",)


class Handler(TypedDict):
    id: str
    expiration_policy: Union[ExpirationPolicy, None]
    matcher: Union[RequestMatcher, LogicalMatcher]
    response: Union[Response, RelayResponse, DelayedResponse]

    history_url: str


class JsonRenderer:
    def __init__(self, body_parser: Optional[BodyParser] = None) -> None:
        self._body_parser = body_parser or BodyParser()

    def render_handlers(self, handlers: List[Handler]) -> str:
        result = []
        for handler in handlers:
            result.append({
                "id": handler["id"],
                "expiration_policy": self._pack(handler["expiration_policy"]),
                "matcher": self._pack(handler["matcher"]),
                "response": self._pack_response(handler["response"]),
                "history": {
                    "url": handler["history_url"],
                },
            })
        return self._to_json(result)

    def render_history(self, history_items: List[HistoryItem]) -> str:
        result = []
        for item in history_items:
            item = self._body_parser.parse(item)
            result.append({
                "request": self._pack(item["request"]),
                "response": self._pack(item["response"]),
            })
        return self._to_json(result)

    def _pack_response(self, response: Union[Response, RelayResponse, DelayedResponse]) -> Any:
        packed = self._pack(response)
        if isinstance(response, (Response, DelayedResponse)):
            cls_name = response.__class__.__name__
            body = self._body_parser._parse_by_content_type(response.content_type,
                                                            cast(bytes, response.body))
            packed[cls_name]["body"] = body
        return packed

    def _pack(self, value: Any) -> Any:
        if hasattr(value, "__packed__"):
            return {value.__class__.__name__: self._pack(value.__packed__())}
        elif isinstance(value, dict):
            return {k: self._pack(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [self._pack(v) for v in value]
        else:
            return value

    def _to_json(self, value: Any) -> str:
        return json.dumps(value, default=str, ensure_ascii=False, indent=4)
