from typing import Union

from ._expiration_policy import ExpirationPolicy
from ._expire_after_requests import ExpireAfterRequests
from ._expire_never import ExpireNever

ExpirationPolicyType = Union[ExpireAfterRequests, ExpireNever, None]
ExpirationPolicyTuple = (ExpireAfterRequests, ExpireNever, None)

__all__ = (
    "ExpirationPolicy",
    "ExpireNever",
    "ExpireAfterRequests",
    "ExpirationPolicyType",
    "ExpirationPolicyTuple",
)
