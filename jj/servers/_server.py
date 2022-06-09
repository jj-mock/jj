from asyncio import AbstractEventLoop, CancelledError, Event, Task, all_tasks, gather
from typing import Any, List, Optional, Sequence, Type

from aiohttp.web_runner import BaseRunner, TCPSite

__all__ = ("Server",)


class Server:
    def __init__(self, loop: AbstractEventLoop,
                 runner_factory: Type[BaseRunner],
                 site_factory: Type[TCPSite]) -> None:
        self._loop = loop
        self._runner_factory = runner_factory
        self._site_factory = site_factory
        self._tasks: List["Task[Any]"] = []
        self._events: List[Event] = []

    async def _start(self, app: Any, event: Event,
                     host: Optional[str] = None,
                     port: Optional[int] = None) -> None:
        runner = self._runner_factory(app, loop=self._loop)  # type: ignore
        await runner.setup()

        site = self._site_factory(runner, host=host, port=port)
        await site.start()

        try:
            await event.wait()
        except CancelledError:
            pass
        finally:
            await runner.cleanup()

    def start(self, app: Any, host: Optional[str] = None, port: Optional[int] = None) -> None:
        event = Event()
        self._events.append(event)
        task = self._loop.create_task(self._start(app, event, host, port))
        self._tasks.append(task)

    async def _serve(self) -> None:
        try:
            await gather(*self._tasks)
        finally:
            self.cleanup()

    def serve(self, exceptions: Sequence[Type[BaseException]] = (KeyboardInterrupt,)) -> None:
        try:
            self._loop.run_until_complete(self._serve())
        except tuple(exceptions):
            pass

    def cleanup(self) -> None:
        while self._events:
            event = self._events.pop()
            event.set()

    def _cancel_tasks(self, tasks: List["Task[Any]"]) -> None:
        if not tasks:
            return

        for task in tasks:
            task.cancel()

        self._loop.run_until_complete(gather(*tasks, return_exceptions=True))

        for task in tasks:
            if task.cancelled():
                continue
            if task.exception() is not None:
                self._loop.call_exception_handler({
                    "message": "unhandled exception during shutdown",
                    "exception": task.exception(),
                    "task": task,
                })

    def shutdown(self) -> None:
        try:
            self._cancel_tasks(list(all_tasks(self._loop)))
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
        finally:
            self._loop.close()
