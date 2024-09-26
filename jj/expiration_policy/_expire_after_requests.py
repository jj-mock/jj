from typing import Any, Dict

from packed import packable

from ..requests import Request
from ._expiration_policy import ExpirationPolicy

__all__ = ("ExpireAfterRequests",)


@packable("jj.expiration_policy.ExpireAfterRequests")
class ExpireAfterRequests(ExpirationPolicy):
    """
    Represents an expiration policy based on the number of requests.

    This policy expires a mocked response after a specified number of requests.
    Once the maximum request count is reached, the response is considered expired
    and will no longer match subsequent requests.
    """

    def __init__(self, max_requests_count: int) -> None:
        """
        Initialize the ExpireAfterRequests policy with a maximum number of allowed requests.

        :param max_requests_count: The maximum number of requests allowed before the mock expires.
                                   Must be greater than 0.
        :raises AssertionError: If `max_requests_count` is less than or equal to 0.
        """
        assert max_requests_count > 0, \
            f'max_requests_count must be more than 0, {max_requests_count} given'

        self._max_requests_count = max_requests_count
        self._current_requests_count = 0

    @property
    def max_requests_count(self) -> int:
        """
        Return the maximum number of requests allowed before expiration.

        :return: The maximum number of requests.
        """
        return self._max_requests_count

    async def is_expired(self, request: Request) -> bool:
        """
        Check if the mock has expired based on the number of requests made.

        :param request: The current request being checked against the expiration policy.
        :return: `True` if the mock has expired, otherwise `False`.
        """
        if self._current_requests_count < self._max_requests_count:
            self._current_requests_count += 1
            return False
        return True

    def __repr__(self) -> str:
        """
        Return a string representation of the ExpireAfterRequests instance.

        :return: A string representation of the instance.
        """
        return f"{self.__class__.__qualname__}({self._max_requests_count!r})"

    def __packed__(self) -> Dict[str, Any]:
        """
        Serialize the ExpireAfterRequests instance for packing.

        :return: A dictionary containing the serialized form of the instance.
        """
        return {
            "max_requests_count": self._max_requests_count,
        }

    @classmethod
    def __unpacked__(cls, *, max_requests_count: int, **kwargs: Any) -> "ExpireAfterRequests":
        """
        Unpack a serialized ExpireAfterRequests instance.

        :param max_requests_count: The maximum number of requests allowed before expiration.
        :param kwargs: Additional keyword arguments (ignored).
        :return: A new instance of ExpireAfterRequests.
        """
        return cls(max_requests_count=max_requests_count)
