from typing import Any, Dict
from urllib.parse import parse_qs

from packed import packable

from ...requests import Request
from ...resolvers import Resolver
from ._request_matcher import RequestMatcher

__all__ = ("FormDataMatcher",)


@packable("jj.matchers.FormDataMatcher")
class FormDataMatcher(RequestMatcher):
    """
    Matches HTTP requests based on a form-urlencoded body field value.

    This matcher checks if the incoming request body contains a form field
    with the specified name and exact value.
    """

    def __init__(self, key: str, value: str, *, resolver: Resolver) -> None:
        """
        Initialize a FormDataMatcher with the form field and resolver.

        :param key: The name of the form field to match.
        :param value: The expected value of the form field.
        :param resolver: The resolver responsible for registering this matcher.
        """
        super().__init__(resolver=resolver)
        self._key = key
        self._value = value

    async def match(self, request: Request) -> bool:
        """
        Determine if the request body contains the expected form field value.

        :param request: The HTTP request containing the form body to match.
        :return: `True` if the form field matches the expected value, otherwise `False`.
        """
        try:
            body_text = await request.text()
        except Exception:
            return False
        params = parse_qs(body_text)
        return params.get(self._key) == [self._value]

    def __repr__(self) -> str:
        """
        Return a string representation of the FormDataMatcher instance.

        :return: A string describing the class, field, and resolver.
        """
        return (
            f"{self.__class__.__qualname__}"
            f"(key={self._key!r}, value={self._value!r}, resolver={self._resolver!r})"
        )

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the FormDataMatcher instance for serialization.

        :return: A dictionary containing the serialized form of the matcher.
        """
        return {
            "key": self._key,
            "value": self._value,
        }

    @classmethod
    def __unpacked__(cls, *,
                     key: str,
                     value: str,
                     resolver: Resolver,
                     **kwargs: Any) -> "FormDataMatcher":
        """
        Unpack a FormDataMatcher instance from its serialized form.

        :param key: The form field name to use for this instance.
        :param value: The expected form field value.
        :param resolver: The resolver to bind this matcher to.
        :param kwargs: Additional keyword arguments (ignored).
        :return: A new instance of FormDataMatcher.
        """
        return cls(key, value, resolver=resolver)
