from unittest import IsolatedAsyncioTestCase as TestCase

import pytest

import jj
from jj import server_version
from jj.apps import create_app
from jj.handlers import default_handler
from jj.matchers import MethodMatcher
from jj.resolvers import Registry, ReversedResolver
from jj.responses import TemplateResponse

from .._test_utils import run


class TestTemplateResponse(TestCase):
    def make_app_with_response(self, *args, **kwargs):
        class App(jj.App):
            resolver = self.resolver

            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                return TemplateResponse(*args, **kwargs)
        return App()

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

    # status

    @pytest.mark.asyncio
    async def test_response_status(self):
        status = 204
        app = self.make_app_with_response(status=status)

        async with run(app) as client:
            response = await client.get("/")
            self.assertEqual(response.status, status)
            # aiohttp automatically sets the reason
            self.assertEqual(response.reason, "No Content")

    @pytest.mark.asyncio
    async def test_response_template_status(self):
        tmpl_status = "{{ request.query['status'] }}"
        app = self.make_app_with_response(status=tmpl_status)

        status = 204

        async with run(app) as client:
            response = await client.get("/", params={"status": status})
            self.assertEqual(response.status, status)
            # aiohttp automatically sets the reason
            self.assertEqual(response.reason, "No Content")

    # headers

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
    async def test_response_template_headers(self):
        app = self.make_app_with_response(headers={
            "X-Header-{{ request.query['header_key'] }}": "{{ request.query['header_val'] }}"
        })

        header_key = "Key"
        header_val = "Value"

        async with run(app) as client:
            response = await client.get("/", params={
                "header_key": header_key,
                "header_val": header_val
            })
            self.assertEqual(response.headers.get(f"X-Header-{header_key}"), header_val)
            self.assertEqual(response.headers.get("Server"), server_version)

    # body

    @pytest.mark.asyncio
    async def test_response_template_body(self):
        headers = {"Content-Type": "application/json"}
        app = self.make_app_with_response(headers=headers, body="""
            [
                {% for user_id in request.query.getall('user_id') %}
                    {"id": "{{ user_id }}"}{% if not loop.last %},{% endif %}
                {% endfor %}
            ]
        """)

        async with run(app) as client:
            response = await client.get("/", params=[("user_id", "1"), ("user_id", "2")])
            self.assertEqual(await response.json(), [
                {"id": "1"},
                {"id": "2"},
            ])

            self.assertTrue(response.headers.get("Content-Length"))
            self.assertEqual(response.headers.get("Content-Type"), "application/json")

    # pack / unpack

    def test_pack_default(self):
        response = TemplateResponse()

        actual = response.__packed__()

        self.assertEqual(actual, {
            "body": "",
            "headers": [],
            "status": "200",
        })

    def test_pack(self):
        response = TemplateResponse(
            body="body",
            headers=[("key1", "val1"), ("key2", "val2")],
            status=204,
        )

        actual = response.__packed__()

        self.assertEqual(actual, {
            "body": "body",
            "headers": [["key1", "val1"], ["key2", "val2"]],
            "status": "204",
        })

    def test_unpack(self):
        packed = {
            "body": "body",
            "headers": [["key1", "val1"], ["key2", "val2"]],
            "status": "204",
        }

        response = TemplateResponse.__unpacked__(**packed)

        self.assertEqual(response.__packed__(), packed)

    # copy

    def test_copy(self):
        response = TemplateResponse(
            body="body",
            headers=[("key1", "val1"), ("key2", "val2")],
            status=204,
        )

        actual = response.copy()

        self.assertEqual(actual.__packed__(), response.__packed__())
        self.assertIsNot(actual, response)
