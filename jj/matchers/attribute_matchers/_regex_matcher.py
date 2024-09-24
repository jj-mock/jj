import re
from typing import Any, Dict

from packed import packable

from ._attribute_matcher import AttributeMatcher

__all__ = ("RegexMatcher",)


@packable("jj.matchers.RegexMatcher")
class RegexMatcher(AttributeMatcher):
    """
    Matches an HTTP request based on a regular expression pattern.

    This matcher evaluates if the actual value (e.g., a URL path or string) matches
    the specified regular expression pattern.
    """

    def __init__(self, pattern: str, flags: int = 0) -> None:
        """
        Initialize a RegexMatcher with a regex pattern and optional flags.

        :param pattern: The regular expression pattern to match.
        :param flags: Optional regex flags (e.g., `re.IGNORECASE`).
        """
        self._pattern = pattern
        self._flags = flags
        self._compiled = re.compile(self._pattern, self._flags)

    @property
    def pattern(self) -> str:
        """
        Return the regular expression pattern.

        :return: The regex pattern.
        """
        return self._pattern

    @property
    def flags(self) -> int:
        """
        Return the regex flags.

        :return: The regex flags.
        """
        return self._flags

    async def match(self, actual: Any) -> bool:
        """
        Determine if the actual value matches the regular expression pattern.

        :param actual: The value to match against the regex.
        :return: `True` if the value matches the pattern, otherwise `False`.
        """
        return self._compiled.search(actual) is not None

    def __repr__(self) -> str:
        """
        Return a string representation of the RegexMatcher instance.

        :return: A string describing the class, pattern, and flags.
        """
        if self._flags == 0:
            return f"{self.__class__.__qualname__}({self._pattern!r})"
        return f"{self.__class__.__qualname__}({self._pattern!r}, {self._flags!r})"

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the RegexMatcher instance for serialization.

        :return: A dictionary containing the pattern and flags.
        """
        return {"pattern": self._pattern, "flags": self._flags}

    @classmethod
    def __unpacked__(cls, *, pattern: str, flags: int = 0, **kwargs: Any) -> "RegexMatcher":
        """
        Unpack a RegexMatcher instance from its serialized form.

        :param pattern: The regex pattern to use for this matcher.
        :param flags: Optional regex flags.
        :param kwargs: Additional arguments (unused in this case).
        :return: A new instance of RegexMatcher.
        """
        return cls(pattern, flags)
