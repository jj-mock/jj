import os
from distutils.util import strtobool
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
    SimpleHistoryFormatter,
    default_history_adapter,
    default_history_formatter,
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

# backward compatibility
_REMOTE_MOCK_URL = REMOTE_MOCK_URL
_REMOTE_MOCK_DISPOSABLE = REMOTE_MOCK_DISPOSABLE


def mocked(matcher: Union[RequestMatcher, LogicalMatcher],
           response: RemoteResponseType,
           expiration_policy: Optional[ExpirationPolicy] = None,
           *,
           disposable: Optional[bool] = None,
           prefetch_history: bool = True,
           pretty_print: Optional[bool] = None,
           history_adapter: Optional[HistoryAdapterType] = default_history_adapter) -> "Mocked":
    if disposable is None:
        disposable = bool(strtobool(REMOTE_MOCK_DISPOSABLE))
    if pretty_print is None:
        pretty_print = bool(strtobool(REMOTE_MOCK_PPRINT))

    handler = create_remote_handler(
        matcher, response, expiration_policy, history_adapter=history_adapter
    )
    history_formatter = default_history_formatter if pretty_print else \
        SimpleHistoryFormatter()

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
           "default_history_formatter", "HistoryFormatter", "PrettyHistoryFormatter",
           "SimpleHistoryFormatter",
           "SystemLogFilter", "RemoteResponseType", "HistoryAdapterType",
           "default_history_adapter", "REMOTE_MOCK_URL",
           "REMOTE_MOCK_DISPOSABLE")
