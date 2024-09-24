from typing import Union

from jj import DelayedResponse, RelayResponse, Response, TemplateResponse

REMOTE_RESPONSES = (Response, RelayResponse, DelayedResponse, TemplateResponse)

RemoteResponseType = Union[Response, RelayResponse, DelayedResponse, TemplateResponse]

__all__ = ("RemoteResponseType", "REMOTE_RESPONSES",)
