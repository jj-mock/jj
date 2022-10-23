from asyncio import sleep
from typing import Optional, Any, Dict, Union, cast

from aiohttp.abc import AbstractStreamWriter
from aiohttp.web_request import BaseRequest
from packed import packable

import jj

__all__ = ("DelayedResponse",)

DelayType = Union[float, int]


@packable("jj.responses.DelayedResponse")
class DelayedResponse(jj.Response):
    def __init__(self, *, delay: DelayType = 0.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._delay = delay

    def set_delay(self, delay: DelayType) -> "DelayedResponse":
        self._delay = delay
        return self

    def copy(self) -> "DelayedResponse":
        copied = cast(DelayedResponse, super().copy())
        return copied.set_delay(self._delay)

    async def prepare(self, request: BaseRequest) -> Optional[AbstractStreamWriter]:
        if self._delay > 0.0:
            await sleep(self._delay)
        return await super().prepare(request)

    def __packed__(self) -> Dict[str, Any]:
        packed = super().__packed__()
        return {"delay": self._delay, **packed}

    @classmethod
    def __unpacked__(cls, *, delay: DelayType = 0.0, **kwargs: Any) -> "DelayedResponse":
        response = cast(DelayedResponse, super().__unpacked__(**kwargs))
        return response.set_delay(delay)
