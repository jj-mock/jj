import os

import asynctest

import jj
from jj import server_version
from jj.apps import create_app
from jj.matchers import MethodMatcher
from jj.responses import StaticResponse
from jj.handlers import default_handler
from jj.resolvers import Registry, ReversedResolver

from .._test_utils import run


class TestStaticResponse(asynctest.TestCase):
    def make_app_with_response(self, *args, **kwargs):
        class App(jj.App):
            resolver = self.resolver
            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                return StaticResponse(*args, **kwargs)
        return App()

    def make_path(self, path):
        return os.path.join(os.path.dirname(__file__), path)

    def setUp(self):
        self.default_app = create_app()
        self.resolver = ReversedResolver(Registry(), self.default_app, default_handler)

    # MimeType

    async def test_response_without_mimetype(self):
        path = self.make_path("fixtures/unknown_mime_type")
        with open(path, "rb") as f:
            body = f.read()
        app = self.make_app_with_response(path)

        async with run(app) as client:
            response = await client.get("/")
            # status
            self.assertEqual(response.status, 200)
            self.assertEqual(response.reason, "OK")
            # headers
            self.assertEqual(response.headers.get("Server"), server_version)
            self.assertEqual(response.headers.get("Content-Length"), str(len(body)))
            self.assertEqual(response.headers.get("Content-Type"), "application/octet-stream")
            self.assertEqual(response.headers.get("Accept-Ranges"), "bytes")
            self.assertIsNotNone(response.headers.get("Last-Modified"))
            self.assertIsNotNone(response.headers.get("Date"))
            self.assertEqual(len(response.headers), 6)
            # body
            raw = await response.read()
            self.assertEqual(raw, body)

    async def test_response_with_mimetype(self):
        path = self.make_path("fixtures/users.json")
        with open(path, "rb") as f:
            body = f.read()
        app = self.make_app_with_response(path)

        async with run(app) as client:
            response = await client.get("/")
            # status
            self.assertEqual(response.status, 200)
            self.assertEqual(response.reason, "OK")
            # headers
            self.assertEqual(response.headers.get("Server"), server_version)
            self.assertEqual(response.headers.get("Content-Length"), str(len(body)))
            self.assertEqual(response.headers.get("Content-Type"), "application/json")
            self.assertEqual(response.headers.get("Accept-Ranges"), "bytes")
            self.assertIsNotNone(response.headers.get("Last-Modified"))
            self.assertIsNotNone(response.headers.get("Date"))
            self.assertEqual(len(response.headers), 6)
            # body
            raw = await response.read()
            self.assertEqual(raw, body)

    # Attachment

    async def test_response_with_attachment(self):
        path = self.make_path("fixtures/users.json")
        app = self.make_app_with_response(path, attachment=True)

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.headers.get("Content-Type"), "application/json")
            self.assertEqual(response.headers.get("Content-Disposition"), "attachment")

    async def test_response_with_attachment_and_custom_header(self):
        path = self.make_path("fixtures/users.json")
        custom_header_key, custom_header_val = "Cutom-Header", "Value"
        app = self.make_app_with_response(path, attachment=True, headers={
            custom_header_key: custom_header_val
        })

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.headers.get("Content-Type"), "application/json")
            self.assertEqual(response.headers.get("Content-Disposition"), "attachment")
            self.assertEqual(response.headers.get(custom_header_key), custom_header_val)

    async def test_response_with_attachment_and_filename(self):
        path = self.make_path("fixtures/users.json")
        app = self.make_app_with_response(path, attachment="users.json")

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.headers.get("Content-Type"), "application/json")
            self.assertEqual(response.headers.get("Content-Disposition"),
                             'attachment; filename="users.json"')

    # Headers

    async def test_response_headers(self):
        path = self.make_path("fixtures/users.json")
        custom_header_key, custom_header_val = "Cutom-Header", "Value"
        app = self.make_app_with_response(path, headers={custom_header_key: custom_header_val})

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.headers.get(custom_header_key), custom_header_val)
            self.assertEqual(response.headers.get("Server"), server_version)

    async def test_response_with_custom_server_header(self):
        path = self.make_path("fixtures/users.json")
        server_header = "server version x"
        app = self.make_app_with_response(path, headers={"Server": server_header})

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.headers.get("Server"), server_header)

    async def test_response_with_expect_header(self):
        app = self.make_app_with_response(self.make_path("fixtures/users.json"))

        async with run(app) as client:
            response = await client.post("/", json={}, expect100=True)
            self.assertEqual(response.status, 200)

    async def test_response_with_incorrect_expect_header(self):
        app = self.make_app_with_response(self.make_path("fixtures/users.json"))

        async with run(app) as client:
            response = await client.post("/", json={}, headers={"Expect": "banana"})
            self.assertEqual(response.status, 417)
