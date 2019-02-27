from ..requests import Request
from ..responses import Response


__all__ = ("default_handler",)


async def default_handler(request: Request) -> Response:
    return Response(status=404)
