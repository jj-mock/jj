from pytest import raises

# apps


def test_import_abstract_app():
    from jj.apps import AbstractApp
    with raises(ImportError):
        from jj import AbstractApp


def test_import_base_app():
    from jj.apps import BaseApp
    with raises(ImportError):
        from jj import BaseApp


def test_import_default_app():
    from jj.apps import DefaultApp
    with raises(ImportError):
        from jj import DefaultApp


def test_import_app_factory():
    from jj.apps import define_app, create_app
    with raises(ImportError):
        from jj import define_app, create_app


def test_import_registrar():
    with raises(ImportError):
        from jj.apps import _Registrar


def test_import_singleton():
    with raises(ImportError):
        from jj.apps import _Singleton


def test_import_app():
    from jj import App


# handlers


def test_import_handler_function():
    from jj.handlers import HandlerFunction
    with raises(ImportError):
        from jj import HandlerFunction


def test_import_default_handler():
    from jj.handlers import default_handler
    from jj import default_handler


# http


def test_import_http_codes():
    from jj.http.codes import OK
    from jj.http import OK
    with raises(ImportError):
        from jj import OK


def test_import_http_headers():
    from jj.http.headers import CONTENT_TYPE
    from jj.http import CONTENT_TYPE
    with raises(ImportError):
        from jj import CONTENT_TYPE


def test_import_http_methods():
    from jj.http.methods import GET
    from jj.http import GET
    with raises(ImportError):
        from jj import GET


# logs


def test_import_logger():
    from jj.logs import Logger
    with raises(ImportError):
        from jj import Logger


def test_import_default_logger():
    from jj.logs import logger
    with raises(ImportError):
        from jj import logger
    from jj import default_logger


def test_import_filter():
    from jj.logs import Filter
    with raises(ImportError):
        from jj import Filter


def test_import_default_filter():
    from jj.logs import filter_
    with raises(ImportError):
        from jj import filter_


def test_import_formatter():
    from jj.logs import Formatter
    with raises(ImportError):
        from jj import Formatter


def test_import_default_formatter():
    from jj.logs import formatter
    with raises(ImportError):
        from jj import formatter


def test_import_simple_formatter():
    from jj.logs import SimpleFormatter
    with raises(ImportError):
        from jj import SimpleFormatter


def test_import_default_log_handler():
    from jj.logs import handler
    with raises(ImportError):
        from jj import handler


# matchers


def test_import_resolvable_matcher():
    from jj.matchers import ResolvableMatcher
    with raises(ImportError):
        from jj import ResolvableMatcher


def test_import_match_methods():
    from jj import match_method
    from jj import match_path
    from jj import match_header, match_headers
    from jj import match_param, match_params
    from jj import match_all, match_any
    from jj import match


def test_import_matcher_shorthands():
    from jj.matchers import exists
    with raises(ImportError):
        from jj import exists

    from jj.matchers import equals, not_equals
    with raises(ImportError):
        from jj import equals
    with raises(ImportError):
        from jj import not_equals

    from jj.matchers import contains, not_contains
    with raises(ImportError):
        from jj import contains
    with raises(ImportError):
        from jj import not_contains

    from jj.matchers import regex
    with raises(ImportError):
        from jj import regex


# matchers/attribute_matchers


def test_import_attribute_matcher():
    from jj.matchers.attribute_matchers import AttributeMatcher
    from jj.matchers import AttributeMatcher
    with raises(ImportError):
        from jj import AttributeMatcher


def test_import_attribute_contain_matcher():
    from jj.matchers.attribute_matchers import ContainMatcher
    from jj.matchers import ContainMatcher
    with raises(ImportError):
        from jj import ContainMatcher


def test_import_attribute_not_contain_matcher():
    from jj.matchers.attribute_matchers import NotContainMatcher
    from jj.matchers import NotContainMatcher
    with raises(ImportError):
        from jj import NotContainMatcher


def test_import_attribute_equal_matcher():
    from jj.matchers.attribute_matchers import EqualMatcher
    from jj.matchers import EqualMatcher
    with raises(ImportError):
        from jj import EqualMatcher


def test_import_attribute_not_equal_matcher():
    from jj.matchers.attribute_matchers import NotEqualMatcher
    from jj.matchers import NotEqualMatcher
    with raises(ImportError):
        from jj import NotEqualMatcher


def test_import_attribute_exist_matcher():
    from jj.matchers.attribute_matchers import ExistMatcher
    from jj.matchers import ExistMatcher
    with raises(ImportError):
        from jj import ExistMatcher


def test_import_attribute_multi_dict_matcher():
    from jj.matchers.attribute_matchers import MultiDictMatcher
    with raises(ImportError):
        from jj.matchers import MultiDictMatcher
    with raises(ImportError):
        from jj import MultiDictMatcher


def test_import_attribute_regex_matcher():
    from jj.matchers.attribute_matchers import RegexMatcher
    from jj.matchers import RegexMatcher
    with raises(ImportError):
        from jj import RegexMatcher


def test_import_attribute_route_matcher():
    from jj.matchers.attribute_matchers import RouteMatcher
    with raises(ImportError):
        from jj.matchers import RouteMatcher
    with raises(ImportError):
        from jj import RouteMatcher


# matchers/logical_matchers


def test_import_logical_all_matcher():
    from jj.matchers.logical_matchers import AllMatcher
    from jj.matchers import AllMatcher
    with raises(ImportError):
        from jj import AllMatcher


def test_import_logical_any_matcher():
    from jj.matchers.logical_matchers import AnyMatcher
    from jj.matchers import AnyMatcher
    with raises(ImportError):
        from jj import AnyMatcher


def test_import_logical_matcher():
    from jj.matchers.logical_matchers import LogicalMatcher
    from jj.matchers import LogicalMatcher
    with raises(ImportError):
        from jj import LogicalMatcher


# matchers/request_matchers


def test_import_request_header_matcher():
    from jj.matchers.request_matchers import HeaderMatcher
    from jj.matchers import HeaderMatcher
    with raises(ImportError):
        from jj import HeaderMatcher


def test_import_request_method_matcher():
    from jj.matchers.request_matchers import MethodMatcher
    from jj.matchers import MethodMatcher
    with raises(ImportError):
        from jj import MethodMatcher


def test_import_request_param_matcher():
    from jj.matchers.request_matchers import ParamMatcher
    from jj.matchers import ParamMatcher
    with raises(ImportError):
        from jj import ParamMatcher


def test_import_request_path_matcher():
    from jj.matchers.request_matchers import PathMatcher
    from jj.matchers import PathMatcher
    with raises(ImportError):
        from jj import PathMatcher


def test_import_request_matcher():
    from jj.matchers.request_matchers import RequestMatcher
    from jj.matchers import RequestMatcher
    with raises(ImportError):
        from jj import RequestMatcher


# middlewares


def test_import_abstract_middleware():
    from jj.middlewares import AbstractMiddleware
    with raises(ImportError):
        from jj import AbstractMiddleware


def test_import_root_middleware():
    from jj.middlewares import RootMiddleware
    with raises(ImportError):
        from jj import RootMiddleware


def test_import_base_middleware():
    from jj.middlewares import BaseMiddleware
    with raises(ImportError):
        from jj import BaseMiddleware


def test_import_self_middleware():
    from jj.middlewares import SelfMiddleware
    with raises(ImportError):
        from jj import SelfMiddleware


def test_import_logger_middleware():
    from jj.middlewares import LoggerMiddleware
    with raises(ImportError):
        from jj import LoggerMiddleware


def test_import_middleware():
    from jj import Middleware


# requests


def test_import_request():
    from jj.requests import Request
    from jj import Request


# resolvers


def test_import_registry():
    from jj.resolvers import Registry
    with raises(ImportError):
        from jj import Registry


def test_import_resolver():
    from jj.resolvers import Resolver
    with raises(ImportError):
        from jj import Resolver


def test_import_reversed_resolver():
    from jj.resolvers import ReversedResolver
    with raises(ImportError):
        from jj import ReversedResolver


# responses


def test_import_response():
    from jj.responses import Response
    from jj import Response


def test_import_static_response():
    from jj.responses import StaticResponse
    from jj import StaticResponse


def test_import_stream_response():
    from jj.responses import StreamResponse
    from jj import StreamResponse


def test_import_tunnel_response():
    from jj.responses import TunnelResponse
    from jj import TunnelResponse


# runners


def test_import_runner():
    from jj.runners import AppRunner
    with raises(ImportError):
        from jj import AppRunner


# servers


def test_import_server():
    from jj.servers import Server
    with raises(ImportError):
        from jj import Server


def test_import_start():
    from jj import start


def test_import_wait_for():
    from jj import wait_for


def test_import_serve():
    from jj import serve


def test_import_version():
    from jj import version
    from jj import server_version
