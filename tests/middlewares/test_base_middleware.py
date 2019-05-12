import asynctest
from asynctest import Mock, sentinel, call

import jj
from jj.apps import create_app
from jj.resolvers import Registry, ReversedResolver
from jj.matchers import MethodMatcher, PathMatcher
from jj.handlers import default_handler
from jj.requests import Request
from jj.responses import Response
from jj.middlewares import AbstractMiddleware, BaseMiddleware, RootMiddleware

from .._test_utils import run


class TestBaseMiddleware(asynctest.TestCase):
    def setUp(self):
        self.default_app = create_app()
        self.resolver = ReversedResolver(Registry(), self.default_app, default_handler)

    def test_middleware_without_resolver(self):
        with self.assertRaises(Exception):
            BaseMiddleware()

    def test_middleware_with_instance_resolver(self):
        middleware = BaseMiddleware(self.resolver)
        self.assertIsInstance(middleware, AbstractMiddleware)

    def test_middleware_with_class_resolver(self):
        class Middleware(BaseMiddleware):
            resolver = self.resolver
        middleware = Middleware()
        self.assertIsInstance(middleware, AbstractMiddleware)

    async def test_middleware_without_impl_and_without_handlers(self):
        @BaseMiddleware(self.resolver)
        class App(jj.App):
            resolver = self.resolver

        async with run(App()) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 404)

    async def test_middleware_without_impl_but_with_handlers(self):
        @BaseMiddleware(self.resolver)
        class App(jj.App):
            resolver = self.resolver
            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                return Response(status=200)

        async with run(App()) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 200)

    # App middleware

    async def test_app_middleware_without_handlers(self):
        mock = Mock()
    
        class Middleware(BaseMiddleware):
            async def do(self, request, handler, app):
                mock(request, handler, app)
                return await handler(request)

        @Middleware(self.resolver)
        class App(jj.App):
            resolver = self.resolver

        app = App()
        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 404)

        mock.assert_called_once()
        request_arg, handler_arg, app_arg = mock.call_args[0]
        self.assertIsInstance(request_arg, Request)
        self.assertEqual(handler_arg, default_handler)
        self.assertEqual(app_arg, app)

    async def test_app_middleware_with_handlers(self):
        mock = Mock()
    
        class Middleware(BaseMiddleware):
            async def do(self, r, h, a):
                mock(r, h, a)
                return await h(r)

        @Middleware(self.resolver)
        class App(jj.App):
            resolver = self.resolver
            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                return Response(status=200)

        app = App()
        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 200)

        mock.assert_called_once()
        request_arg, handler_arg, app_arg = mock.call_args[0]
        self.assertIsInstance(request_arg, Request)
        self.assertEqual(handler_arg, App.handler)
        self.assertEqual(app_arg, app)

    async def test_multiple_app_middlewares(self):
        mock = Mock()

        class Middleware1(BaseMiddleware):
            async def do(self, request, handler, app):
                mock(self.__class__.__name__, sentinel.BEFORE)
                response = await handler(request)
                mock(self.__class__.__name__, sentinel.AFTER)
                return response

        class Middleware2(Middleware1):
            pass

        @Middleware1(self.resolver)
        @Middleware2(self.resolver)
        class App(jj.App):
            resolver = self.resolver
            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                mock(App.__name__, sentinel.BEFORE)
                response = Response(status=200)
                mock(App.__name__, sentinel.AFTER)
                return response

        async with run(App()) as client:
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

    async def test_app_middleware_hook(self):
        mock = Mock()

        class Middleware(BaseMiddleware):
            def on_app(self, app):
                mock(app)
            def on_handler(self, handler):
                mock(handler)

        @Middleware(self.resolver)
        class App(jj.App):
            resolver = self.resolver

        async with run(App()) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 404)

        mock.assert_called_once_with(App)

    # Handler middleware

    async def test_handler_middleware(self):
        mock = Mock()
    
        class Middleware(BaseMiddleware):
            async def do(self, r, h, a):
                mock(r, h, a)
                return await h(r)

        class App(jj.App):
            resolver = self.resolver
            @PathMatcher("/path", resolver=resolver)
            @Middleware(resolver)
            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                return Response(status=200)

        app = App()
        async with run(app) as client:
            response = await client.get("/path")
            self.assertEqual(response.status, 200)

        mock.assert_called_once()
        request_arg, handler_arg, app_arg = mock.call_args[0]
        self.assertIsInstance(request_arg, Request)
        self.assertEqual(handler_arg, App.handler)
        self.assertEqual(app_arg, app)

    async def test_handler_middleware_hook(self):
        mock = Mock()

        class Middleware(BaseMiddleware):
            def on_app(self, app):
                mock(app)
            def on_handler(self, handler):
                mock(handler)

        class App(jj.App):
            resolver = self.resolver
            @Middleware(resolver)
            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                return Response(status=200)

        async with run(App()) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 200)

        mock.assert_called_once_with(App.handler)

    async def test_multiple_handler_middlewares(self):
        mock = Mock()

        class Middleware1(BaseMiddleware):
            async def do(self, request, handler, app):
                mock(self.__class__.__name__, sentinel.BEFORE)
                response = await handler(request)
                mock(self.__class__.__name__, sentinel.AFTER)
                return response

        class Middleware2(Middleware1):
            pass

        class App(jj.App):
            resolver = self.resolver
            @Middleware1(resolver)
            @MethodMatcher("*", resolver=resolver)
            @Middleware2(resolver)
            async def handler(request):
                mock(App.__name__, sentinel.BEFORE)
                response = Response(status=200)
                mock(App.__name__, sentinel.AFTER)
                return response

        async with run(App()) as client:
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

    # App + Handler middlewares

    async def test_app_and_handler_middlewares_priority(self):
        mock = Mock()

        class Middleware1(BaseMiddleware):
            async def do(self, request, handler, app):
                mock(self.__class__.__name__, sentinel.BEFORE)
                response = await handler(request)
                mock(self.__class__.__name__, sentinel.AFTER)
                return response

        class Middleware2(Middleware1):
            pass

        @Middleware1(self.resolver)
        class App(jj.App):
            resolver = self.resolver
            @MethodMatcher("*", resolver=resolver)
            @Middleware2(resolver)
            async def handler(request):
                mock(App.__name__, sentinel.BEFORE)
                response = Response(status=200)
                mock(App.__name__, sentinel.AFTER)
                return response

        async with run(App()) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 200)

        mock.assert_has_calls([
            call(Middleware1.__name__, sentinel.BEFORE),
            call(Middleware2.__name__, sentinel.BEFORE),
            call(App.__name__, sentinel.BEFORE),
            call(App.__name__, sentinel.AFTER),
            call(Middleware2.__name__, sentinel.AFTER),
            call(Middleware1.__name__, sentinel.AFTER),
        ])
        self.assertEqual(mock.call_count, 6)

    # Root + App + Handler middlewares

    async def test_root_and_app_and_handler_middlewares_priority(self):
        mock = Mock()

        class Do:
            async def do(self, request, handler, app):
                mock(self.__class__.__name__, sentinel.BEFORE)
                response = await handler(request)
                mock(self.__class__.__name__, sentinel.AFTER)
                return response

        class Middleware(Do, RootMiddleware):
            resolver = self.resolver

        class AppMiddleware(Do, BaseMiddleware):
            resolver = self.resolver

        class HandlerMiddleware(Do, BaseMiddleware):
            resolver = self.resolver

        @AppMiddleware()
        class App(jj.App):
            resolver = self.resolver
            @MethodMatcher("*", resolver=resolver)
            @HandlerMiddleware()
            async def handler(request):
                mock(App.__name__, sentinel.BEFORE)
                response = Response(status=200)
                mock(App.__name__, sentinel.AFTER)
                return response

        async with run(App(), middlewares=[Middleware()]) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 200)

        mock.assert_has_calls([
            call(AppMiddleware.__name__, sentinel.BEFORE),
            call(HandlerMiddleware.__name__, sentinel.BEFORE),
            call(Middleware.__name__, sentinel.BEFORE),
            call(App.__name__, sentinel.BEFORE),
            call(App.__name__, sentinel.AFTER),
            call(Middleware.__name__, sentinel.AFTER),
            call(HandlerMiddleware.__name__, sentinel.AFTER),
            call(AppMiddleware.__name__, sentinel.AFTER),
        ])
        self.assertEqual(mock.call_count, 8)
