from typing import Any, Dict

from packed import packable

from ._attribute_matcher import AttributeMatcher

__all__ = ("EqualMatcher", "NotEqualMatcher",)


@packable("jj.matchers.EqualMatcher")
class EqualMatcher(AttributeMatcher):
    """
    Matches if the actual value equals the expected value.

    This matcher evaluates whether the actual value in a request matches
    the predefined expected value.
    """

    def __init__(self, expected: Any) -> None:
        """
        Initialize an EqualMatcher with an expected value.

        :param expected: The value to compare against the actual value.
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
        Determine if the actual value matches the expected value.

        :param actual: The value to compare against the expected value.
        :return: `True` if the actual value equals the expected value, otherwise `False`.
        """
        return bool(self._expected == actual)

    def __repr__(self) -> str:
        """
        Return a string representation of the EqualMatcher instance.

        :return: A string describing the class and expected value.
        """
        return f"{self.__class__.__qualname__}({self._expected!r})"

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the EqualMatcher instance for serialization.

        :return: A dictionary containing the expected value.
        """
        return {"expected": self._expected}

    @classmethod
    def __unpacked__(cls, *, expected: Any, **kwargs: Any) -> "EqualMatcher":
        """
        Unpack an EqualMatcher instance from its serialized form.

        :param expected: The expected value to use for the matcher.
        :param kwargs: Additional arguments (unused in this case).
        :return: A new instance of EqualMatcher.
        """
        return cls(expected)


@packable("jj.matchers.NotEqualMatcher")
class NotEqualMatcher(EqualMatcher):
    """
    Matches if the actual value does not equal the expected value.

    This matcher evaluates whether the actual value in a request does not
    match the predefined expected value.
    """

    async def match(self, actual: Any) -> bool:
        """
        Determine if the actual value does not match the expected value.

        :param actual: The value to compare against the expected value.
        :return: `True` if the actual value does not equal the expected value, otherwise `False`.
        """
        return bool(self._expected != actual)

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the NotEqualMatcher instance for serialization.

        :return: A dictionary containing the expected value.
        """
        return {"expected": self._expected}

    @classmethod
    def __unpacked__(cls, *, expected: Any, **kwargs: Any) -> "NotEqualMatcher":
        """
        Unpack a NotEqualMatcher instance from its serialized form.

        :param expected: The expected value to use for the matcher.
        :param kwargs: Additional arguments (unused in this case).
        :return: A new instance of NotEqualMatcher.
        """
        return cls(expected)
