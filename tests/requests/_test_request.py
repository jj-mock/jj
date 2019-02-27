import asynctest
from asynctest import sentinel

from multidict import MultiDictProxy

import jj
from jj.apps import create_app
from jj.matchers import MethodMatcher
from jj.responses import Response
from jj.handlers import default_handler
from jj.resolvers import Registry, ReversedResolver

from .._test_utils import run


class TestRequest(asynctest.TestCase):
    def setUp(self):
        self.default_app = create_app()
        self.resolver = ReversedResolver(Registry(), self.default_app, default_handler)

    async def test_request_params_without_query(self):
        class App(jj.App):
            resolver = self.resolver
            @MethodMatcher(self.resolver, "*")
            async def handler(request):
                self.assertIsInstance(request.params, MultiDictProxy)
                self.assertEqual(request.params, {})
                return Response(status=200)

        async with run(App()) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 200)

    async def test_request_params_with_query(self):
        params = {"key1": "1", "key2": "2"}

        class App(jj.App):
            resolver = self.resolver
            @MethodMatcher(self.resolver, "*")
            async def handler(request):
                self.assertIsInstance(request.params, MultiDictProxy)
                self.assertEqual(request.params, params)
                return Response(status=200)

        async with run(App()) as client:
            response = await client.get("/", params=params)
            self.assertEqual(response.status, 200)
