import pytest

import jj
from jj.middlewares import SelfMiddleware
from jj.mock import Mock, Mocked, RemoteMock
from jj.mock._history import SimpleHistoryFormatter, default_history_formatter

from .._test_utils import run


@pytest.mark.asyncio
async def test_mocked_prefetch_history():
    remote_mock = Mock()
    self_middleware = SelfMiddleware(remote_mock.resolver)
    matcher, response = jj.match("*"), jj.Response(status=200)

    async with run(remote_mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)

        async with Mocked(handler, prefetch_history=True) as mock:
            response = await client.get("/")
            assert response.status == 200
            assert mock.history is None

        assert len(mock.history) == 1


@pytest.mark.asyncio
async def test_mocked_not_prefetch_history():
    remote_mock = Mock()
    self_middleware = SelfMiddleware(remote_mock.resolver)
    matcher, response = jj.match("*"), jj.Response(status=200)

    async with run(remote_mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)

        async with Mocked(handler, prefetch_history=False) as mock:
            response = await client.get("/")
            assert response.status == 200

        assert mock.history is None


@pytest.mark.asyncio
async def test_mocked_fetch_history():
    remote_mock = Mock()
    self_middleware = SelfMiddleware(remote_mock.resolver)
    matcher, response = jj.match("*"), jj.Response(status=200)

    async with run(remote_mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)

        async with Mocked(handler, prefetch_history=False) as mock:
            response = await client.get("/")
            assert response.status == 200
            assert mock.history is None

            history = await mock.fetch_history()
            assert len(history) == len(mock.history) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("prefetch_history", [True, False])
async def test_mocked_wait_for_requests(*, prefetch_history: bool):
    remote_mock = Mock()
    self_middleware = SelfMiddleware(remote_mock.resolver)
    matcher, response = jj.match("*"), jj.Response(status=200)

    async with run(remote_mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)

        async with Mocked(handler, prefetch_history=prefetch_history) as mock:
            response = await client.get("/")
            assert response.status == 200
            await mock.wait_for_requests()

        assert len(mock.history) == 1


@pytest.mark.asyncio
async def test_mocked_wait_for_requests_timeout():
    remote_mock = Mock()
    self_middleware = SelfMiddleware(remote_mock.resolver)
    matcher, response = jj.match("*"), jj.Response(status=200)

    async with run(remote_mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)

        async with Mocked(handler) as mock:
            await mock.wait_for_requests(timeout=0.01)
            assert len(mock.history) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(("disposable", "status"), [
    (True, 404),
    (False, 200),
])
async def test_mocked_disposable(*, disposable: bool, status: int):
    remote_mock = Mock()
    self_middleware = SelfMiddleware(remote_mock.resolver)
    matcher, response = jj.match("*"), jj.Response(status=200)

    async with run(remote_mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)

        async with Mocked(handler, disposable=disposable):
            response = await client.get("/")
            assert response.status == 200

        response = await client.get("/")
        assert response.status == status


@pytest.mark.asyncio
@pytest.mark.parametrize(("disposable", "prefetch_history", "pretty_print"), [
    (True, True, True),
    (False, False, False),
])
async def test_mocked_repr(*, disposable: bool, prefetch_history: bool, pretty_print: bool):
    mock = Mock()
    self_middleware = SelfMiddleware(mock.resolver)
    matcher, response = jj.match("*"), jj.Response()

    async with run(mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        history_formatter = default_history_formatter if pretty_print else \
            SimpleHistoryFormatter()
        mocked = Mocked(handler, disposable=disposable, prefetch_history=prefetch_history,
                        history_formatter=history_formatter)
        history = history_formatter.format_history(mocked.history)
        assert repr(mocked) == (f"Mocked<{handler}, "
                                f"disposable={disposable}, "
                                f"prefetch_history={prefetch_history}, "
                                f"history={history}>")

        assert mocked.handler == handler
        assert mocked.disposable == disposable
        assert mocked.prefetch_history == prefetch_history
        assert mocked.get_formatted_history == history
