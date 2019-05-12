import asynctest
from aiohttp import FormData

import jj
from jj.apps import create_app
from jj.matchers import MethodMatcher
from jj.responses import TunnelResponse, Response
from jj.handlers import default_handler
from jj.resolvers import Registry, ReversedResolver
from jj.http.methods import GET, DELETE, POST

from .._test_utils import run, TestServer
from ._request_formatter import RequestFormatter


class TestTunnelResponse(asynctest.TestCase):
    def make_app_with_response(self, *args, **kwargs):
        class App(jj.App):
            resolver = self.resolver
            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                return TunnelResponse(*args, **kwargs)
        return App()

    def make_debug_app(self):
        @MethodMatcher("*", resolver=self.resolver)
        async def handler(request):
            payload = await RequestFormatter(request).format()
            return Response(json=payload)
        return create_app(resolver=self.resolver, handlers={"handler": handler})

    def setUp(self):
        self.default_app = create_app()
        self.resolver = ReversedResolver(Registry(), self.default_app, default_handler)

    # Method

    async def test_get_request(self):
        debug_app = self.make_debug_app()
        async with TestServer(debug_app) as server:
            url = str(server.make_url("/"))
            app = self.make_app_with_response(target=url)

            async with run(app) as client:
                response = await client.request(GET, "/")
                body = await response.json()
                self.assertEqual(body["method"], GET)

    async def test_delete_request(self):
        debug_app = self.make_debug_app()
        async with TestServer(debug_app) as server:
            url = str(server.make_url("/"))
            app = self.make_app_with_response(target=url)

            async with run(app) as client:
                response = await client.request(DELETE, "/")
                body = await response.json()
                self.assertEqual(body["method"], DELETE)

    # Body

    async def test_post_request_with_no_data(self):
        debug_app = self.make_debug_app()
        async with TestServer(debug_app) as server:
            url = str(server.make_url("/"))
            app = self.make_app_with_response(target=url)

            async with run(app) as client:
                response = await client.request(POST, "/")
                body = await response.json()
                self.assertEqual(body["method"], POST)
                self.assertEqual(body["data"], None)

    async def test_request_with_post_data(self):
        debug_app = self.make_debug_app()
        async with TestServer(debug_app) as server:
            url = str(server.make_url("/"))
            app = self.make_app_with_response(target=url)
            payload = FormData([
                ("field1", "value1"),
                ("field1", "value2"),
                ("field2", "null"),
            ])

            async with run(app) as client:
                response = await client.request(POST, "/", data=payload)
                body = await response.json()
                self.assertEqual(body["method"], POST)
                self.assertEqual(body["data"], {
                    "field1": ["value1", "value2"],
                    "field2": ["null"],
                })

    async def test_request_with_form_data(self):
        debug_app = self.make_debug_app()
        async with TestServer(debug_app) as server:
            url = str(server.make_url("/"))
            app = self.make_app_with_response(target=url)
            payload = FormData([
                ("field1", "value1"),
                ("field1", "value2"),
                ("field2", "null"),
            ])
            payload._is_multipart = True

            async with run(app) as client:
                response = await client.request(POST, "/", data=payload)
                body = await response.json()
                self.assertEqual(body["method"], POST)
                self.assertEqual(body["form"], {
                    "field1": ["value1", "value2"],
                    "field2": ["null"],
                })

    async def test_request_with_file(self):
        debug_app = self.make_debug_app()
        async with TestServer(debug_app) as server:
            url = str(server.make_url("/"))
            app = self.make_app_with_response(target=url)
            payload = FormData()
            payload.add_field("field1", "value1")
            payload.add_field("field2", b"binary", content_type="image/jpeg", filename="image.jpg")

            async with run(app) as client:
                response = await client.request(POST, "/", data=payload)
                body = await response.json()
                self.assertEqual(body["method"], POST)
                self.assertEqual(body["form"], {
                    "field1": ["value1"],
                    "field2": [{
                        "name": "image.jpg",
                        "size": str(len(b"binary")),
                        "type": "image/jpeg",
                    }],
                })

    async def test_request_with_json_data(self):
        debug_app = self.make_debug_app()
        async with TestServer(debug_app) as server:
            url = str(server.make_url("/"))
            app = self.make_app_with_response(target=url)
            payload = {"field1": "value1", "field2": None}
            payload_serialized = '{"field1": "value1", "field2": null}'

            async with run(app) as client:
                response = await client.request(POST, "/", json=payload)
                body = await response.json()
                self.assertEqual(body["method"], POST)
                self.assertEqual(body["headers"].get("Content-Type"), ["application/json"])
                self.assertEqual(body["raw"], payload_serialized)

    async def test_request_with_binary_data(self):
        debug_app = self.make_debug_app()
        async with TestServer(debug_app) as server:
            url = str(server.make_url("/"))
            app = self.make_app_with_response(target=url)

            async with run(app) as client:
                response = await client.request(POST, "/", data=b"binary")
                body = await response.json()
                self.assertEqual(body["method"], POST)
                self.assertEqual(body["headers"].get("Content-Type"), ["application/octet-stream"])
                self.assertEqual(body["raw"], "binary")

    # Path

    async def test_request_with_custom_path(self):
        debug_app = self.make_debug_app()
        async with TestServer(debug_app) as server:
            url = str(server.make_url("/"))
            app = self.make_app_with_response(target=url)
            path = "/users/1234"

            async with run(app) as client:
                response = await client.request(GET, path)
                body = await response.json()
                self.assertEqual(body["method"], GET)
                self.assertEqual(body["path"], path)

    # Params

    async def test_request_with_custom_query_params(self):
        debug_app = self.make_debug_app()
        async with TestServer(debug_app) as server:
            url = str(server.make_url("/"))
            app = self.make_app_with_response(target=url)
            params = [
                ("field1", "value1"),
                ("field1", "value2"),
                ("field2", "null"),
            ]

            async with run(app) as client:
                response = await client.request(GET, "/", params=params)
                body = await response.json()
                self.assertEqual(body["method"], GET)
                self.assertEqual(body["params"], {
                    "field1": ["value1", "value2"],
                    "field2": ["null"],
                })

    # Headers

    async def test_request_with_custom_headers(self):
        debug_app = self.make_debug_app()
        async with TestServer(debug_app) as server:
            url = str(server.make_url("/"))
            app = self.make_app_with_response(target=url)
            headers = [
                ("x-header-1", "value1"),
                ("x-header-1", "value2"),
                ("x-header-2", "null"),
            ]

            async with run(app) as client:
                response = await client.request(GET, "/", headers=headers)
                body = await response.json()
                self.assertEqual(body["method"], GET)
                # aiohttp client не умеет отправлять несколько заголовков с одним названием,
                # однако aiohttp server умеет их принимать
                self.assertEqual(body["headers"].get("x-header-1"), ["value2"])
                self.assertEqual(body["headers"].get("x-header-2"), ["null"])

    async def test_request_default_headers(self):
        debug_app = self.make_debug_app()
        async with TestServer(debug_app) as server:
            url = str(server.make_url("/"))
            app = self.make_app_with_response(target=url)

            async with run(app) as client:
                response = await client.request(GET, "/")
                body = await response.json()
                self.assertEqual(body["headers"].get("Host"), ["{}:{}".format(server.host, server.port)])
                self.assertEqual(body["headers"].get("Accept"), ["*/*"])
                self.assertEqual(body["headers"].get("Accept-Encoding"), ["gzip, deflate"])
                self.assertEqual(body["headers"].get("Content-Type"), ["application/octet-stream"])
                self.assertEqual(body["headers"].get("Transfer-Encoding"), ["chunked"])
                self.assertIsNotNone(body["headers"].get("User-Agent"))
                self.assertEqual(len(body["headers"]), 6)
