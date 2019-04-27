import asyncio

from aiohttp.test_utils import TestClient

from ._request_formatter import RequestFormatter
from ._test_server import TestServer
from ._steps import Given, When, Then


__all__ = ("TestClient", "TestServer", "RequestFormatter",
           "run", "given", "when", "then",)


def run(app, resolver=None, middlewares=None):
    loop = asyncio.get_event_loop()
    return TestClient(TestServer(app, resolver, middlewares, loop=loop), loop=loop)

given = Given()
when = When()
then = Then()
