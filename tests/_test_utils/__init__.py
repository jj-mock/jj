import asyncio

from aiohttp.test_utils import TestClient

from .server import TestServer


__all__ = ("TestClient", "TestServer", "run",)


def run(app, resolver=None, middlewares=None):
    loop = asyncio.get_event_loop()
    return TestClient(TestServer(app, resolver, middlewares, loop=loop), loop=loop)
