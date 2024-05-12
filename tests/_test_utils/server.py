import asyncio

from aiohttp.test_utils import TestServer as BaseTestServer

from jj.runners import AppRunner


class TestServer(BaseTestServer):
    def __init__(self, app, resolver=None, middlewares=None, loop=None, **kwargs):
        super().__init__(app, loop=loop or asyncio.get_event_loop(), **kwargs)
        self.app = app
        self.resolver = resolver
        self.middlewares = middlewares or []

    async def _make_runner(self, **kwargs):
        try:
            resolver = self.app.resolver
        except (AttributeError, NotImplementedError):
            resolver = self.resolver
        return AppRunner(self.app, resolver, self.middlewares, self._loop)
