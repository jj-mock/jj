import asynctest

import jj
from jj import server_version
from jj.apps import create_app
from jj.matchers import MethodMatcher
from jj.responses import StreamResponse
from jj.handlers import default_handler
from jj.resolvers import Registry, ReversedResolver

from .._test_utils import run


class TestStreamResponse(asynctest.TestCase):
    def make_app_with_response(self, *args, **kwargs):
        class App(jj.App):
            resolver = self.resolver
            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                return StreamResponse(*args, **kwargs)
        return App()

    def setUp(self):
        self.default_app = create_app()
        self.resolver = ReversedResolver(Registry(), self.default_app, default_handler)

    async def test_response_with_manual_preparing(self):
        body = b"200 OK"
        class App(jj.App):
            resolver = self.resolver
            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                stream = StreamResponse()
                await stream.prepare(request)
                await stream.write(body)
                await stream.write_eof()
                return stream

        async with run(App()) as client:
            response = await client.get("/")
            # status
            self.assertEqual(response.status, 200)
            self.assertEqual(response.reason, "OK")
            # headers
            self.assertEqual(response.headers.get("Server"), server_version)
            self.assertEqual(response.headers.get("Content-Type"), "application/octet-stream")
            self.assertEqual(response.headers.get("Transfer-Encoding"), "chunked")
            self.assertIsNotNone(response.headers.get("Date"))
            self.assertEqual(len(response.headers), 4)
            # body
            raw = await response.read()
            self.assertEqual(raw, body)

    async def test_response_with_default_args(self):
        app = self.make_app_with_response()

        async with run(app) as client:
            response = await client.get("/")
            # status
            self.assertEqual(response.status, 200)
            self.assertEqual(response.reason, "OK")
            # headers
            self.assertEqual(response.headers.get("Server"), server_version)
            self.assertEqual(response.headers.get("Content-Type"), "application/octet-stream")
            self.assertEqual(response.headers.get("Transfer-Encoding"), "chunked")
            self.assertIsNotNone(response.headers.get("Date"))
            self.assertEqual(len(response.headers), 4)
            # body
            raw = await response.read()
            self.assertEqual(raw, b"")

    # Status

    async def test_response_status(self):
        status = 204
        app = self.make_app_with_response(status=status)

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.status, status)
            # aiohttp автоматически подставляет нужный reason
            self.assertEqual(response.reason, "No Content")

    async def test_response_reason(self):
        status, reason = 204, "Custom Reason"
        app = self.make_app_with_response(status=status, reason=reason)

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.status, status)
            self.assertEqual(response.reason, reason)

    # Headers

    async def test_response_headers(self):
        custom_header_key, custom_header_val = "Cutom-Header", "Value"
        app = self.make_app_with_response(headers={custom_header_key: custom_header_val})

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.headers.get(custom_header_key), custom_header_val)
            self.assertEqual(response.headers.get("Server"), server_version)

    async def test_response_with_custom_server_header(self):
        server_header = "server version x"
        app = self.make_app_with_response(headers={"Server": server_header})

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.headers.get("Server"), server_header)

    async def test_response_with_expect_header(self):
        app = self.make_app_with_response()

        async with run(app) as client:
            response = await client.post("/", json={}, expect100=True)
            self.assertEqual(response.status, 200)

    async def test_response_with_incorrect_expect_header(self):
        app = self.make_app_with_response()

        async with run(app) as client:
            response = await client.post("/", json={}, headers={"Expect": "banana"})
            self.assertEqual(response.status, 417)
