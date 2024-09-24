import asyncio
from functools import partial
from typing import List, Optional, Sequence, Type

from aiohttp import web

from .apps import AbstractApp, BaseApp, DefaultApp
from .handlers import default_handler
from .logs import Logger
from .logs import logger as default_logger
from .matchers import ResolvableMatcher
from .matchers.logical_matchers import AllMatcher, AnyMatcher
from .matchers.request_matchers import (
    DictOrTupleListOrAttrMatcher,
    HeaderMatcher,
    MethodMatcher,
    ParamMatcher,
    PathMatcher,
    StrOrAttrMatcher,
)
from .middlewares import BaseMiddleware, LoggerMiddleware, SelfMiddleware
from .resolvers import Registry, ReversedResolver
from .runners import AppRunner
from .servers import Server

__all__ = (
    "App",
    "Middleware",
    "match_method", "match_methods",
    "match_path",
    "match_headers", "match_header",
    "match_params", "match_param",
    "match_all", "match_any",
    "match",
    "start", "wait_for", "serve",
    "default_app", "default_handler", "default_logger",
)

default_app = DefaultApp()
registry = Registry()
resolver = ReversedResolver(registry, default_app, default_handler)
loop = asyncio.get_event_loop()

runner = partial(AppRunner, resolver=resolver, handle_signals=True, middlewares=[
    SelfMiddleware(resolver),
])
# ignore because of https://github.com/python/mypy/issues/1484
server = Server(loop, runner, web.TCPSite)  # type: ignore


class App(BaseApp):
    """
    Represents the main application class, extending `BaseApp`.

    This class uses the global `resolver` for request handling and matcher resolution.
    """
    resolver = resolver


class Middleware(BaseMiddleware):
    """
    Represents middleware used in the application, extending `BaseMiddleware`.

    This middleware also uses the global `resolver` for matcher resolution and handling.
    """
    resolver = resolver


def match_method(method: StrOrAttrMatcher) -> MethodMatcher:
    """
    Match an HTTP request based on its method.

    :param method: The HTTP method to match (e.g., "GET", "POST").
    :return: A `MethodMatcher` that will match requests with the given method.
    """
    return MethodMatcher(method, resolver=resolver)


def match_methods(*methods: StrOrAttrMatcher) -> AnyMatcher:
    """
    Match an HTTP request against multiple possible methods.

    :param methods: A variable number of HTTP methods to match.
    :return: An `AnyMatcher` that will match if any of the methods match.
    """
    matchers: List[ResolvableMatcher] = [
        MethodMatcher(method, resolver=resolver)
        for method in methods
    ]
    return AnyMatcher(matchers, resolver=resolver)


def match_path(path: StrOrAttrMatcher) -> PathMatcher:
    """
    Match an HTTP request based on the request path.

    :param path: The path or a matcher for the path to match (e.g., "/users").
    :return: A `PathMatcher` that will match requests with the given path.
    """
    return PathMatcher(path, resolver=resolver)


def match_headers(headers: DictOrTupleListOrAttrMatcher) -> HeaderMatcher:
    """
    Match an HTTP request based on its headers.

    :param headers: The headers or matchers for the headers to match.
    :return: A `HeaderMatcher` that will match requests with the given headers.
    """
    return HeaderMatcher(headers, resolver=resolver)


def match_header(name: str, value: StrOrAttrMatcher) -> HeaderMatcher:
    """
    Match an HTTP request based on a specific header.

    :param name: The name of the header to match.
    :param value: The expected value of the header or a matcher for the value.
    :return: A `HeaderMatcher` that will match requests with the specified header.
    """
    return HeaderMatcher([(name, value)], resolver=resolver)


def match_params(params: DictOrTupleListOrAttrMatcher) -> ParamMatcher:
    """
    Match an HTTP request based on its query parameters.

    :param params: The query parameters or matchers for the parameters.
    :return: A `ParamMatcher` that will match requests with the given query parameters.
    """
    return ParamMatcher(params, resolver=resolver)


def match_param(name: str, value: StrOrAttrMatcher) -> ParamMatcher:
    """
    Match an HTTP request based on a specific query parameter.

    :param name: The name of the query parameter to match.
    :param value: The expected value of the parameter or a matcher for the value.
    :return: A `ParamMatcher` that will match requests with the specified query parameter.
    """
    return ParamMatcher([(name, value)], resolver=resolver)


def match_all(matchers: List[ResolvableMatcher]) -> AllMatcher:
    """
    Match an HTTP request if all provided matchers succeed.

    :param matchers: A list of matchers that must all succeed for the request to match.
    :return: An `AllMatcher` that will match only if all the matchers succeed.
    """
    return AllMatcher(matchers, resolver=resolver)


def match_any(matchers: List[ResolvableMatcher]) -> AnyMatcher:
    """
    Match an HTTP request if any of the provided matchers succeed.

    :param matchers: A list of matchers where at least one must succeed for the request to match.
    :return: An `AnyMatcher` that will match if any of the matchers succeed.
    """
    return AnyMatcher(matchers, resolver=resolver)


def match(method: Optional[StrOrAttrMatcher] = None,
          path: Optional[StrOrAttrMatcher] = None,
          params: Optional[DictOrTupleListOrAttrMatcher] = None,
          headers: Optional[DictOrTupleListOrAttrMatcher] = None) -> AllMatcher:
    """
    Match an HTTP request based on multiple criteria such as method, path,
    query parameters, and headers.

    :param method: The HTTP method to match (optional).
    :param path: The request path to match (optional).
    :param params: The query parameters to match (optional).
    :param headers: The headers to match (optional).
    :return: An `AllMatcher` that matches if all specified conditions are met.
    """
    submatchers: List[ResolvableMatcher] = []
    if method:
        submatchers += [MethodMatcher(method, resolver=resolver)]
    if path:
        submatchers += [PathMatcher(path, resolver=resolver)]
    if params:
        submatchers += [ParamMatcher(params, resolver=resolver)]
    if headers:
        submatchers += [HeaderMatcher(headers, resolver=resolver)]
    return AllMatcher(submatchers, resolver=resolver)


def start(app: AbstractApp, *,
          host: Optional[str] = None, port: Optional[int] = None,
          logger: Logger = default_logger) -> None:
    """
    Start the HTTP server for the provided app.

    :param app: The application instance to run.
    :param host: The host address to bind to (optional).
    :param port: The port to bind to (optional).
    :param logger: The logger instance to use for logging (default: `default_logger`).
    """
    LoggerMiddleware(resolver, logger)(type(app))
    server.start(app, host=host, port=port)


def wait_for(exceptions: Sequence[Type[BaseException]]) -> None:
    """
    Wait for server termination, handling the provided exceptions.

    This method blocks until the server shuts down, listening for specified exceptions.

    :param exceptions: A sequence of exception types that should be handled to stop the server.
    """
    try:
        server.serve(exceptions)
    finally:
        server.shutdown()


def serve(app: AbstractApp = default_app, *,
          host: Optional[str] = None, port: Optional[int] = None,
          logger: Logger = default_logger) -> None:
    """
    Serve the provided app and wait for its termination.

    This method starts the app and blocks until the server is interrupted
    (e.g., by a keyboard interrupt).

    :param app: The application instance to run (default: `default_app`).
    :param host: The host address to bind to (optional).
    :param port: The port to bind to (optional).
    :param logger: The logger instance to use for logging (default: `default_logger`).
    """
    start(app, host=host, port=port, logger=logger)
    wait_for([KeyboardInterrupt])
