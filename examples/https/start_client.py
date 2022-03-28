import asyncio
from pprint import pformat as pf

import httpx

import jj
from jj.mock import mocked


async def main():
    matcher = jj.match("GET", "/users")
    response = jj.Response(status=200, json=[])

    async with mocked(matcher, response) as mock:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get("https://localhost:4443/users")
            print("response", response, response.json())

    assert len(mock.history) == 1, f"History: {pf(mock.history)}"

if __name__ == "__main__":
    asyncio.run(main())
