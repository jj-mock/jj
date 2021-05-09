import os
import sys

if sys.version_info >= (3, 8):
    from unittest import IsolatedAsyncioTestCase as TestCase
else:
    from unittest import TestCase

import pytest

import jj
from jj import server_version
from jj.apps import create_app
from jj.handlers import default_handler
from jj.matchers import MethodMatcher
from jj.resolvers import Registry, ReversedResolver
from jj.responses import Response

from .._test_utils import run


class TestResponse(TestCase):
    def make_app_with_response(self, *args, **kwargs):
        class App(jj.App):
            resolver = self.resolver

            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                return Response(*args, **kwargs)
        return App()

    def make_path(self, path):
        return os.path.join(os.path.dirname(__file__), path)

    def setUp(self):
        self.default_app = create_app()
        self.resolver = ReversedResolver(Registry(), self.default_app, default_handler)

    @pytest.mark.asyncio
    async def test_response_with_default_args(self):
        app = self.make_app_with_response()

        async with run(app) as client:
            response = await client.get("/")
            # status
            self.assertEqual(response.status, 200)
            self.assertEqual(response.reason, "OK")
            # headers
            self.assertEqual(response.headers.get("Server"), server_version)
            self.assertEqual(response.headers.get("Content-Length"), "0")
            self.assertEqual(response.headers.get("Content-Type"), "text/plain; charset=utf-8")
            self.assertIsNotNone(response.headers.get("Date"))
            self.assertEqual(len(response.headers), 4)
            # body
            raw = await response.read()
            self.assertEqual(raw, b"")

    @pytest.mark.asyncio
    async def test_response_with_conflicted_args(self):
        payload = "200 OK"

        with self.assertRaises(Exception):
            Response(text=payload, body=payload)

        with self.assertRaises(Exception):
            Response(text=payload, json=payload)

        with self.assertRaises(Exception):
            Response(body=payload, json=payload)

    # Status

    @pytest.mark.asyncio
    async def test_response_status(self):
        status = 204
        app = self.make_app_with_response(status=status)

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.status, status)
            # aiohttp автоматически подставляет нужный reason
            self.assertEqual(response.reason, "No Content")

    @pytest.mark.asyncio
    async def test_response_reason(self):
        status, reason = 204, "Custom Reason"
        app = self.make_app_with_response(status=status, reason=reason)

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.status, status)
            self.assertEqual(response.reason, reason)

    # Body

    @pytest.mark.asyncio
    async def test_response_body(self):
        body = "200 OK"
        binary_body = b"200 OK"
        app = self.make_app_with_response(body=body)

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(await response.text(), body)
            self.assertEqual(await response.read(), binary_body)

            self.assertEqual(response.headers.get("Content-Length"), str(len(body)))
            self.assertEqual(response.headers.get("Content-Type"), "text/plain; charset=utf-8")

    @pytest.mark.asyncio
    async def test_response_text_body(self):
        text = "200 OK"
        binary_text = b"200 OK"
        app = self.make_app_with_response(text=text)

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(await response.text(), text)
            self.assertEqual(await response.read(), binary_text)

            self.assertEqual(response.headers.get("Content-Length"), str(len(text)))
            self.assertEqual(response.headers.get("Content-Type"), "text/plain; charset=utf-8")

    @pytest.mark.asyncio
    async def test_response_json_body(self):
        json = {"key": None}
        dumped_json = '{"key": null}'
        binary_json = b'{"key": null}'
        app = self.make_app_with_response(json=json)

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(await response.json(), json)
            self.assertEqual(await response.text(), dumped_json)
            self.assertEqual(await response.read(), binary_json)

            self.assertEqual(response.headers.get("Content-Length"), str(len(dumped_json)))
            self.assertEqual(response.headers.get("Content-Type"), "application/json")

    @pytest.mark.asyncio
    async def test_response_json_body_with_custom_content_type(self):
        json = {"key": None}
        dumped_json = '{"key": null}'
        binary_json = b'{"key": null}'
        content_type = "text/plain"
        app = self.make_app_with_response(json=json, headers={"Content-Type": content_type})

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(await response.text(), dumped_json)
            self.assertEqual(await response.read(), binary_json)

            self.assertEqual(response.headers.get("Content-Length"), str(len(dumped_json)))
            self.assertEqual(response.headers.get("Content-Type"), content_type)

    @pytest.mark.asyncio
    async def test_response_null_json_body(self):
        json = None
        dumped_json = 'null'
        binary_json = b'null'
        app = self.make_app_with_response(json=json)

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(await response.json(), json)
            self.assertEqual(await response.text(), dumped_json)
            self.assertEqual(await response.read(), binary_json)

            self.assertEqual(response.headers.get("Content-Length"), str(len(dumped_json)))
            self.assertEqual(response.headers.get("Content-Type"), "application/json")

    @pytest.mark.asyncio
    async def test_response_binary_body(self):
        body = b"200 OK"
        app = self.make_app_with_response(body=body)

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(await response.text(), body.decode())
            self.assertEqual(await response.read(), body)

            self.assertEqual(response.headers.get("Content-Length"), str(len(body)))
            self.assertEqual(response.headers.get("Content-Type"), "application/octet-stream")

    @pytest.mark.asyncio
    async def test_response_predefined_text_body(self):
        path = self.make_path("fixtures/users.json")
        with open(path, "rt") as f:
            body = f.read()
        app = self.make_app_with_response(body=open(path, "rt"))

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(await response.text(), body)
            self.assertEqual(response.headers.get("Content-Length"), str(len(body)))
            self.assertEqual(response.headers.get("Content-Type"), "text/plain; charset=utf-8")
            self.assertEqual(response.headers.get("Content-Disposition"), "inline")

    @pytest.mark.asyncio
    async def test_response_predefined_binary_body(self):
        path = self.make_path("fixtures/users.json")
        with open(path, "rb") as f:
            body = f.read()
        app = self.make_app_with_response(body=open(path, "rb"))

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(await response.text(), body.decode())
            self.assertEqual(await response.read(), body)
            self.assertEqual(response.headers.get("Content-Length"), str(len(body)))
            self.assertEqual(response.headers.get("Content-Type"), "application/json")
            self.assertEqual(response.headers.get("Content-Disposition"), "inline")

    # Headers

    @pytest.mark.asyncio
    async def test_response_header(self):
        custom_header_key, custom_header_val = "Cutom-Header", "Value"
        app = self.make_app_with_response(headers={custom_header_key: custom_header_val})

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.headers.get(custom_header_key), custom_header_val)
            self.assertEqual(response.headers.get("Server"), server_version)

    @pytest.mark.asyncio
    async def test_response_headers(self):
        custom_header1_key, custom_header1_val = "Cutom-Header", "Value1"
        custom_header2_key, custom_header2_val = "Cutom-Header", "Value2"
        app = self.make_app_with_response(headers=[
            (custom_header1_key, custom_header1_val),
            (custom_header2_key, custom_header2_val),
        ])

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.headers.getall(custom_header1_key),
                             [custom_header1_val, custom_header2_val])
            self.assertEqual(response.headers.get("Server"), server_version)

    @pytest.mark.asyncio
    async def test_response_with_custom_server_header(self):
        server_header = "server version x"
        app = self.make_app_with_response(headers={"Server": server_header})

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.headers.get("Server"), server_header)

    @pytest.mark.asyncio
    async def test_response_with_expect_header(self):
        app = self.make_app_with_response()

        async with run(app) as client:
            response = await client.post("/", json={}, expect100=True)
            self.assertEqual(response.status, 200)

    @pytest.mark.asyncio
    async def test_response_with_incorrect_expect_header(self):
        app = self.make_app_with_response()

        async with run(app) as client:
            response = await client.post("/", json={}, headers={"Expect": "banana"})
            self.assertEqual(response.status, 417)
