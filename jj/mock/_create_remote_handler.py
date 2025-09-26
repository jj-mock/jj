from typing import Optional, Union

from jj.expiration_policy import ExpirationPolicy
from jj.matchers import LogicalMatcher, RequestMatcher

from ._history import HistoryAdapterType, default_history_adapter
from ._remote_handler import RemoteHandler
from ._remote_mock import RemoteMock
from ._remote_response import RemoteResponseType
from ._settings import get_remote_mock_url

__all__ = ("create_remote_handler",)


def create_remote_handler(matcher: Union[RequestMatcher, LogicalMatcher],
                          response: RemoteResponseType,
                          expiration_policy: Optional[ExpirationPolicy] = None,
                          *,
                          mock_url: Optional[str] = None,
                          history_adapter: Optional[HistoryAdapterType] = default_history_adapter
                          ) -> RemoteHandler:
    """
    Create a remote handler for mocking HTTP requests.

    This function creates a `RemoteHandler` instance that will intercept and mock
    HTTP requests matching the specified criteria, returning the configured response.

    :param matcher: A matcher that determines which requests to intercept. Can be either
                    a `RequestMatcher` or `LogicalMatcher`.
    :param response: The response to return for matched requests. Can be any valid
                     remote response type.
    :param expiration_policy: Optional policy that determines when the mock should expire.
                              If `None`, the mock will not expire.
    :param mock_url: Optional URL of the remote mock server. If `None`, uses the value
                     from the `JJ_REMOTE_MOCK_URL` environment variable or defaults to
                     "http://localhost:8080".
    :param history_adapter: Optional adapter for handling request/response history.
                            Defaults to `default_history_adapter`.
    :return: A `RemoteHandler` instance configured with the specified parameters.
    """
    if mock_url is None:
        mock_url = get_remote_mock_url()
    return RemoteMock(mock_url).create_handler(matcher, response, expiration_policy,
                                               history_adapter=history_adapter)
