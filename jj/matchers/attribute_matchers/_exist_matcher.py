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
class NotExistMatcher(ExistMatcher):
    async def match(self, actual: Any) -> bool:
        # If this method is called, it means that there is at least one value for the key.
        # In that case, the key exists, so we return False.
        return False

    def __packed__(self) -> Dict[str, Any]:
        return {}

    @classmethod
    def __unpacked__(cls, **kwargs: Any) -> "NotExistMatcher":
        return cls()
