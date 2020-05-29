import pytest
from pytest import raises

import jj
from jj.middlewares import SelfMiddleware
from jj.mock import Mock, RemoteMock

from .._test_utils import run


@pytest.mark.asyncio
async def test_mock_default_handler():
    mock = Mock()
    self_middleware = SelfMiddleware(mock.resolver)

    async with run(mock, middlewares=[self_middleware]) as client:
        response = await client.get("/")
        assert response.status == 404


@pytest.mark.asyncio
async def test_mock_register():
    mock = Mock()
    self_middleware = SelfMiddleware(mock.resolver)
    matcher, response = jj.match("*"), jj.Response(status=200, body=b"text")

    async with run(mock, middlewares=[self_middleware]) as client:
        remote_mock = RemoteMock(client.make_url("/"))
        handler = remote_mock.create_handler(matcher, response)
        await handler.register()

        response = await client.get("/")
        response_body = await response.read()

        assert response.status == 200
        assert response_body == b"text"


@pytest.mark.asyncio
async def test_mock_register_bad_request():
    mock = Mock()
    self_middleware = SelfMiddleware(mock.resolver)

    async with run(mock, middlewares=[self_middleware]) as client:
        remote_mock = RemoteMock(client.make_url("/"))
        handler = remote_mock.create_handler(None, None)

        with raises(Exception) as exception:
            await handler.register()
        assert exception.type is AssertionError


@pytest.mark.asyncio
async def test_mock_deregister():
    mock = Mock()
    self_middleware = SelfMiddleware(mock.resolver)
    matcher, response = jj.match("*"), jj.Response(status=200, body=b"text")

    async with run(mock, middlewares=[self_middleware]) as client:
        remote_mock = RemoteMock(client.make_url("/"))
        handler = remote_mock.create_handler(matcher, response)
        await handler.register()
        await handler.deregister()

        response = await client.get("/")
        assert response.status == 404


@pytest.mark.asyncio
async def test_mock_deregister_not_registered():
    mock = Mock()
    self_middleware = SelfMiddleware(mock.resolver)
    matcher, response = jj.match("*"), jj.Response(status=200, body=b"text")

    async with run(mock, middlewares=[self_middleware]) as client:
        remote_mock = RemoteMock(client.make_url("/"))
        handler = remote_mock.create_handler(matcher, response)
        await handler.deregister()


@pytest.mark.asyncio
async def test_mock_deregister_bad_request():
    mock = Mock()
    self_middleware = SelfMiddleware(mock.resolver)

    async with run(mock, middlewares=[self_middleware]) as client:
        remote_mock = RemoteMock(client.make_url("/"))
        handler = remote_mock.create_handler(None, None)

        with raises(Exception) as exception:
            await handler.deregister()
        assert exception.type is AssertionError


@pytest.mark.asyncio
async def test_mock_handler_order():
    mock = Mock()
    self_middleware = SelfMiddleware(Mock().resolver)
    matcher1, response1 = jj.match("*"), jj.Response(body=b"text1")
    matcher2, response2 = jj.match("*"), jj.Response(body=b"text2")

    async with run(mock, middlewares=[self_middleware]) as client:
        remote_mock = RemoteMock(client.make_url("/"))
        handler1 = remote_mock.create_handler(matcher1, response1)
        handler2 = remote_mock.create_handler(matcher2, response2)
        async with handler1:
            async with handler2:
                resp = await client.get("/")
                assert resp.status == 200
                body = await resp.read()
                assert body == b"text2"
