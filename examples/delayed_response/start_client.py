import asyncio
from time import monotonic

from httpx import AsyncClient

import jj
from delayed_response import DelayedResponse
from jj.mock import mocked


async def main():
    matcher = jj.match("*", "/users")
    response = DelayedResponse(delay=1.0)

    async with mocked(matcher, response), AsyncClient() as client:
        started_at = monotonic()
        resp = await client.get("http://localhost:8080/users")
        ended_at = monotonic()
    print(f"Response {resp.status_code}, took {ended_at - started_at} seconds")

if __name__ == "__main__":
    asyncio.run(main())
