from typing import Any

__all__ = ("AttributeMatcher",)


class AttributeMatcher:
    """
    Base class for matchers that match attributes of an HTTP request.

    This abstract class defines the interface for all matchers that evaluate
    various attributes (e.g., headers, query parameters) of a request.
    """

    async def match(self, actual: Any) -> bool:
        """
        Determine if the actual value matches the criteria defined by the matcher.

        :param actual: The value to be matched against.
        :return: `True` if the value matches the criteria, otherwise `False`.
        :raises NotImplementedError: This method must be implemented in subclasses.
        """
        raise NotImplementedError()

    def __repr__(self) -> str:
        """
        Return a string representation of the AttributeMatcher instance.

        :return: A string describing the class.
        """
        return f"{self.__class__.__qualname__}()"
