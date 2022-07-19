import jj
from watchfiles import run_process


@jj.match("*")
async def handler(request: jj.Request) -> jj.Response:
    return jj.Response(body="200 OK")


if __name__ == "__main__":
    # Docs https://watchfiles.helpmanual.io
    run_process(__file__, target=jj.serve)
