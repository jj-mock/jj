from asyncio import AbstractEventLoop, Event, all_tasks, gather
from asyncio.exceptions import CancelledError
from typing import Any, List, Optional, Sequence, Type, Union

from aiohttp.web_runner import BaseRunner, TCPSite

__all__ = ("Server",)


class Server:
    def __init__(self, loop: AbstractEventLoop,
                 runner_factory: Type[BaseRunner],
                 site_factory: Type[TCPSite]) -> None:
        self._loop = loop
        self._runner_factory = runner_factory
        self._site_factory = site_factory

        self._apps: List[Any] = []
        self._runners: List[BaseRunner] = []
        self._event: Union[Event, None] = None

    def start(self, app: Any, host: Optional[str] = None, port: Optional[int] = None) -> None:
        self._apps.append((app, host, port))

    async def _start_apps(self) -> None:
        for app, host, port in self._apps:
            runner = self._runner_factory(app, loop=self._loop)  # type: ignore
            await runner.setup()

            site = self._site_factory(runner, host=host, port=port)
            await site.start()

            self._runners.append(runner)

    async def _stop_apps(self) -> None:
        for runner in reversed(self._runners):
            await runner.cleanup()

    async def _serve(self) -> None:
        self._event = Event()

        await self._start_apps()
        try:
            await self._event.wait()
        except CancelledError:
            pass
        finally:
            await self._stop_apps()

    def serve(self, exceptions: Sequence[Type[BaseException]] = (KeyboardInterrupt,)) -> None:
        task = self._loop.create_task(self._serve())
        try:
            self._loop.run_until_complete(task)
        except tuple(exceptions):
            pass
        finally:
            task.cancel()
            self._loop.run_until_complete(task)

    def cleanup(self) -> None:
        if self._event:
            self._event.set()

    def shutdown(self) -> None:
        tasks = all_tasks(self._loop)
        for task in tasks:
            task.cancel()
        gather(*tasks, return_exceptions=True)

        self._loop.run_until_complete(self._loop.shutdown_asyncgens())
        self._loop.close()
