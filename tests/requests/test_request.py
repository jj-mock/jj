from unittest import IsolatedAsyncioTestCase as TestCase

import pytest
from multidict import MultiDictProxy

import jj
from jj.apps import create_app
from jj.handlers import default_handler
from jj.matchers import MethodMatcher, PathMatcher
from jj.resolvers import Registry, ReversedResolver
from jj.responses import Response

from .._test_utils import run


class TestRequest(TestCase):
    def setUp(self):
        self.default_app = create_app()
        self.resolver = ReversedResolver(Registry(), self.default_app, default_handler)

    # params

    @pytest.mark.asyncio
    async def test_request_params_without_query(self):
        class App(jj.App):
            resolver = self.resolver

            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                self.assertIsInstance(request.params, MultiDictProxy)
                self.assertEqual(request.params, {})
                return Response(status=200)

        async with run(App()) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 200)

    @pytest.mark.asyncio
    async def test_request_params_with_query(self):
        params = {"key1": "1", "key2": "2"}

        class App(jj.App):
            resolver = self.resolver

            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                self.assertIsInstance(request.params, MultiDictProxy)
                self.assertEqual(request.params, params)
                return Response(status=200)

        async with run(App()) as client:
            response = await client.get("/", params=params)
            self.assertEqual(response.status, 200)

    # segments

    @pytest.mark.asyncio
    async def test_request_without_segments(self):
        class App(jj.App):
            resolver = self.resolver

            @PathMatcher("/users/1", resolver=resolver)
            async def handler(request):
                self.assertIsInstance(request.segments, dict)
                self.assertEqual(request.segments, {})
                return Response(status=200)

        async with run(App()) as client:
            response = await client.get("/users/1")
            self.assertEqual(response.status, 200)

    @pytest.mark.asyncio
    async def test_request_with_segments(self):
        class App(jj.App):
            resolver = self.resolver

            @PathMatcher("/users/{user_id}", resolver=resolver)
            async def handler(request):
                self.assertIsInstance(request.segments, dict)
                self.assertEqual(request.segments, {"user_id": "1"})
                return Response(status=200)

        async with run(App()) as client:
            response = await client.get("/users/1")
            self.assertEqual(response.status, 200)

    @pytest.mark.asyncio
    async def test_request_segments_with_other_matchers(self):
        class App(jj.App):
            resolver = self.resolver

            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                self.assertIsInstance(request.segments, dict)
                self.assertEqual(request.segments, {})
                return Response(status=200)

        async with run(App()) as client:
            response = await client.get("/users/1")
            self.assertEqual(response.status, 200)

    @pytest.mark.asyncio
    async def test_request_raw_data(self):
        raw_bytes = b"sample raw data"

        class App(jj.App):
            resolver = self.resolver

            @MethodMatcher("POST", resolver=resolver)
            async def handler(request):
                await request.read()
                self.assertEqual(request.raw_data, raw_bytes)
                return Response(status=200)

        async with run(App()) as client:
            response = await client.post("/", data=raw_bytes)
            self.assertEqual(response.status, 200)

    @pytest.mark.asyncio
    async def test_request_post_data(self):
        form_data = {"key": "value"}

        class App(jj.App):
            resolver = self.resolver

            @MethodMatcher("POST", resolver=resolver)
            async def handler(request):
                await request.post()
                self.assertIsInstance(request.post_data, MultiDictProxy)
                self.assertEqual(dict(request.post_data), form_data)
                return Response(status=200)

        async with run(App()) as client:
            response = await client.post("/", data=form_data)
            self.assertEqual(response.status, 200)

    @pytest.mark.asyncio
    async def test_request_json_data(self):
        json_body = {"key": "value"}

        class App(jj.App):
            resolver = self.resolver

            @MethodMatcher("POST", resolver=resolver)
            async def handler(request):
                await request.read()
                self.assertEqual(request.json_data, json_body)
                return Response(status=200)

        async with run(App()) as client:
            response = await client.post("/", json=json_body)
            self.assertEqual(response.status, 200)
