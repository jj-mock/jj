import unittest


class TestImports(unittest.TestCase):
    # apps

    def test_import_abstract_app(self):
        from jj.apps import AbstractApp
        with self.assertRaises(ImportError):
            from jj import AbstractApp

    def test_import_base_app(self):
        from jj.apps import BaseApp
        with self.assertRaises(ImportError):
            from jj import BaseApp

    def test_import_default_app(self):
        from jj.apps import DefaultApp
        with self.assertRaises(ImportError):
            from jj import DefaultApp

    def test_import_app_factory(self):
        from jj.apps import define_app, create_app
        with self.assertRaises(ImportError):
            from jj import define_app, create_app

    def test_import_registrar(self):
        with self.assertRaises(ImportError):
            from jj.apps import _Registrar

    def test_import_singleton(self):
        with self.assertRaises(ImportError):
            from jj.apps import _Singleton

    def test_import_app(self):
        from jj import App

    # handlers

    def test_import_handler_function(self):
        from jj.handlers import HandlerFunction
        with self.assertRaises(ImportError):
            from jj import HandlerFunction

    def test_import_default_handler(self):
        from jj.handlers import default_handler
        from jj import default_handler

    # http

    def test_import_http_codes(self):
        from jj.http.codes import OK
        from jj.http import OK
        with self.assertRaises(ImportError):
            from jj import OK

    def test_import_http_headers(self):
        from jj.http.headers import CONTENT_TYPE
        from jj.http import CONTENT_TYPE
        with self.assertRaises(ImportError):
            from jj import CONTENT_TYPE

    def test_import_http_methods(self):
        from jj.http.methods import GET
        from jj.http import GET
        with self.assertRaises(ImportError):
            from jj import GET

    # logs

    def test_import_logger(self):
        from jj.logs import Logger
        with self.assertRaises(ImportError):
            from jj import Logger

    def test_import_default_logger(self):
        from jj.logs import logger
        with self.assertRaises(ImportError):
            from jj import logger
        from jj import default_logger

    def test_import_filter(self):
        from jj.logs import Filter
        with self.assertRaises(ImportError):
            from jj import Filter

    def test_import_default_filter(self):
        from jj.logs import filter_
        with self.assertRaises(ImportError):
            from jj import filter_

    def test_import_formatter(self):
        from jj.logs import Formatter
        with self.assertRaises(ImportError):
            from jj import Formatter

    def test_import_default_formatter(self):
        from jj.logs import formatter
        with self.assertRaises(ImportError):
            from jj import formatter

    def test_import_simple_formatter(self):
        from jj.logs import SimpleFormatter
        with self.assertRaises(ImportError):
            from jj import SimpleFormatter

    def test_import_default_log_handler(self):
        from jj.logs import handler
        with self.assertRaises(ImportError):
            from jj import handler

    # matchers

    def test_import_attribute_matcher(self):
        from jj.matchers.attribute_matchers import AttributeMatcher
        from jj.matchers import AttributeMatcher
        with self.assertRaises(ImportError):
            from jj import AttributeMatcher

    def test_import_attribute_equal_matcher(self):
        from jj.matchers.attribute_matchers import EqualMatcher
        from jj.matchers import EqualMatcher
        with self.assertRaises(ImportError):
            from jj import EqualMatcher

    def test_import_attribute_not_equal_matcher(self):
        from jj.matchers.attribute_matchers import NotEqualMatcher
        from jj.matchers import NotEqualMatcher
        with self.assertRaises(ImportError):
            from jj import NotEqualMatcher

    def test_import_attribute_contain_matcher(self):
        from jj.matchers.attribute_matchers import ContainMatcher
        from jj.matchers import ContainMatcher
        with self.assertRaises(ImportError):
            from jj import ContainMatcher

    def test_import_attribute_not_contain_matcher(self):
        from jj.matchers.attribute_matchers import NotContainMatcher
        from jj.matchers import NotContainMatcher
        with self.assertRaises(ImportError):
            from jj import NotContainMatcher

    def test_import_attribute_route_matcher(self):
        from jj.matchers.attribute_matchers import RouteMatcher
        with self.assertRaises(ImportError):
            from jj.matchers import RouteMatcher
        with self.assertRaises(ImportError):
            from jj import RouteMatcher

    def test_import_attribute_multi_dict_matcher(self):
        from jj.matchers.attribute_matchers import MultiDictMatcher
        with self.assertRaises(ImportError):
            from jj.matchers import MultiDictMatcher
        with self.assertRaises(ImportError):
            from jj import MultiDictMatcher

    def test_import_logical_matcher(self):
        from jj.matchers.logical_matchers import LogicalMatcher
        from jj.matchers import LogicalMatcher
        with self.assertRaises(ImportError):
            from jj import LogicalMatcher

    def test_import_logical_all_matcher(self):
        from jj.matchers.logical_matchers import AllMatcher
        from jj.matchers import AllMatcher
        with self.assertRaises(ImportError):
            from jj import AllMatcher

    def test_import_logical_any_matcher(self):
        from jj.matchers.logical_matchers import AnyMatcher
        from jj.matchers import AnyMatcher
        with self.assertRaises(ImportError):
            from jj import AnyMatcher

    def test_import_request_matcher(self):
        from jj.matchers.request_matchers import RequestMatcher
        from jj.matchers import RequestMatcher
        with self.assertRaises(ImportError):
            from jj import RequestMatcher

    def test_import_request_method_matcher(self):
        from jj.matchers.request_matchers import MethodMatcher
        from jj.matchers import MethodMatcher
        with self.assertRaises(ImportError):
            from jj import MethodMatcher

    def test_import_request_path_matcher(self):
        from jj.matchers.request_matchers import PathMatcher
        from jj.matchers import PathMatcher
        with self.assertRaises(ImportError):
            from jj import PathMatcher

    def test_import_request_param_matcher(self):
        from jj.matchers.request_matchers import ParamMatcher
        from jj.matchers import ParamMatcher
        with self.assertRaises(ImportError):
            from jj import ParamMatcher

    def test_import_request_header_matcher(self):
        from jj.matchers.request_matchers import HeaderMatcher
        from jj.matchers import HeaderMatcher
        with self.assertRaises(ImportError):
            from jj import HeaderMatcher

    def test_import_resolvable_matcher(self):
        from jj.matchers.resolvable_matcher import ResolvableMatcher
        from jj.matchers import ResolvableMatcher
        with self.assertRaises(ImportError):
            from jj import ResolvableMatcher

    def test_import_equals_matcher(self):
        from jj.matchers import equals
        with self.assertRaises(ImportError):
            from jj import equals

    def test_import_contains_matcher(self):
        from jj.matchers import contains
        with self.assertRaises(ImportError):
            from jj import contains

    def test_import_match_methods(self):
        from jj import match_method
        from jj import match_path
        from jj import match_header, match_headers
        from jj import match_param, match_params
        from jj import match_all, match_any
        from jj import match

    # middlewares

    def test_import_abstract_middleware(self):
        from jj.middlewares import AbstractMiddleware
        with self.assertRaises(ImportError):
            from jj import AbstractMiddleware

    def test_import_root_middleware(self):
        from jj.middlewares import RootMiddleware
        with self.assertRaises(ImportError):
            from jj import RootMiddleware

    def test_import_base_middleware(self):
        from jj.middlewares import BaseMiddleware
        with self.assertRaises(ImportError):
            from jj import BaseMiddleware

    def test_import_self_middleware(self):
        from jj.middlewares import SelfMiddleware
        with self.assertRaises(ImportError):
            from jj import SelfMiddleware

    def test_import_logger_middleware(self):
        from jj.middlewares import LoggerMiddleware
        with self.assertRaises(ImportError):
            from jj import LoggerMiddleware

    def test_import_middleware(self):
        from jj import Middleware

    # requests

    def test_import_request(self):
        from jj.requests import Request
        from jj import Request

    # resolvers

    def test_import_registry(self):
        from jj.resolvers import Registry
        with self.assertRaises(ImportError):
            from jj import Registry

    def test_import_resolver(self):
        from jj.resolvers import Resolver
        with self.assertRaises(ImportError):
            from jj import Resolver

    def test_import_reversed_resolver(self):
        from jj.resolvers import ReversedResolver
        with self.assertRaises(ImportError):
            from jj import ReversedResolver

    # responses

    def test_import_response(self):
        from jj.responses import Response
        from jj import Response

    def test_import_stream_response(self):
        from jj.responses import StreamResponse
        from jj import StreamResponse

    def test_import_tunnel_response(self):
        from jj.responses import TunnelResponse
        from jj import TunnelResponse

    # runners

    def test_import_runner(self):
        from jj.runners import AppRunner
        with self.assertRaises(ImportError):
            from jj import AppRunner

    # servers

    def test_import_server(self):
        from jj.servers import Server
        with self.assertRaises(ImportError):
            from jj import Server

    def test_import_start(self):
        from jj import start

    def test_import_wait_for(self):
        from jj import wait_for

    def test_import_serve(self):
        from jj import serve

    def test_import_version(self):
        from jj import version
        from jj import server_version
