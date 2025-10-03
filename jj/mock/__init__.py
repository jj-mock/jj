import os

from jj.logs import SystemLogFilter  # backward compatibility

from ._create_remote_handler import create_remote_handler
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
from ._mocked_factory import MockedFactory
from ._remote_handler import RemoteHandler
from ._remote_mock import RemoteMock
from ._remote_response import RemoteResponseType
from ._settings import get_remote_mock_disposable, get_remote_mock_url
from ._stacked import stacked

__all__ = ("mocked", "stacked", "Mock", "Mocked", "create_remote_handler", "RemoteMock",
           "RemoteHandler", "HistoryRepository", "HistoryRequest", "HistoryResponse",
           "HistoryItem", "HistoryFormatter", "PrettyHistoryFormatter", "RemoteResponseType",
           "HistoryAdapterType", "SystemLogFilter", "default_history_adapter",
           "REMOTE_MOCK_URL", "REMOTE_MOCK_DISPOSABLE",
           "get_remote_mock_url", "get_remote_mock_disposable",)


# Deprecated: Use getter methods instead to avoid race conditions with runtime env loading
# like load_dotenv()
REMOTE_MOCK_URL = os.environ.get("JJ_REMOTE_MOCK_URL", "http://localhost:8080")
REMOTE_MOCK_DISPOSABLE = os.environ.get("JJ_REMOTE_MOCK_DISPOSABLE", "True")

REMOTE_MOCK_PPRINT = os.environ.get("JJ_REMOTE_MOCK_PPRINT", "False")
REMOTE_MOCK_PPRINT_LENGTH = os.environ.get("JJ_REMOTE_MOCK_PPRINT_LENGTH", "")
REMOTE_MOCK_PPRINT_WIDTH = os.environ.get("JJ_REMOTE_MOCK_PPRINT_WIDTH", "")

# backward compatibility
_REMOTE_MOCK_URL = REMOTE_MOCK_URL
_REMOTE_MOCK_DISPOSABLE = REMOTE_MOCK_DISPOSABLE


mocked = MockedFactory()
