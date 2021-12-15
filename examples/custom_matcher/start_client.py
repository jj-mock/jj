import asyncio
from pprint import pformat as pf
from uuid import uuid4

import httpx

import jj
from body_matcher import match_body_key
from jj.mock import mocked


async def main():
    matcher = jj.match_all([
        jj.match("POST", "/users"),
        match_body_key("id"),
    ])
    response = jj.Response(status=200, json=[])

    async with mocked(matcher, response) as mock:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8080/users", json={
                "id": str(uuid4()),
                "name": "User",
            })
            # print("response", response)

    assert len(mock.history) == 1, f"History: {pf(mock.history)}"

if __name__ == "__main__":
    asyncio.run(main())
