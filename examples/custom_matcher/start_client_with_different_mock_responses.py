import asyncio
from pprint import pformat as pf
from uuid import uuid4

import httpx

import jj
from jj.mock import mocked


async def main():
    matcher = jj.match_all([
        jj.match("POST", "/users"),
    ])
    response_200 = jj.Response(status=200, json=[])
    response_500 = jj.Response(status=500, json=[])

    async with mocked(matcher, response_200) as mock_200:
        async with mocked(matcher, response_500,
                          allowed_number_of_requests=2) as mock_500:
            async with httpx.AsyncClient() as client:
                response = await client.post("http://localhost:8080/users", json={
                    "id": str(uuid4()),
                    "name": "User",
                })
                print("response", response)
                response = await client.post("http://localhost:8080/users", json={
                    "id": str(uuid4()),
                    "name": "User",
                })
                print("response", response)
                response = await client.post("http://localhost:8080/users", json={
                    "id": str(uuid4()),
                    "name": "User",
                })
                print("response", response)

    assert len(mock_500.history) == 2, f"History: {pf(mock_500.history)}"
    assert len(mock_200.history) == 1, f"History: {pf(mock_200.history)}"


if __name__ == "__main__":
    asyncio.run(main())
