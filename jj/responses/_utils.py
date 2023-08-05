from http.cookies import Morsel
from typing import Any, Dict, Union

from aiohttp.payload import BytesPayload, IOBasePayload, TextIOPayload

__all__ = ("cookie_to_dict", "get_response_body",)


def cookie_to_dict(cookie: "Morsel[str]") -> Dict[str, Union[str, None]]:
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
