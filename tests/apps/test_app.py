import asynctest
from asynctest import Mock, sentinel, call

import jj
from jj.apps import create_app
from jj.matchers import MethodMatcher, PathMatcher, ParamMatcher
from jj.resolvers import Registry, ReversedResolver
from jj.handlers import default_handler
from jj.responses import Response

from .._test_utils import run


class TestApp(asynctest.TestCase):
    def setUp(self):
        self.default_app = create_app()
        self.resolver = ReversedResolver(Registry(), self.default_app, default_handler)

    async def test_app_without_handlers(self):
        class App(jj.App):
            resolver = self.resolver

        async with run(App()) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 404)

    async def test_app_with_default_handler(self):
        status, text = 201, "text"
        class App(jj.App):
            resolver = self.resolver
            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                return Response(status=status, text=text)

        async with run(App()) as client:
            response = await client.get("/")
            self.assertEqual(response.status, status)
            self.assertEqual(await response.text(), text)

    async def test_app_with_single_handler(self):
        path, status, text = "/route", 201, "text"
        class App(jj.App):
            resolver = self.resolver
            @PathMatcher(path, resolver=resolver)
            async def handler(request):
                return Response(status=status, text=text)

        async with run(App()) as client:
            response = await client.get(path)
            self.assertEqual(response.status, status)
            self.assertEqual(await response.text(), text)

            response2 = await client.get("/")
            self.assertEqual(response2.status, 404)

    async def test_app_with_multiple_handlers(self):
        path1, status1, text1 = "/route", 201, "text-1"
        path2, status2, text2 = "/route/subroute", 202, "text-2"
        class App(jj.App):
            resolver = self.resolver
            @PathMatcher(path1, resolver=resolver)
            async def handler1(request):
                return Response(status=status1, text=text1)
            @PathMatcher(path2, resolver=resolver)
            async def handler2(request):
                return Response(status=status2, text=text2)

        async with run(App()) as client:
            response1 = await client.get(path1)
            self.assertEqual(response1.status, status1)
            self.assertEqual(await response1.text(), text1)

            response2 = await client.get(path2)
            self.assertEqual(response2.status, status2)
            self.assertEqual(await response2.text(), text2)

    async def test_app_handlers_priority(self):
        path = "/route"
        status1, text1 = 201, "text-1"
        status2, text2 = 202, "text-2"
        class App(jj.App):
            resolver = self.resolver
            @PathMatcher(path, resolver=resolver)
            async def handler1(request):
                return Response(status=status1, text=text1)
            @PathMatcher(path, resolver=resolver)
            async def handler2(request):
                return Response(status=status2, text=text2)

        async with run(App()) as client:
            response = await client.get(path)
            self.assertEqual(response.status, status1)
            self.assertEqual(await response.text(), text1)

    async def test_handler_with_matcher_and_decorators(self):
        mock = Mock()

        def decorator_before(fn):
            async def before_handler(request):
                mock(sentinel.BEFORE)
                return await fn(request)
            return before_handler

        def decorator_after(fn):
            async def after_handler(request):
                mock(sentinel.AFTER)
                return await fn(request)
            return after_handler

        path, status, text = "/route", 201, "text"
        class App(jj.App):
            resolver = self.resolver
            @decorator_after
            @PathMatcher(path, resolver=resolver)
            @decorator_before
            async def handler(request):
                mock(sentinel.HANDLE)
                return Response(status=status, text=text)

        async with run(App()) as client:
            response = await client.get(path)
            self.assertEqual(response.status, status)
            self.assertEqual(await response.text(), text)

            response2 = await client.get("/")
            self.assertEqual(response2.status, 404)

        mock.assert_has_calls([
            call(sentinel.AFTER),
            call(sentinel.BEFORE),
            call(sentinel.HANDLE)
        ])
        self.assertEqual(mock.call_count, 3)

    async def test_handler_with_matchers_and_decorator(self):
        mock = Mock()

        def decorator(fn):
            async def handler(request):
                mock()
                return await fn(request)
            return handler

        status, text = 201, "text"
        class App(jj.App):
            resolver = self.resolver
            @ParamMatcher({"key2": "2"}, resolver=resolver)
            @decorator
            @ParamMatcher({"key1": "1"}, resolver=resolver)
            async def handler(request):
                return Response(status=status, text=text)

        async with run(App()) as client:
            response0 = await client.get("/", params={})
            self.assertEqual(response0.status, 404)

            response1 = await client.get("/", params={"key1": "1"})
            self.assertEqual(response1.status, 404)

            response2 = await client.get("/", params={"key1": "1", "key2": "2"})
            self.assertEqual(response2.status, status)
            self.assertEqual(await response2.text(), text)

    async def test_app_inheritance(self):
        path, status, text = "/route", 201, "text"
        class App(jj.App):
            resolver = self.resolver
            @PathMatcher(path, resolver=resolver)
            async def handler(request):
                return Response(status=status, text=text)

        class AnotherApp(App):
            pass

        async with run(AnotherApp()) as client:
            response = await client.get(path)
            self.assertEqual(response.status, status)
            self.assertEqual(await response.text(), text)

            response2 = await client.get("/")
            self.assertEqual(response2.status, 404)

    async def test_app_inheritance_with_handler_overriding(self):
        path = "/route"
        status1, text1 = 201, "text-1"
        status2, text2 = 202, "text-2"
        class App(jj.App):
            resolver = self.resolver
            @PathMatcher(path, resolver=self.resolver)
            async def handler(request):
                return Response(status=status1, text=text1)

        class AnotherApp(App):
            @PathMatcher(path, resolver=self.resolver)
            async def handler(request):
                return Response(status=status2, text=text2)

        async with run(AnotherApp(), self.resolver) as client:
            response = await client.get(path)
            self.assertEqual(response.status, status2)
            self.assertEqual(await response.text(), text2)

        async with run(App(), self.resolver) as client:
            response = await client.get(path)
            self.assertEqual(response.status, status1)
            self.assertEqual(await response.text(), text1)

    async def test_app_inheritance_with_default_handler_overriding(self):
        status1, text1 = 201, "text-1"
        status2, text2 = 202, "text-2"
        status3, text3 = 203, "text-3"
        class App(jj.App):
            resolver = self.resolver
            @MethodMatcher("*", resolver=self.resolver)
            async def other(request):
                return Response(status=status1, text=text1)

        class AnotherApp(App):
            @PathMatcher("/route", resolver=self.resolver)
            async def handler(request):
                return Response(status=status2, text=text2)
            @MethodMatcher("*", resolver=self.resolver)
            async def other(request):
                return Response(status=status3, text=text3)

        async with run(AnotherApp(), self.resolver) as client:
            response = await client.get("/route")
            self.assertEqual(response.status, status2)
            self.assertEqual(await response.text(), text2)

            response2 = await client.get("/")
            self.assertEqual(response2.status, status3)
            self.assertEqual(await response2.text(), text3)

        async with run(App(), self.resolver) as client:
            response = await client.get("/other")
            self.assertEqual(response.status, status1)
            self.assertEqual(await response.text(), text1)

    async def test_app_multiple_inheritance(self):
        path1, status1, text1 = "/route-1", 201, "text-1"
        path2, status2, text2 = "/route-2", 202, "text-2"
        class App(jj.App):
            resolver = self.resolver
            @PathMatcher(path1, resolver=self.resolver)
            async def handler(request):
                return Response(status=status1, text=text1)

        class AnotherApp(jj.App):
            @PathMatcher(path2, resolver=self.resolver)
            async def handler(request):
                return Response(status=status2, text=text2)

        class ChildApp(App, AnotherApp):
            pass

        async with run(ChildApp(), self.resolver) as client:
            response = await client.get(path1)
            self.assertEqual(response.status, status1)
            self.assertEqual(await response.text(), text1)

            response2 = await client.get(path2)
            self.assertEqual(response2.status, status2)
            self.assertEqual(await response2.text(), text2)

    async def test_app_setter(self):
        path, status, text = "/route", 201, "text"
        @PathMatcher(path, resolver=self.resolver)
        async def handler(request):
            return Response(status=status, text=text)

        class App(jj.App):
            resolver = self.resolver
        App.handler = handler

        async with run(App(), self.resolver) as client:
            response = await client.get(path)
            self.assertEqual(response.status, status)
            self.assertEqual(await response.text(), text)

        async with run(self.default_app, self.resolver) as client:
            response = await client.get(path)
            self.assertEqual(response.status, 404)

    async def test_app_instance_setter(self):
        path, status, text = "/route", 201, "text"
        @PathMatcher(path, resolver=self.resolver)
        async def handler(request):
            return Response(status=status, text=text)

        class App(jj.App):
            resolver = self.resolver
        app = App()
        app.handler = handler

        async with run(app, self.resolver) as client:
            response = await client.get(path)
            self.assertEqual(response.status, status)
            self.assertEqual(await response.text(), text)

        async with run(self.default_app, self.resolver) as client:
            response = await client.get(path)
            self.assertEqual(response.status, 404)
