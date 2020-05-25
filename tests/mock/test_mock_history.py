import pytest
from aiohttp import FormData

import jj
from jj.middlewares import SelfMiddleware
from jj.mock import Mock, RemoteMock

from .._test_utils import run


@pytest.mark.asyncio
async def test_mock_history_request():
    mock = Mock()
    self_middleware = SelfMiddleware(Mock().resolver)
    matcher, response = jj.match("*"), jj.Response(status=200, body=b"text")

    async with run(mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        async with handler:
            resp = await client.get("/", params={"key": "val"})
            assert resp.status == 200

            history = await handler.history()
            req = history[0]["request"]
            assert req.method == "GET"
            assert req.path == "/"
            assert req.params == {"key": "val"}
            assert req.body == b""

            res = history[0]["response"]
            assert res.status == 200
            assert res.reason == "OK"
            assert res.body == b"text"


@pytest.mark.asyncio
async def test_mock_history_multiple_requests():
    mock = Mock()
    self_middleware = SelfMiddleware(Mock().resolver)
    matcher, response = jj.match("*"), jj.Response()

    async with run(mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        async with handler:
            resp1 = await client.get("/path1")
            assert resp1.status == 200

            resp2 = await client.get("/path2")
            assert resp2.status == 200

            history = await handler.history()
            req1 = history[-1]["request"]
            assert req1.method == "GET"
            assert req1.path == "/path1"

            req = history[0]["request"]
            assert req.method == "GET"
            assert req.path == "/path2"


@pytest.mark.asyncio
async def test_mock_history_post_no_data():
    mock = Mock()
    self_middleware = SelfMiddleware(Mock().resolver)
    matcher, response = jj.match("*"), jj.Response()

    async with run(mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        async with handler:
            resp = await client.post("/")
            assert resp.status == 200

            history = await handler.history()
            req = history[0]["request"]
            assert req.method == "POST"
            assert req.path == "/"
            assert req.body == b""


@pytest.mark.asyncio
async def test_mock_history_post_json():
    mock = Mock()
    self_middleware = SelfMiddleware(Mock().resolver)
    matcher, response = jj.match("*"), jj.Response()

    payload = {
        "field1": "value1",
        "field2": None,
    }
    async with run(mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        async with handler:
            resp = await client.post("/", json=payload)
            assert resp.status == 200

            history = await handler.history()
            req = history[0]["request"]
            assert req.method == "POST"
            assert req.path == "/"
            assert req.body == b'{"field1": "value1", "field2": null}'


@pytest.mark.asyncio
async def test_mock_history_post_data():
    mock = Mock()
    self_middleware = SelfMiddleware(Mock().resolver)
    matcher, response = jj.match("*"), jj.Response()

    payload = FormData([
        ("field1", "value1"),
        ("field1", "value2"),
        ("field2", "null"),
    ])
    async with run(mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        async with handler:
            resp = await client.post("/", data=payload)
            assert resp.status == 200

            history = await handler.history()
            req = history[0]["request"]
            assert req.method == "POST"
            assert req.path == "/"
            assert req.body == b'field1=value1&field1=value2&field2=null'


@pytest.mark.asyncio
async def test_mock_history_post_form_data():
    mock = Mock()
    self_middleware = SelfMiddleware(Mock().resolver)
    matcher, response = jj.match("*"), jj.Response()

    payload = FormData([
        ("field1", "value1"),
        ("field1", "value2"),
        ("field2", "null"),
    ])
    payload._is_multipart = True

    async with run(mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        async with handler:
            resp = await client.post("/", data=payload)
            assert resp.status == 200

            history = await handler.history()
            req = history[0]["request"]
            assert req.method == "POST"
            assert req.path == "/"
            assert isinstance(req.body, bytes)


@pytest.mark.asyncio
async def test_mock_history_post_binary_data():
    mock = Mock()
    self_middleware = SelfMiddleware(Mock().resolver)
    matcher, response = jj.match("*"), jj.Response()

    async with run(mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        async with handler:
            resp = await client.post("/", data=b"binary")
            assert resp.status == 200

            history = await handler.history()
            req = history[0]["request"]
            assert req.method == "POST"
            assert req.path == "/"
            assert req.body == b"binary"
