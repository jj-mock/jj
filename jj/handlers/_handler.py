from ..requests import Request
from ..responses import Response

__all__ = ("default_handler",)


async def default_handler(request: Request) -> Response:
    """
    Handle unmatched requests with a default 404 response.

    This asynchronous function is used as the default handler for HTTP requests
    that do not match any defined routes or handlers. It returns a `Response` object
    with a 404 status code, indicating that the requested resource was not found.

    :param request: The incoming HTTP request that triggered the default handler.
    :return: A `Response` object with a 404 status code.
    """
    return Response(status=404)
