import os
from distutils.util import strtobool
from typing import Optional, Union

from jj.expiration_policy import ExpirationPolicy
from jj.matchers import LogicalMatcher, RequestMatcher

from ._history import (
    HistoryAdapterType,
    HistoryItem,
    HistoryRepository,
    HistoryRepr,
    HistoryRequest,
    HistoryResponse,
    default_history_adapter,
    default_history_repr,
)
from ._mock import Mock
from ._mocked import Mocked
from ._remote_handler import RemoteHandler
from ._remote_mock import RemoteMock
from ._remote_response import RemoteResponseType
from ._stacked import stacked
from ._system_log_filter import SystemLogFilter

REMOTE_MOCK_URL = os.environ.get("JJ_REMOTE_MOCK_URL", "http://localhost:8080")
REMOTE_MOCK_DISPOSABLE = os.environ.get("JJ_REMOTE_MOCK_DISPOSABLE", "True")

# backward compatibility
_REMOTE_MOCK_URL = REMOTE_MOCK_URL
_REMOTE_MOCK_DISPOSABLE = REMOTE_MOCK_DISPOSABLE


def mocked(matcher: Union[RequestMatcher, LogicalMatcher],
           response: RemoteResponseType,
           expiration_policy: Optional[ExpirationPolicy] = None,
           *,
           disposable: Optional[bool] = None,
           prefetch_history: bool = True,
           history_repr: Optional[HistoryRepr] = default_history_repr,
           history_adapter: Optional[HistoryAdapterType] = default_history_adapter) -> "Mocked":
    if disposable is None:
        disposable = bool(strtobool(REMOTE_MOCK_DISPOSABLE))

    handler = create_remote_handler(
        matcher, response, expiration_policy, history_adapter=history_adapter
    )
    return Mocked(handler, disposable=disposable, prefetch_history=prefetch_history,
                  history_repr=history_repr)


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
           "HistoryRepr", "SystemLogFilter", "RemoteResponseType", "HistoryAdapterType",
           "default_history_adapter", "default_history_repr", "REMOTE_MOCK_URL",
           "REMOTE_MOCK_DISPOSABLE")
