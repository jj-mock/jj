from typing import Any, Dict

from packed import packable

from ._attribute_matcher import AttributeMatcher

__all__ = ("ContainMatcher", "NotContainMatcher",)


@packable("jj.matchers.ContainMatcher")
class ContainMatcher(AttributeMatcher):
    """
    Matches if the actual value contains the expected value.

    This matcher checks if the expected value is present in the actual value.
    """

    def __init__(self, expected: Any) -> None:
        """
        Initialize a ContainMatcher with an expected value.

        :param expected: The value to check for in the actual value.
        """
        self._expected = expected

    @property
    def expected(self) -> Any:
        """
        Return the expected value for this matcher.

        :return: The expected value.
        """
        return self._expected

    async def match(self, actual: Any) -> bool:
        """
        Determine if the actual value contains the expected value.

        :param actual: The value to check.
        :return: `True` if the actual value contains the expected value, otherwise `False`.
        """
        return self._expected in actual

    def __repr__(self) -> str:
        """
        Return a string representation of the ContainMatcher instance.

        :return: A string describing the class and expected value.
        """
        return f"{self.__class__.__qualname__}({self._expected!r})"

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the ContainMatcher instance for serialization.

        :return: A dictionary containing the expected value.
        """
        return {"expected": self._expected}

    @classmethod
    def __unpacked__(cls, *, expected: Any, **kwargs: Any) -> "ContainMatcher":
        """
        Unpack a ContainMatcher instance from its serialized form.

        :param expected: The expected value to use for this matcher.
        :param kwargs: Additional keyword arguments (ignored).
        :return: A new instance of ContainMatcher.
        """
        return cls(expected)


@packable("jj.matchers.NotContainMatcher")
class NotContainMatcher(ContainMatcher):
    """
    Matches if the actual value does not contain the expected value.

    This matcher checks if the expected value is not present in the actual value.
    """

    async def match(self, actual: Any) -> bool:
        """
        Determine if the actual value does not contain the expected value.

        :param actual: The value to check.
        :return: `True` if the actual value does not contain the expected value, otherwise `False`.
        """
        return self._expected not in actual

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the NotContainMatcher instance for serialization.

        :return: A dictionary containing the expected value.
        """
        return {"expected": self._expected}

    @classmethod
    def __unpacked__(cls, *, expected: Any, **kwargs: Any) -> "NotContainMatcher":
        """
        Unpack a NotContainMatcher instance from its serialized form.

        :param expected: The expected value to use for this matcher.
        :param kwargs: Additional keyword arguments (ignored).
        :return: A new instance of NotContainMatcher.
        """
        return cls(expected)
