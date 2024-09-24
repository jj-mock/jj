from http.cookies import Morsel
from typing import Any, Dict, Union

from aiohttp.payload import BytesPayload, IOBasePayload, TextIOPayload

__all__ = ("cookie_to_dict", "get_response_body",)


def cookie_to_dict(cookie: "Morsel[str]") -> Dict[str, Union[str, None]]:
    """
    Convert a Morsel object into a dictionary.

    :param cookie: The cookie morsel object to be converted.
    :return: A dictionary representation of the cookie, including attributes like
             "name", "value", "expires", "domain", "max-age", "path", "secure",
             "httponly", and "version".
    """
    dictionary: Dict[str, Union[str, None]] = {
        "name": cookie.key,
        "value": cookie.value,
    }
    for attr in ("expires", "domain", "max-age", "path", "secure", "httponly", "version"):
        key = attr.replace("-", "_")
        val = cookie.get(attr)
        dictionary[key] = None if val == "" else val
    return dictionary


def get_response_body(body: Any) -> bytes:
    """
    Convert the provided response body into bytes.

    :param body: The response body, which can be of types like bytes, bytearray,
                 memoryview, or specific aiohttp payloads.
    :return: The body converted to a bytes object.
    :raises ValueError: If the body type is unsupported.
    """
    if isinstance(body, (bytes, bytearray, memoryview)):
        return bytes(body)
    elif isinstance(body, BytesPayload):
        return bytes(body._value)
    elif isinstance(body, TextIOPayload):
        return bytes(body._value.read(), body.encoding)  # type: ignore
    elif isinstance(body, IOBasePayload):
        return bytes(body._value.read())
    else:
        raise ValueError("Unsupported body type {}".format(type(body)))
