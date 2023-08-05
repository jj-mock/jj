import os
from typing import Optional, Union

from jj.expiration_policy import ExpirationPolicy
from jj.matchers import LogicalMatcher, RequestMatcher

from ._history import (
    HistoryAdapterType,
    HistoryFormatter,
    HistoryItem,
    HistoryRepository,
    HistoryRequest,
    HistoryResponse,
    PrettyHistoryFormatter,
    default_history_adapter,
)
from ._mock import Mock
from ._mocked import Mocked
from ._remote_handler import RemoteHandler
from ._remote_mock import RemoteMock
from ._remote_response import RemoteResponseType
from ._stacked import stacked

REMOTE_MOCK_URL = os.environ.get("JJ_REMOTE_MOCK_URL", "http://localhost:8080")
REMOTE_MOCK_DISPOSABLE = os.environ.get("JJ_REMOTE_MOCK_DISPOSABLE", "True")

REMOTE_MOCK_PPRINT = os.environ.get("JJ_REMOTE_MOCK_PPRINT", "False")
REMOTE_MOCK_PPRINT_LENGTH = os.environ.get("JJ_REMOTE_MOCK_PPRINT_LENGTH", "")
REMOTE_MOCK_PPRINT_WIDTH = os.environ.get("JJ_REMOTE_MOCK_PPRINT_WIDTH", "")

# backward compatibility
_REMOTE_MOCK_URL = REMOTE_MOCK_URL
_REMOTE_MOCK_DISPOSABLE = REMOTE_MOCK_DISPOSABLE


def mocked(matcher: Union[RequestMatcher, LogicalMatcher],
           response: RemoteResponseType,
           expiration_policy: Optional[ExpirationPolicy] = None,
           *,
           disposable: Optional[bool] = None,
           prefetch_history: bool = True,
           history_formatter: Optional[HistoryFormatter] = None,
           history_adapter: Optional[HistoryAdapterType] = default_history_adapter) -> "Mocked":
    if disposable is None:
        disposable = True if REMOTE_MOCK_DISPOSABLE.lower() == 'true' else False

    if (history_formatter is None) and (REMOTE_MOCK_PPRINT.lower() == 'true'):
        _history_width = int(REMOTE_MOCK_PPRINT_WIDTH) if REMOTE_MOCK_PPRINT_WIDTH else None
        _history_length = int(REMOTE_MOCK_PPRINT_LENGTH) if REMOTE_MOCK_PPRINT_LENGTH else None
        history_formatter = PrettyHistoryFormatter(_history_width, _history_length)

    handler = create_remote_handler(
        matcher, response, expiration_policy, history_adapter=history_adapter
    )

    return Mocked(handler, disposable=disposable, prefetch_history=prefetch_history,
                  history_formatter=history_formatter)


def create_remote_handler(matcher: Union[RequestMatcher, LogicalMatcher],
                          response: RemoteResponseType,
                          expiration_policy: Optional[ExpirationPolicy] = None,
                          *,
                          mock_url: str = REMOTE_MOCK_URL,
                          history_adapter: Optional[HistoryAdapterType] = default_history_adapter
                          ) -> RemoteHandler:
    return RemoteMock(mock_url).create_handler(matcher, response, expiration_policy,
                                               history_adapter=history_adapter)


__all__ = ("Mock", "mocked", "stacked", "create_remote_handler", "RemoteMock", "RemoteHandler",
           "Mocked", "HistoryRepository", "HistoryRequest", "HistoryResponse", "HistoryItem",
           "SystemLogFilter", "RemoteResponseType", "HistoryAdapterType",
           "default_history_adapter", "REMOTE_MOCK_URL", "REMOTE_MOCK_DISPOSABLE",)
