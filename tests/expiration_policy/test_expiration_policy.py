import pytest

import jj
from jj.expiration_policy import ExpireAfterRequests
from jj.middlewares import SelfMiddleware
from jj.mock import Mock, RemoteMock

from .._test_utils import run


@pytest.mark.asyncio
@pytest.mark.parametrize("count_requests", [1, 2])
async def test_expire_after_requests(count_requests: int):
    mock = Mock()
    self_middleware = SelfMiddleware(mock.resolver)
    matcher, response = jj.match("*"), jj.Response(status=200, body=b"text")
    policy = ExpireAfterRequests(count_requests)

    async with run(mock, middlewares=[self_middleware]) as client:
        remote_mock = RemoteMock(client.make_url("/"))
        handler = remote_mock.create_handler(matcher, response, expiration_policy=policy)
        await handler.register()

        for _ in range(count_requests):
            response = await client.get("/")
            assert response.status == 200

            response_body = await response.read()
            assert response_body == b"text"

        excess_response = await client.get("/")
        assert excess_response.status == 404

        excess_response_body = await response.read()
        assert excess_response_body == b"text"


@pytest.mark.asyncio
async def test_expire_after_requests_with_request_and_deregister():
    mock = Mock()
    self_middleware = SelfMiddleware(mock.resolver)
    matcher, response = jj.match("*"), jj.Response(status=200, body=b"text")
    policy = ExpireAfterRequests(1)

    async with run(mock, middlewares=[self_middleware]) as client:
        remote_mock = RemoteMock(client.make_url("/"))
        handler = remote_mock.create_handler(matcher, response, expiration_policy=policy)
        await handler.register()

        response = await client.get("/")
        assert response.status == 200

        response_body = await response.read()
        assert response_body == b"text"

        await handler.deregister()

        response_after_deregister = await client.get("/")
        assert response_after_deregister.status == 404


@pytest.mark.asyncio
async def test_expiration_after_request_without_request_and_deregister():
    mock = Mock()
    self_middleware = SelfMiddleware(mock.resolver)
    matcher, response = jj.match("*"), jj.Response(status=200, body=b"text")
    policy = ExpireAfterRequests(1)

    async with run(mock, middlewares=[self_middleware]) as client:
        remote_mock = RemoteMock(client.make_url("/"))
        handler = remote_mock.create_handler(matcher, response, expiration_policy=policy)
        await handler.register()
        await handler.deregister()

        response = await client.get("/")
        assert response.status == 404
