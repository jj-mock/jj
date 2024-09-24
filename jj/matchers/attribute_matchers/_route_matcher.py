from typing import Any, Dict, Union

from aiohttp.web_urldispatcher import DynamicResource
from packed import packable

from ._attribute_matcher import AttributeMatcher

__all__ = ("RouteMatcher",)


class _Resource(DynamicResource):
    """
    A resource that defines the logic for matching URL paths.

    This class extends `DynamicResource` from aiohttp and provides the
    ability to match a URL path against a predefined route pattern.
    """

    def match(self, path: str) -> Union[Dict[str, str], None]:
        """
        Match the given path against the route pattern.

        :param path: The URL path to match.
        :return: A dictionary of matched segments if the path matches, otherwise `None`.
        """
        return self._match(path)


@packable("jj.matchers.RouteMatcher")
class RouteMatcher(AttributeMatcher):
    """
    Matches HTTP requests based on a URL route pattern.

    This matcher evaluates whether the request path matches a predefined route pattern,
    and can extract segments from the path.
    """

    def __init__(self, path: str) -> None:
        """
        Initialize a RouteMatcher with the expected route path.

        :param path: The URL route pattern to match.
        """
        self._path = path
        self._resource = _Resource(path)

    @property
    def path(self) -> str:
        """
        Return the expected route path.

        :return: The route pattern.
        """
        return self._path

    def get_segments(self, path: str) -> Dict[str, str]:
        """
        Extract and return segments from the given path.

        :param path: The URL path to extract segments from.
        :return: A dictionary of matched segments.
        """
        return self._resource.match(path) or {}

    async def match(self, path: str) -> bool:
        """
        Determine if the actual path matches the expected route pattern.

        :param path: The URL path to match.
        :return: `True` if the path matches the route pattern, otherwise `False`.
        """
        return self._resource.match(path) is not None

    def __repr__(self) -> str:
        """
        Return a string representation of the RouteMatcher instance.

        :return: A string describing the class and expected route pattern.
        """
        return f"{self.__class__.__qualname__}({self._path!r})"

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the RouteMatcher instance for serialization.

        :return: A dictionary containing the expected route path.
        """
        return {"path": self._path}

    @classmethod
    def __unpacked__(cls, *, path: str, **kwargs: Any) -> "RouteMatcher":
        """
        Unpack a RouteMatcher instance from its serialized form.

        :param path: The expected route pattern to use for this matcher.
        :param kwargs: Additional keyword arguments (ignored).
        :return: A new instance of RouteMatcher.
        """
        return cls(path)
