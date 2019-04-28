import asyncio

from aiohttp.test_utils import TestClient

from ._request_formatter import RequestFormatter
from ._test_server import TestServer


__all__ = ("TestClient", "TestServer", "RequestFormatter", "run",)


def run(app, resolver=None, middlewares=None):
    loop = asyncio.get_event_loop()
    return TestClient(TestServer(app, resolver, middlewares, loop=loop), loop=loop)
