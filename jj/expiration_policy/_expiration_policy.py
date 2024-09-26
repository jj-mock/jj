from ..requests import Request

__all__ = ("ExpirationPolicy",)


class ExpirationPolicy:
    """
    Base class for defining expiration policies in HTTP mocking.

    An expiration policy determines if a mocked response should still be
    considered valid based on the criteria defined by its implementation.
    """

    async def is_expired(self, request: Request) -> bool:
        """
        Determine whether the response associated with this policy has expired.

        :param request: The request to evaluate against the expiration criteria.
        :return: `True` if the policy deems the response expired, otherwise `False`.
        :raises NotImplementedError: If this method is not implemented by a subclass.
        """
        raise NotImplementedError()

    def __repr__(self) -> str:
        """
        Return a string representation of the ExpirationPolicy instance.

        :return: A string representation of the instance.
        """
        return f"{self.__class__.__qualname__}()"
