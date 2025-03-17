from typing import Any, Dict

from packed import packable

from ._attribute_matcher import AttributeMatcher

__all__ = ("ExistMatcher", "NotExistMatcher",)


@packable("jj.matchers.ExistMatcher")
class ExistMatcher(AttributeMatcher):
    """
    Matches any HTTP request.

    This matcher is used when the presence of a value is sufficient for matching,
    regardless of its actual content.
    """

    async def match(self, actual: Any) -> bool:
        """
        Always return `True`, as this matcher matches any request.

        :param actual: The value to match (unused in this case).
        :return: `True` for all requests.
        """
        return True

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the ExistMatcher instance for serialization.

        :return: An empty dictionary, as no specific state is stored.
        """
        return {}

    @classmethod
    def __unpacked__(cls, **kwargs: Any) -> "ExistMatcher":
        """
        Unpack an ExistMatcher instance from its serialized form.

        :param kwargs: Additional keyword arguments (ignored).
        :return: A new instance of ExistMatcher.
        """
        return cls()


@packable("jj.matchers.NotExistMatcher")
class NotExistMatcher(AttributeMatcher):
    """
    Matches when an attribute does not exist in the HTTP request.

    This matcher is used to check the absence of a value in the request attributes.
    If the attribute exists, the matcher does not match.
    """

    async def match(self, actual: Any) -> bool:
        """
        Return `False` if the attribute exists in the request.

        This method is called when an attribute key is present. Since this matcher
        is designed to match when the key does not exist, it always returns `False`.

        :param actual: The value to check (not used, as existence is the only criteria).
        :return: `False`, indicating the key exists.
        """
        return False

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the NotExistMatcher instance for serialization.

        :return: An empty dictionary, as no specific state is stored.
        """
        return {}

    @classmethod
    def __unpacked__(cls, **kwargs: Any) -> "NotExistMatcher":
        """
        Unpack a NotExistMatcher instance from its serialized form.

        :param kwargs: Additional keyword arguments (ignored).
        :return: A new instance of NotExistMatcher.
        """
        return cls()
