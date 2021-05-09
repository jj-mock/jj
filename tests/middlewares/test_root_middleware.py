import sys

if sys.version_info >= (3, 8):
    from unittest import IsolatedAsyncioTestCase as TestCase
else:
    from unittest import TestCase

from unittest.mock import Mock, call, sentinel

import pytest

import jj
from jj.apps import create_app
from jj.handlers import default_handler
from jj.matchers import MethodMatcher
from jj.middlewares import AbstractMiddleware, RootMiddleware
from jj.requests import Request
from jj.resolvers import Registry, ReversedResolver
from jj.responses import Response

from .._test_utils import run


class TestRootMiddleware(TestCase):
    def setUp(self):
        self.default_app = create_app()
        self.resolver = ReversedResolver(Registry(), self.default_app, default_handler)

    def test_middleware_without_resolver(self):
        with self.assertRaises(Exception):
            RootMiddleware()

    def test_middleware_with_instance_resolver(self):
        middleware = RootMiddleware(self.resolver)
        self.assertIsInstance(middleware, AbstractMiddleware)

    def test_middleware_with_class_resolver(self):
        class Middleware(RootMiddleware):
            resolver = self.resolver
        middleware = Middleware()
        self.assertIsInstance(middleware, AbstractMiddleware)

    @pytest.mark.asyncio
    async def test_middleware_without_impl(self):
        class App(jj.App):
            resolver = self.resolver

        middleware = RootMiddleware(self.resolver)
        async with run(App(), middlewares=[middleware]) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 404)

    @pytest.mark.asyncio
    async def test_middleware_without_impl_but_with_handlers(self):
        class App(jj.App):
            resolver = self.resolver

            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                return Response(status=200)

        middleware = RootMiddleware(self.resolver)
        async with run(App(), middlewares=[middleware]) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 200)

    @pytest.mark.asyncio
    async def test_middleware_with_impl(self):
        mock = Mock()

        class App(jj.App):
            resolver = self.resolver

        class Middleware(RootMiddleware):
            async def do(self, r, h, a):
                mock(r, h, a)
                return await super().do(r, h, a)

        app, middleware = App(), Middleware(self.resolver)
        async with run(app, middlewares=[middleware]) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 404)

        mock.assert_called_once()
        request_arg, handler_arg, app_arg = mock.call_args[0]
        self.assertIsInstance(request_arg, Request)
        self.assertEqual(handler_arg, default_handler)
        self.assertEqual(app_arg, app)

    @pytest.mark.asyncio
    async def test_multiple_root_middlewares(self):
        mock = Mock()

        class App(jj.App):
            resolver = self.resolver

            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                mock(App.__name__, sentinel.BEFORE)
                response = Response(status=200)
                mock(App.__name__, sentinel.AFTER)
                return response

        class Middleware1(RootMiddleware):
            async def do(self, request, handler, app):
                mock(self.__class__.__name__, sentinel.BEFORE)
                response = await super().do(request, handler, app)
                mock(self.__class__.__name__, sentinel.AFTER)
                return response

        class Middleware2(Middleware1):
            pass

        middleware1, middleware2 = Middleware1(self.resolver), Middleware2(self.resolver)
        async with run(App(), middlewares=[middleware2, middleware1]) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 200)

        mock.assert_has_calls([
            call(Middleware2.__name__, sentinel.BEFORE),
            call(Middleware1.__name__, sentinel.BEFORE),
            call(App.__name__, sentinel.BEFORE),
            call(App.__name__, sentinel.AFTER),
            call(Middleware1.__name__, sentinel.AFTER),
            call(Middleware2.__name__, sentinel.AFTER),
        ])
        self.assertEqual(mock.call_count, 6)

    @pytest.mark.asyncio
    async def test_same_root_middlewares(self):
        mock = Mock()

        class App(jj.App):
            resolver = self.resolver

            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                return Response(status=200)

        class Middleware(RootMiddleware):
            async def do(self, request, handler, app):
                mock()
                return await super().do(request, handler, app)

        middleware = Middleware(self.resolver)
        async with run(App(), middlewares=[middleware, middleware]) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 200)

        mock.assert_called_once_with()
