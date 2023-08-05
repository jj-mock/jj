from typing import Union

from jj import DelayedResponse, RelayResponse, Response

RemoteResponseType = Union[Response, RelayResponse, DelayedResponse]

__all__ = ("RemoteResponseType",)
