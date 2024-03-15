import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable
from uuid import uuid4

import aiohttp
import pytest

import jj
from jj.http import BAD_REQUEST
from jj.middlewares import SelfMiddleware
from jj.mock import Mock, RemoteMock

from .._test_utils import run


@pytest.fixture()
def mock() -> Mock:
    return Mock()


@pytest.fixture()
def make_client(mock: Mock):
    @asynccontextmanager
    async def wrapper():
        self_middleware = SelfMiddleware(Mock().resolver)
        async with run(mock, middlewares=[self_middleware]) as client:
            yield client
    return wrapper


@pytest.fixture()
def server_version() -> str:
    return f"jj/{jj.__version__} via aiohttp/{aiohttp.__version__}"


@pytest.fixture()
def client_version() -> str:
    return f"Python/3.{sys.version_info.minor} aiohttp/{aiohttp.__version__}"


@pytest.mark.asyncio
async def test_api_index(make_client: Callable[[], AsyncGenerator]):
    async with make_client() as client:
        resp = await client.get("/__jj__")

        assert resp.status == 200
        assert await resp.json() == {
            "handlers": {
                "url": str(client.make_url("/__jj__/handlers"))
            }
        }


@pytest.mark.asyncio
async def test_api_handlers_empty(make_client: Callable[[], AsyncGenerator]):
    async with make_client() as client:
        resp = await client.get("/__jj__/handlers")

        assert resp.status == 200
        assert await resp.json() == []


@pytest.mark.asyncio
async def test_api_handlers(make_client: Callable[[], AsyncGenerator], server_version: str):
    async with make_client() as client:
        matcher, response = jj.match("*"), jj.Response(status=200, body=b"text")
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        await handler.register()

        resp = await client.get("/__jj__/handlers")
        assert resp.status == 200

        body = await resp.json()
        assert len(body) == 1
        assert body[0]["id"] == str(handler.id)
        assert isinstance(body[0]["registered_at"], str)

        assert body[0]["matcher"] == {
           "AllMatcher": {
               "matchers": [
                   {"MethodMatcher": {"method": {"EqualMatcher": {"expected": "*"}}}}
               ]
           }
        }
        assert body[0]["response"] == {
            "Response": {
                "status": 200,
                "reason": "OK",
                "headers": [["Server", server_version]],
                "cookies": [],
                "body": "b'text'",
                "chunked": False,
                "compression": None
            }
        }
        assert body[0]["history"] == {
            "url": str(client.make_url(f"/__jj__/handlers/{handler.id}/history"))
        }


@pytest.mark.asyncio
async def test_api_history_nonexisting_handler(make_client: Callable[[], AsyncGenerator]):
    handler_id = str(uuid4())
    async with make_client() as client:
        resp = await client.get(f"/__jj__/handlers/{handler_id}/history")

        assert resp.status == 400
        assert await resp.json() == {
            "status": BAD_REQUEST,
            "error": "Handler not found"
        }


@pytest.mark.asyncio
async def test_api_history_empty(make_client: Callable[[], AsyncGenerator]):
    async with make_client() as client:
        matcher, response = jj.match("*"), jj.Response(status=200, body=b"text")
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        await handler.register()

        resp = await client.get(f"/__jj__/handlers/{handler.id}/history")

        assert resp.status == 200
        assert await resp.json() == []


@pytest.mark.asyncio
async def test_api_history(make_client: Callable[[], AsyncGenerator],
                           server_version: str, client_version: str):
    async with make_client() as client:
        matcher, response = jj.match("*"), jj.Response(status=200, body=b"text")
        handler = RemoteMock(client.make_url("/")).create_handler(matcher, response)
        await handler.register()

        await client.post("/", json={"key": "val"})

        resp = await client.get(f"/__jj__/handlers/{handler.id}/history")

        assert resp.status == 200
        body = await resp.json()
        print("body", body)

        assert len(body) == 1
        assert isinstance(body[0]["created_at"], str)
        assert body[0]["request"] == {
            'HistoryRequest': {
                'method': 'POST',
                'path': '/',
                'segments': {},
                'params': [],
                'headers': [
                    ['Host', f"{client.host}:{client.port}"],
                    ['Accept', '*/*'],
                    ['Accept-Encoding', 'gzip, deflate'],
                    ['User-Agent', client_version],
                    ['Content-Length', '14'],
                    ['Content-Type', 'application/json']
                ],
                'body': {'key': 'val'},
                'raw': 'b\'{"key": "val"}\''
            }
        }
        hdrs = body[0]["response"]["HistoryResponse"]["headers"][:-1]
        body[0]["response"]["HistoryResponse"]["headers"] = hdrs
        assert body[0]["response"] == {
                'HistoryResponse': {
                    'status': 200,
                    'reason': 'OK',
                    'headers': [
                        ['Server', server_version],
                        ['Content-Length', '4'],
                        ['Content-Type', 'application/octet-stream'],
                    ],
                    'body': "b'text'",
                    'raw': "b'text'"
                }
            }
