import sys
from contextlib import asynccontextmanager
from typing import AsyncContextManager, Callable, Optional

import aiohttp
import pytest

import jj
from jj.matchers import ResolvableMatcher
from jj.middlewares import SelfMiddleware
from jj.mock import Mock, RemoteHandler, RemoteMock

from ..._test_utils import run
from ._api_client import ApiClient


@pytest.fixture()
def mock() -> Mock:
    return Mock()


@pytest.fixture()
def make_client(mock: Mock) -> Callable[[], AsyncContextManager[ApiClient]]:
    @asynccontextmanager
    async def wrapper():
        self_middleware = SelfMiddleware(Mock().resolver)
        async with run(mock, middlewares=[self_middleware]) as client:
            yield ApiClient(client)
    return wrapper


@pytest.fixture()
def server_version() -> str:
    return f"jj/{jj.__version__} via aiohttp/{aiohttp.__version__}"


@pytest.fixture()
def client_version() -> str:
    return f"Python/3.{sys.version_info.minor} aiohttp/{aiohttp.__version__}"


async def register_handler(api: ApiClient, response: Optional[jj.Response] = None,
                           matcher: Optional[ResolvableMatcher] = None) -> RemoteHandler:
    if matcher is None:
        matcher = jj.match("*")
    if response is None:
        response = jj.Response(status=200)
    handler = RemoteMock(api.url).create_handler(matcher, response)
    await handler.register()
    return handler
