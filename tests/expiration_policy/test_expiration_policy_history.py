import pytest

import jj
from jj.expiration_policy import ExpireAfterRequests
from jj.middlewares import SelfMiddleware
from jj.mock import Mock, RemoteMock

from .._test_utils import run


@pytest.mark.asyncio
async def test_expiration_policy_history_request():
    mock = Mock()
    self_middleware = SelfMiddleware(Mock().resolver)
    matcher, response = jj.match("*"), jj.Response(status=200, body=b"text")
    policy = ExpireAfterRequests(2)

    async with run(mock, middlewares=[self_middleware]) as client:
        handler = RemoteMock(client.make_url("/")).create_handler(
            matcher, response, expiration_policy=policy
        )
        async with handler:
            for _ in range(2):
                resp = await client.get("/", params={"key": "val"})
                assert resp.status == 200

            history = await handler.fetch_history()
            for i in range(2):
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
