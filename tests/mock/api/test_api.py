import sys
from typing import AsyncContextManager, Callable
from uuid import uuid4

import pytest

import jj
from jj.http import BAD_REQUEST

from ._api_client import ApiClient
from ._utils import client_version, make_client, mock, register_handler, server_version

__all__ = ("make_client", "mock", "server_version", "client_version",)  # fixtures

ClientFixtureType = Callable[[], AsyncContextManager[ApiClient]]


@pytest.mark.asyncio
async def test_api_index(make_client: ClientFixtureType):
    async with make_client() as api:
        status, body = await api.get_index()

        assert status == 200
        assert body == {
            "handlers": {
                "url": f"{api.url}/__jj__/handlers"
            }
        }


@pytest.mark.asyncio
async def test_api_handlers_empty(make_client: ClientFixtureType):
    async with make_client() as api:
        status, body = await api.get_handlers()

        assert status == 200
        assert body == []


@pytest.mark.asyncio
async def test_api_handlers(make_client: ClientFixtureType, server_version: str):
    async with make_client() as api:
        handler = await register_handler(api, response=jj.Response(body=b"body"))

        status, body = await api.get_handlers()
        assert status == 200
        assert body == [{
            "id": str(handler.id),
            "expiration_policy": None,
            "matcher": {
                "AllMatcher": {
                    "matchers": [
                        {"MethodMatcher": {"method": {"EqualMatcher": {"expected": "*"}}}}
                    ]
                }
            },
            "response": {
                "Response": {
                    "status": 200,
                    "reason": "OK",
                    "headers": [
                        ["Server", server_version],
                    ],
                    "cookies": [],
                    "body": "b'body'",
                    "chunked": False,
                    "compression": None
                }
            },
            "history": {
                "url": f"{api.url}/__jj__/handlers/{handler.id}/history"
            }
        }]


@pytest.mark.asyncio
async def test_api_history_nonexisting_handler(make_client: ClientFixtureType):
    async with make_client() as api:
        handler_id = uuid4()

        status, body = await api.get_history(handler_id)

        assert status == 400
        assert body == {
            "status": BAD_REQUEST,
            "error": "Handler not found"
        }


@pytest.mark.asyncio
async def test_api_history_empty(make_client: ClientFixtureType):
    async with make_client() as api:
        handler = await register_handler(api)

        status, body = await api.get_history(handler.id)

        assert status == 200
        assert body == []


@pytest.mark.asyncio
async def test_api_history(make_client: ClientFixtureType,
                           server_version: str, client_version: str):
    async with make_client() as api:
        handler = await register_handler(api, response=jj.Response(text="text"))

        await api.client.post("/", json={"key": "val"})

        status, body = await api.get_history(handler.id)

        accept_encoding = "gzip, deflate, zstd" if sys.version_info >= (3, 14) else "gzip, deflate"

        assert status == 200
        assert body == [{
            "request": {
                "HistoryRequest": {
                    "method": "POST",
                    "path": "/",
                    "segments": {},
                    "params": [],
                    "headers": [
                        ["Host", f"{api.host}:{api.port}"],
                        ["Accept", "*/*"],
                        ["Accept-Encoding", accept_encoding],
                        ["User-Agent", client_version],
                        ["Content-Length", "14"],
                        ["Content-Type", "application/json"]
                    ],
                    "body": {"key": "val"},
                    "raw": "b'{\"key\": \"val\"}'"
                }
            },
            "response": {
                "HistoryResponse": {
                    "status": 200,
                    "reason": "OK",
                    "headers": [
                        ["Content-Type", "text/plain; charset=utf-8"],
                        ["Server", server_version],
                        ["Content-Length", "4"],
                    ],
                    "body": "text",
                    "raw": "b'text'"
                }
            }
        }]
