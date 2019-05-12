import asynctest
from asynctest import Mock, call

import jj
from jj.apps import create_app
from jj.resolvers import Registry, ReversedResolver
from jj.matchers import MethodMatcher, PathMatcher
from jj.handlers import default_handler
from jj.requests import Request
from jj.responses import Response
from jj.middlewares import RootMiddleware, SelfMiddleware, BaseMiddleware

from .._test_utils import run


class TestSelfMiddleware(asynctest.TestCase):
    def setUp(self):
        self.default_app = create_app()
        self.resolver = ReversedResolver(Registry(), self.default_app, default_handler)

    def test_middleware_without_resolver(self):
        with self.assertRaises(Exception):
            SelfMiddleware()

    def test_middleware_with_instance_resolver(self):
        middleware = SelfMiddleware(self.resolver)
        self.assertIsInstance(middleware, RootMiddleware)

    def test_middleware_with_class_resolver(self):
        class Middleware(SelfMiddleware):
            resolver = self.resolver
        middleware = Middleware()
        self.assertIsInstance(middleware, RootMiddleware)

    async def test_middleware_without_handlers(self):
        class App(jj.App):
            resolver = self.resolver

        middleware = SelfMiddleware(self.resolver)
        async with run(App(), middlewares=[middleware]) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 404)

    async def test_middleware_with_handler(self):
        mock = Mock()

        class App(jj.App):
            resolver = self.resolver
            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                mock(request)
                return Response(status=200)

        middleware = SelfMiddleware(self.resolver)
        async with run(App(), middlewares=[middleware]) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 200)

        mock.assert_called_once()
        request_arg, = mock.call_args[0]
        self.assertIsInstance(request_arg, Request)

    async def test_middleware_with_handler_and_self_reference(self):
        mock = Mock()

        class App(jj.App):
            resolver = self.resolver
            @MethodMatcher("*", resolver=resolver)
            async def handler(self, request):
                mock(self, request)
                return Response(status=200)

        app, middleware = App(), SelfMiddleware(self.resolver)
        async with run(app, middlewares=[middleware]) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 200)

        mock.assert_called_once()
        app_arg, request_arg = mock.call_args[0]
        self.assertIsInstance(app_arg, App)
        self.assertIsInstance(request_arg, Request)

    async def test_middleware_with_handler_middleware(self):
        mock = Mock()

        class App(jj.App):
            resolver = self.resolver
            @PathMatcher("/path", resolver=resolver)
            @BaseMiddleware(resolver)
            @MethodMatcher("*", resolver=resolver)
            async def handler(self, request):
                mock(self, request)
                return Response(status=200)

        app, middleware = App(), SelfMiddleware(self.resolver)
        async with run(app, middlewares=[middleware]) as client:
            response = await client.get("/path")
            self.assertEqual(response.status, 200)

        mock.assert_called_once()
        app_arg, request_arg = mock.call_args[0]
        self.assertIsInstance(app_arg, App)
        self.assertIsInstance(request_arg, Request)
