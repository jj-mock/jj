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
    "match_method",
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

runner = partial(AppRunner, resolver=resolver, middlewares=[
    SelfMiddleware(resolver),
])
# ignore because of https://github.com/python/mypy/issues/1484
server = Server(loop, runner, web.TCPSite)  # type: ignore


class App(BaseApp):
    resolver = resolver


class Middleware(BaseMiddleware):
    resolver = resolver


def match_method(method: StrOrAttrMatcher) -> MethodMatcher:
    return MethodMatcher(method, resolver=resolver)


def match_path(path: StrOrAttrMatcher) -> PathMatcher:
    return PathMatcher(path, resolver=resolver)


def match_headers(headers: DictOrTupleListOrAttrMatcher) -> HeaderMatcher:
    return HeaderMatcher(headers, resolver=resolver)


def match_header(name: str, value: StrOrAttrMatcher) -> HeaderMatcher:
    return HeaderMatcher([(name, value)], resolver=resolver)


def match_params(params: DictOrTupleListOrAttrMatcher) -> ParamMatcher:
    return ParamMatcher(params, resolver=resolver)


def match_param(name: str, value: StrOrAttrMatcher) -> ParamMatcher:
    return ParamMatcher([(name, value)], resolver=resolver)


def match_all(matchers: List[ResolvableMatcher]) -> AllMatcher:
    return AllMatcher(matchers, resolver=resolver)


def match_any(matchers: List[ResolvableMatcher]) -> AnyMatcher:
    return AnyMatcher(matchers, resolver=resolver)


def match(method: Optional[StrOrAttrMatcher] = None,
          path: Optional[StrOrAttrMatcher] = None,
          params: Optional[DictOrTupleListOrAttrMatcher] = None,
          headers: Optional[DictOrTupleListOrAttrMatcher] = None) -> AllMatcher:
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
    LoggerMiddleware(resolver, logger)(type(app))
    server.start(app, host=host, port=port)


def wait_for(exceptions: Sequence[Type[BaseException]]) -> None:
    try:
        server.serve()
    except tuple(exceptions):
        pass
    finally:
        server.cleanup()
    server.shutdown()


def serve(app: AbstractApp = default_app, *,
          host: Optional[str] = None, port: Optional[int] = None,
          logger: Logger = default_logger) -> None:
    start(app, host=host, port=port, logger=logger)
    wait_for([KeyboardInterrupt])
