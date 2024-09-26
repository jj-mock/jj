from typing import Any, Dict

from packed import packable

from ..requests import Request
from ._expiration_policy import ExpirationPolicy

__all__ = ("ExpireNever",)


@packable("jj.expiration_policy.ExpireNever")
class ExpireNever(ExpirationPolicy):
    """
    Represents a policy where a mocked response never expires.

    This policy ensures that the mocked response is always valid, regardless
    of how many requests have been made.
    """

    async def is_expired(self, request: Request) -> bool:
        """
        Check if the mock has expired. Always returns `False` as this policy never expires.

        :param request: The current request being evaluated (not used in this policy).
        :return: `False`, indicating the mock never expires.
        """
        return False

    def __repr__(self) -> str:
        """
        Return a string representation of the ExpireNever instance.

        :return: A string representation of the instance.
        """
        return f"{self.__class__.__qualname__}()"

    def __packed__(self) -> Dict[str, Any]:
        """
        Serialize the ExpireNever instance for packing.

        :return: A dictionary containing the serialized form of the instance.
        """
        return dict()

    @classmethod
    def __unpacked__(cls, **kwargs: Any) -> "ExpireNever":
        """
        Unpack a serialized ExpireNever instance.

        :return: A new instance of ExpireNever.
        """
        return cls()
