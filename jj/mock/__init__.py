import os
from distutils.util import strtobool
from typing import Optional, Union

from jj.expiration_policy import ExpirationPolicyType, ExpireNever
from jj.matchers import LogicalMatcher, RequestMatcher

from ._history import (
    HistoryAdapterType,
    HistoryItem,
    HistoryRepository,
    HistoryRequest,
    HistoryResponse,
    default_history_adapter,
)
from ._mock import Mock
from ._mocked import Mocked
from ._remote_handler import RemoteHandler
from ._remote_mock import RemoteMock
from ._remote_response import RemoteResponseType
from ._system_log_filter import SystemLogFilter

_REMOTE_MOCK_URL = os.environ.get("JJ_REMOTE_MOCK_URL", "http://localhost:8080")
_REMOTE_MOCK_DISPOSABLE = os.environ.get("JJ_REMOTE_MOCK_DISPOSABLE", "True")


def mocked(matcher: Union[RequestMatcher, LogicalMatcher],
           response: RemoteResponseType,
           expiration_policy: Optional[ExpirationPolicyType] = None,
           *,
           disposable: Optional[bool] = None,
           prefetch_history: bool = True,
           history_adapter: Optional[HistoryAdapterType] = default_history_adapter,
           ) -> "Mocked":
    if disposable is None:
        disposable = strtobool(_REMOTE_MOCK_DISPOSABLE)

    if expiration_policy is None:
        expiration_policy = ExpireNever()

    handler = RemoteMock(_REMOTE_MOCK_URL).create_handler(
        matcher,
        response,
        expiration_policy,
        history_adapter=history_adapter
    )
    return Mocked(handler, disposable=disposable, prefetch_history=prefetch_history)


__all__ = ("Mock", "mocked", "RemoteMock", "RemoteHandler", "Mocked",
           "HistoryRepository", "HistoryRequest", "HistoryResponse", "HistoryItem",
           "SystemLogFilter", "RemoteResponseType", "HistoryAdapterType",
           "default_history_adapter",)
