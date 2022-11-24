from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncGenerator, Dict, List, TypeVar

from ._mocked import Mocked

__all__ = ("stacked",)

MockedType = TypeVar("MockedType", List[Mocked], Dict[str, Mocked])


@asynccontextmanager
async def stacked(mocks: MockedType) -> AsyncGenerator[MockedType, None]:
    async with AsyncExitStack() as stack:
        if isinstance(mocks, list):
            yield [await stack.enter_async_context(mock) for mock in mocks]
        elif isinstance(mocks, dict):
            yield {name: await stack.enter_async_context(mock) for name, mock in mocks.items()}
        else:
            raise TypeError(f"Unsupported type: {type(mocks)}")
