import asyncio
from functools import partial
from typing import Optional, List

from aiohttp import web

from .apps import AbstractApp, DefaultApp, BaseApp
from .resolvers import Registry, ReversedResolver
from .handlers import default_handler
from .logs import Logger, logger as default_logger
from .servers import Server
from .runners import AppRunner
from .middlewares import BaseMiddleware, SelfMiddleware, LoggerMiddleware
from .matchers import ResolvableMatcher
from .matchers.logical_matchers import AllMatcher, AnyMatcher
from .matchers.request_matchers import (MethodMatcher, PathMatcher,
                                        HeaderMatcher, ParamMatcher, StrOrAttrMatcher,
                                        DictOrTupleListOrAttrMatcher)


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
    "default_app", "default_handler",
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
    return MethodMatcher(resolver, method)


def match_path(path: StrOrAttrMatcher) -> PathMatcher:
    return PathMatcher(resolver, path)


def match_headers(headers: DictOrTupleListOrAttrMatcher) -> HeaderMatcher:
    return HeaderMatcher(resolver, headers)


def match_header(name: str, value: StrOrAttrMatcher) -> HeaderMatcher:
    return HeaderMatcher(resolver, [(name, value)])


def match_params(params: DictOrTupleListOrAttrMatcher) -> ParamMatcher:
    return ParamMatcher(resolver, params)


def match_param(name: str, value: StrOrAttrMatcher) -> ParamMatcher:
    return ParamMatcher(resolver, [(name, value)])


def match_all(matchers: List[ResolvableMatcher]) -> AllMatcher:
    return AllMatcher(resolver, matchers)


def match_any(matchers: List[ResolvableMatcher]) -> AnyMatcher:
    return AnyMatcher(resolver, matchers)


def match(method=None, path=None, params=None, headers=None) -> AllMatcher:
    submatchers: List[ResolvableMatcher] = []
    if method:
        submatchers += [MethodMatcher(resolver, method)]
    if path:
        submatchers += [PathMatcher(resolver, path)]
    if params:
        submatchers += [ParamMatcher(resolver, params)]
    if headers:
        submatchers += [HeaderMatcher(resolver, headers)]
    return AllMatcher(resolver, submatchers)


def start(app: AbstractApp, *,
          host: Optional[str] = None, port: Optional[int] = None,
          logger: Logger = default_logger) -> None:
    LoggerMiddleware(resolver, logger)(type(app))
    server.start(app, host=host, port=port)


def wait_for(exceptions) -> None:
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
