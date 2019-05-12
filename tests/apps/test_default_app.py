import asynctest

import jj
from jj.apps import create_app, DefaultApp
from jj.matchers import PathMatcher
from jj.resolvers import Registry, ReversedResolver
from jj.handlers import default_handler
from jj.responses import Response

from .._test_utils import run


class TestDefaultApp(asynctest.TestCase):
    def setUp(self):
        self.default_app = create_app()
        self.resolver = ReversedResolver(Registry(), self.default_app, default_handler)

    def test_default_app_is_singleton(self):
        self.assertEqual(DefaultApp(), DefaultApp())

    async def test_default_app_with_handler(self):
        path, status, text = "/route", 201, "text"
        @PathMatcher(path, resolver=self.resolver)
        async def handler(request):
            return Response(status=status, text=text)

        async with run(self.default_app, self.resolver) as client:
            response = await client.get(path)
            self.assertEqual(response.status, status)
            self.assertEqual(await response.text(), text)

    async def test_default_app_without_handlers(self):
        path, status, text = "/route", 201, "text"
        class App(jj.App):
            resolver = self.resolver
            @PathMatcher(path, resolver=resolver)
            async def handler(request):
                return Response(status=status, text=text)

        async with run(self.default_app, self.resolver) as client:
            response = await client.get(path)
            self.assertEqual(response.status, 404)

    async def test_default_app(self):
        path = "/route"
        status1, text1 = 201, "text-1"
        status2, text2 = 202, "text-2"

        @PathMatcher(path, resolver=self.resolver)
        async def handler(request):
            return Response(status=status1, text=text1)

        class App(jj.App):
            resolver = self.resolver
            @PathMatcher(path, resolver=resolver)
            async def handler(request):
                return Response(status=status2, text=text2)

        async with run(self.default_app, self.resolver) as client:
            response = await client.get(path)
            self.assertEqual(response.status, status1)
            self.assertEqual(await response.text(), text1)

        async with run(App(), self.resolver) as client:
            response = await client.get(path)
            self.assertEqual(response.status, status2)
            self.assertEqual(await response.text(), text2)
