from typing import Any, Dict, Tuple
from uuid import UUID

from aiohttp.test_utils import TestClient


class ApiClient:
    def __init__(self, client: TestClient) -> None:
        self.client = client

    @property
    def url(self) -> str:
        return str(self.client.make_url("/")).rstrip("/")

    @property
    def host(self) -> str:
        return self.client.host

    @property
    def port(self) -> int:
        return self.client.port

    async def get_index(self) -> Tuple[int, Dict[str, Any]]:
        resp = await self.client.get("/__jj__")
        return resp.status, await resp.json()

    async def get_handlers(self) -> Tuple[int, Any]:
        resp = await self.client.get("/__jj__/handlers")
        body = await resp.json()
        if resp.status == 200:
            for handler in body:
                handler.pop("registered_at")
        return resp.status, body

    async def get_history(self, handler_id: UUID) -> Tuple[int, Any]:
        resp = await self.client.get(f"/__jj__/handlers/{handler_id}/history")
        body = await resp.json()
        if resp.status == 200:
            for history_item in body:
                history_item.pop("created_at")
                history_item["response"]["HistoryResponse"]["headers"] = [
                    [k, v] for k, v in history_item["response"]["HistoryResponse"]["headers"]
                    if k not in ("Date",)
                ]
        return resp.status, body
