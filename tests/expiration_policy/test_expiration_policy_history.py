import pytest

import jj
from jj.expiration_policy import ExpireAfterRequests
from jj.middlewares import SelfMiddleware
from jj.mock import Mock, RemoteMock

from .._test_utils import run


@pytest.mark.asyncio
async def test_expire_after_requests_history_request():
    mock = Mock()
    self_middleware = SelfMiddleware(Mock().resolver)
    matcher, response = jj.match("*"), jj.Response(status=200, body=b"text")

    requests_count = 2
    policy = ExpireAfterRequests(requests_count)

    async with run(mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(
            matcher, response, expiration_policy=policy
        )
        async with handler:
            for _ in range(requests_count):
                resp = await client.get("/", params={"key": "val"})
                assert resp.status == 200

            excess_response = await client.get("/")
            assert excess_response.status == 404

            history = await handler.fetch_history()
            assert len(history) == requests_count

            for i in range(requests_count):
                req = history[i]["request"]
                assert req.method == "GET"
                assert req.segments == {}
                assert req.path == "/"
                assert req.params == {"key": "val"}
                assert req.headers.get("User-Agent")
                assert req.body == req.raw == b""

                res = history[i]["response"]
                assert res.status == 200
                assert res.headers.get("Server")
                assert res.reason == "OK"
                assert res.body == res.raw == b"text"
