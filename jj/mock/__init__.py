import os
from distutils.util import strtobool
from typing import Optional, Union

from jj.matchers import LogicalMatcher, RequestMatcher

from ._history import HistoryItem, HistoryRepository, HistoryRequest, HistoryResponse
from ._mock import Mock
from ._mocked import HistoryAdapterType, Mocked
from ._remote_handler import RemoteHandler
from ._remote_mock import RemoteMock
from ._remote_response import RemoteResponseType
from ._system_log_filter import SystemLogFilter

_REMOTE_MOCK_URL = os.environ.get("JJ_REMOTE_MOCK_URL", "http://localhost:8080")
_REMOTE_MOCK_DISPOSABLE = os.environ.get("JJ_REMOTE_MOCK_DISPOSABLE", "True")


def mocked(matcher: Union[RequestMatcher, LogicalMatcher], response: RemoteResponseType, *,
           disposable: Optional[bool] = None,
           prefetch_history: bool = True,
           history_adapter: Optional[HistoryAdapterType] = None) -> "Mocked":
    if disposable is None:
        disposable = strtobool(_REMOTE_MOCK_DISPOSABLE)
    handler = RemoteMock(_REMOTE_MOCK_URL).create_handler(matcher, response)
    return Mocked(handler,
                  disposable=disposable,
                  prefetch_history=prefetch_history,
                  history_adapter=history_adapter)


__all__ = ("Mock", "mocked", "RemoteMock", "RemoteHandler", "Mocked",
           "HistoryRepository", "HistoryRequest", "HistoryResponse", "HistoryItem",
           "SystemLogFilter", "RemoteResponseType",)
