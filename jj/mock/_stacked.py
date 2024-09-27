from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncGenerator, Dict, List, TypeVar

from ._mocked import Mocked

__all__ = ("stacked",)

MockedType = TypeVar("MockedType", List[Mocked], Dict[str, Mocked])


@asynccontextmanager
async def stacked(mocks: MockedType) -> AsyncGenerator[MockedType, None]:
    """
    Stack multiple mocks into a single context manager for easier management.

    This context manager allows you to stack multiple mocks (either in a list or a dictionary)
    into a single context, ensuring they are all activated upon entering and deactivated
    upon exiting. It simplifies the process of managing multiple mocks simultaneously.

    :param mocks: A list or dictionary of `Mocked` objects to be activated in the context.
                  If a list is provided, the mocks are returned as a list; if a dictionary is
                  provided, they are returned as a dictionary with the same keys.
    :return: Yields the activated mocks. If the input was a list, it yields a list of active mocks;
             if the input was a dictionary, it yields a dictionary of active mocks
             keyed by the same names.
    :raises TypeError: If the `mocks` parameter is not a list or a dictionary.
    """
    async with AsyncExitStack() as stack:
        if isinstance(mocks, list):
            yield [await stack.enter_async_context(mock) for mock in mocks]
        elif isinstance(mocks, dict):
            yield {name: await stack.enter_async_context(mock) for name, mock in mocks.items()}
        else:
            raise TypeError(f"Unsupported type: {type(mocks)}")
