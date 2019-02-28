from asyncio import AbstractEventLoop, ensure_future
from typing import Type, Any, List

from aiohttp.web_runner import BaseRunner, TCPSite


__all__ = ("Server",)


class Server:
    def __init__(self, loop: AbstractEventLoop,
                 runner_factory: Type[BaseRunner],
                 site_factory: Type[TCPSite]) -> None:
        self._loop = loop
        self._runner_factory = runner_factory
        self._site_factory = site_factory
        self._runners: List[BaseRunner] = []

    async def _start(self, app, host, port):
        runner = self._runner_factory(app, loop=self._loop)
        await runner.setup()

        site = self._site_factory(runner, host=host, port=port)
        await site.start()

        self._runners += [runner]

    def start(self, app: Any, host: str = None, port: int = None) -> None:
        ensure_future(self._start(app, host, port))

    def serve(self) -> None:
        self._loop.run_forever()

    def cleanup(self) -> None:
        for runner in reversed(self._runners):
            self._loop.run_until_complete(runner.cleanup())

    def shutdown(self) -> None:
        if hasattr(self._loop, "shutdown_asyncgens"):  # python 3.6+
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
        self._loop.close()
