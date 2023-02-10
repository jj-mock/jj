import os
from distutils.util import strtobool
from typing import Optional, Union

from jj.expiration_policy import ExpirationPolicy
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
from ._stacked import stacked
from ._system_log_filter import SystemLogFilter

REMOTE_MOCK_URL = os.environ.get("JJ_REMOTE_MOCK_URL", "http://localhost:8080")
REMOTE_MOCK_DISPOSABLE = os.environ.get("JJ_REMOTE_MOCK_DISPOSABLE", "True")
REMOTE_MOCK_PPRINT = os.environ.get("JJ_REMOTE_MOCK_PPRINT", "True")
REMOTE_MOCK_PPRINT_LIMIT = os.environ.get("JJ_REMOTE_MOCK_PPRINT_LIMIT", 1000000)
REMOTE_MOCK_PPRINT_WIDTH = os.environ.get("JJ_REMOTE_MOCK_PPRINT_WIDTH")

# backward compatibility
_REMOTE_MOCK_URL = REMOTE_MOCK_URL
_REMOTE_MOCK_DISPOSABLE = REMOTE_MOCK_DISPOSABLE


def mocked(matcher: Union[RequestMatcher, LogicalMatcher],
           response: RemoteResponseType,
           expiration_policy: Optional[ExpirationPolicy] = None,
           *,
           disposable: Optional[bool] = None,
           pretty_print: Optional[bool] = None,
           history_output_limit: Optional[int] = None,
           history_output_width: Optional[int] = None,
           prefetch_history: bool = True,
           history_adapter: Optional[HistoryAdapterType] = default_history_adapter) -> "Mocked":
    if disposable is None:
        disposable = bool(strtobool(REMOTE_MOCK_DISPOSABLE))
    if pretty_print is None:
        pretty_print = bool(strtobool(REMOTE_MOCK_PPRINT))
    if history_output_limit is None:
        history_output_limit = int(REMOTE_MOCK_PPRINT_LIMIT)
    if history_output_width is None:
        history_output_width = REMOTE_MOCK_PPRINT_WIDTH

    handler = create_remote_handler(matcher, response, expiration_policy,
                                    history_adapter=history_adapter)
    return Mocked(handler, disposable=disposable, pretty_print=pretty_print, history_output_limit=history_output_limit,
                  history_output_width=history_output_width, prefetch_history=prefetch_history)


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
