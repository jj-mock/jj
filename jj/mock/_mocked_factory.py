from typing import Any, Callable, Optional, TypeVar, Union

from jj.expiration_policy import ExpirationPolicy
from jj.matchers import LogicalMatcher, RequestMatcher

from ._create_remote_handler import create_remote_handler
from ._history import (
    HistoryAdapterType,
    HistoryFormatter,
    PrettyHistoryFormatter,
    default_history_adapter,
)
from ._mocked import Mocked
from ._remote_response import RemoteResponseType
from ._settings import (
    get_remote_mock_disposable,
    get_remote_mock_pprint,
    get_remote_mock_pprint_length,
    get_remote_mock_pprint_width,
)

__all__ = ("MockedFactory",)

F = TypeVar("F", bound=Callable[..., Any])


class MockedFactory:
    """
    Factory for creating `Mocked` instances with remote handlers.

    This class provides multiple ways to create and use mocked HTTP requests:
    - Direct instantiation via `__call__`
    - As a decorator with mock injection via `with_mock`

    The factory handles configuration from environment variables and sets up
    the remote handler with the specified matchers and responses.
    """

    def __call__(
        self,
        matcher: Union[RequestMatcher, LogicalMatcher],
        response: RemoteResponseType,
        expiration_policy: Optional[ExpirationPolicy] = None,
        *,
        disposable: Optional[bool] = None,
        prefetch_history: bool = True,
        history_formatter: Optional[HistoryFormatter] = None,
        history_adapter: Optional[HistoryAdapterType] = default_history_adapter
    ) -> Mocked:
        """
        Create a `Mocked` instance for intercepting and mocking HTTP requests.

        This method can be used as a context manager or decorator to mock HTTP requests
        that match the specified criteria.

        :param matcher: A matcher that determines which requests to intercept.
        :param response: The response to return for matched requests.
        :param expiration_policy: Optional policy that determines when the mock expires.
        :param disposable: Whether the mock should be automatically deregistered after use.
                          If `None`, uses the value from `JJ_REMOTE_MOCK_DISPOSABLE` env var.
        :param prefetch_history: Whether to automatically fetch request history when exiting
                                the context. Defaults to `True`.
        :param history_formatter: Optional formatter for displaying request/response history.
                                 If `None` and `JJ_REMOTE_MOCK_PPRINT` is "true", uses
                                 `PrettyHistoryFormatter`.
        :param history_adapter: Optional adapter for handling request/response history.
                               Defaults to `default_history_adapter`.
        :return: A configured `Mocked` instance.
        """
        return self._mocked(matcher, response, expiration_policy,
                            disposable=disposable,
                            prefetch_history=prefetch_history,
                            history_formatter=history_formatter,
                            history_adapter=history_adapter)

    def with_mock(
        self,
        matcher: Union[RequestMatcher, LogicalMatcher],
        response: RemoteResponseType,
        expiration_policy: Optional[ExpirationPolicy] = None,
        *,
        disposable: Optional[bool] = None,
        prefetch_history: bool = True,
        history_formatter: Optional[HistoryFormatter] = None,
        history_adapter: Optional[HistoryAdapterType] = default_history_adapter
    ) -> Callable[[F], F]:
        """
        Create a decorator that injects a `Mocked` instance into the decorated function.

        This method returns a decorator that passes the mock as the first argument to
        the decorated function, allowing direct access to the mock instance within tests.

        :param matcher: A matcher that determines which requests to intercept.
        :param response: The response to return for matched requests.
        :param expiration_policy: Optional policy that determines when the mock expires.
        :param disposable: Whether the mock should be automatically deregistered after use.
                          If `None`, uses the value from `JJ_REMOTE_MOCK_DISPOSABLE` env var.
        :param prefetch_history: Whether to automatically fetch request history when exiting
                                the context. Defaults to `True`.
        :param history_formatter: Optional formatter for displaying request/response history.
                                 If `None` and `JJ_REMOTE_MOCK_PPRINT` is "true", uses
                                 `PrettyHistoryFormatter`.
        :param history_adapter: Optional adapter for handling request/response history.
                               Defaults to `default_history_adapter`.
        :return: A decorator that injects the mock into the decorated function.
        """
        return self._mocked(matcher, response, expiration_policy,
                            disposable=disposable,
                            prefetch_history=prefetch_history,
                            history_formatter=history_formatter,
                            history_adapter=history_adapter).with_mock

    def _mocked(
        self,
        matcher: Union[RequestMatcher, LogicalMatcher],
        response: RemoteResponseType,
        expiration_policy: Optional[ExpirationPolicy] = None,
        *,
        disposable: Optional[bool] = None,
        prefetch_history: bool = True,
        history_formatter: Optional[HistoryFormatter] = None,
        history_adapter: Optional[HistoryAdapterType] = default_history_adapter
    ) -> Mocked:
        if disposable is None:
            disposable = get_remote_mock_disposable()

        if (history_formatter is None) and get_remote_mock_pprint():
            history_formatter = PrettyHistoryFormatter(
                get_remote_mock_pprint_width(),
                get_remote_mock_pprint_length()
            )

        handler = create_remote_handler(matcher, response, expiration_policy,
                                        history_adapter=history_adapter)

        return Mocked(handler, disposable=disposable, prefetch_history=prefetch_history,
                      history_formatter=history_formatter)
