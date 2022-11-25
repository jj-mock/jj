import pytest

import jj
from jj.middlewares import SelfMiddleware
from jj.mock import Mock, Mocked, RemoteMock, stacked

from .._test_utils import run


@pytest.mark.asyncio
async def test_stacked():
    app = Mock()
    self_middleware = SelfMiddleware(app.resolver)
    matcher, response = jj.match("*"), jj.Response(status=200)

    async with run(app, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        mocked = [Mocked(handler)]

        async with stacked(mocked) as (mock,):
            response = await client.get("/")
            assert response.status == 200

        assert isinstance(mock, Mocked)

        response = await client.get("/")
        assert response.status == 404


@pytest.mark.asyncio
async def test_stacked_list():
    app = Mock()
    self_middleware = SelfMiddleware(app.resolver)
    matcher1, response1 = jj.match("*", "/users/1"), jj.Response(status=201)
    matcher2, response2 = jj.match("*", "/users/2"), jj.Response(status=202)

    async with run(app, middlewares=[self_middleware]) as client:
        remote_mock = RemoteMock(client.make_url("/"))
        mocked = [
            Mocked(remote_mock.create_handler(matcher1, response1)),
            Mocked(remote_mock.create_handler(matcher2, response2))
        ]

        async with stacked(mocked) as (mock1, mock2):
            response1 = await client.get("/users/1")
            assert response1.status == 201

            response2 = await client.get("/users/2")
            assert response2.status == 202

        assert mock1.history[0]["request"].path == "/users/1"
        assert mock2.history[0]["request"].path == "/users/2"


@pytest.mark.asyncio
async def test_stacked_list_order():
    app = Mock()
    self_middleware = SelfMiddleware(app.resolver)
    matcher1, response1 = jj.match("*"), jj.Response(status=201)
    matcher2, response2 = jj.match("*", "/users"), jj.Response(status=202)

    async with run(app, middlewares=[self_middleware]) as client:
        remote_mock = RemoteMock(client.make_url("/"))
        mocked = [
            Mocked(remote_mock.create_handler(matcher1, response1)),
            Mocked(remote_mock.create_handler(matcher2, response2))
        ]

        async with stacked(mocked) as (mock1, mock2):
            response = await client.get("/users")
            assert response.status == 202

        assert len(mock1.history) == 0
        assert len(mock2.history) == 1


@pytest.mark.asyncio
async def test_stacked_dict():
    app = Mock()
    self_middleware = SelfMiddleware(app.resolver)
    matcher1, response1 = jj.match("*", "/users/1"), jj.Response(status=201)
    matcher2, response2 = jj.match("*", "/users/2"), jj.Response(status=202)

    async with run(app, middlewares=[self_middleware]) as client:
        remote_mock = RemoteMock(client.make_url("/"))
        mocks = {
            "mock1": Mocked(remote_mock.create_handler(matcher1, response1)),
            "mock2": Mocked(remote_mock.create_handler(matcher2, response2)),
        }

        async with stacked(mocks) as mocks:
            response1 = await client.get("/users/1")
            assert response1.status == 201

            response2 = await client.get("/users/2")
            assert response2.status == 202

        assert mocks["mock1"].history[0]["request"].path == "/users/1"
        assert mocks["mock2"].history[0]["request"].path == "/users/2"


@pytest.mark.asyncio
async def test_stacked_incorrect_type():
    with pytest.raises(BaseException) as exc:
        async with stacked(None):
            pass

    assert exc.type == TypeError
    assert str(exc.value) == "Unsupported type: <class 'NoneType'>"
