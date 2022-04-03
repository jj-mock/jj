import asyncio
from pprint import pformat as pf
from uuid import uuid4

import httpx

import jj
from jj.expiration_policy import ExpireAfterRequests
from jj.mock import mocked


async def main():
    matcher = jj.match_all([
        jj.match("POST", "/users"),
    ])
    requests_count = 3
    response_200 = jj.Response(status=200, json=[])
    response_500 = jj.Response(status=500, json=[])
    policy = ExpireAfterRequests(requests_count - 1)

    async with mocked(matcher, response_200) as mock_200:
        async with mocked(matcher, response_500, expiration_policy=policy) as mock_500:
            async with httpx.AsyncClient() as client:
                for _ in range(requests_count):
                    response = await client.post("http://localhost:8080/users", json={
                        "id": str(uuid4()),
                        "name": "User",
                    })
                    print("response", response)

    assert len(mock_500.history) == 2, f"History: {pf(mock_500.history)}"
    assert len(mock_200.history) == 1, f"History: {pf(mock_200.history)}"


if __name__ == "__main__":
    asyncio.run(main())
