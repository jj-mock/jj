from typing import Any, Dict, List, Tuple, Union

from multidict import MultiDict, MultiMapping
from packed import packable

from ._attribute_matcher import AttributeMatcher
from ._equal_matcher import EqualMatcher
from ._exist_matcher import NotExistMatcher

__all__ = ("MultiDictMatcher", "StrOrAttrMatcher", "DictOrTupleList",)

StrOrAttrMatcher = Union[str, AttributeMatcher]
DictOrTupleList = Union[
    Dict[str, StrOrAttrMatcher],
    List[Tuple[str, StrOrAttrMatcher]],
]


@packable("jj.matchers.MultiDictMatcher")
class MultiDictMatcher(AttributeMatcher):
    """
    Matches HTTP requests based on multiple key-value pairs, such as query parameters or headers.

    This matcher checks if the actual request contains key-value pairs that match
    the expected key-value pairs, with the option to use either static values
    or dynamic matchers for each value.
    """

    def __init__(self, expected: DictOrTupleList) -> None:
        """
        Initialize a MultiDictMatcher with the expected key-value pairs.

        :param expected: The expected key-value pairs to match, provided as a dictionary
                         or list of tuples.
        """
        self._expected = MultiDict(expected)

    @property
    def expected(self) -> MultiDict[StrOrAttrMatcher]:
        """
        Return the expected key-value pairs for this matcher.

        :return: A MultiDict containing the expected key-value pairs.
        """
        return self._expected

    async def _match_any(self, submatcher: AttributeMatcher, values: List[Any]) -> bool:
        """
        Determine if any value in the list matches the given submatcher.

        :param submatcher: The matcher to evaluate each value.
        :param values: A list of values to be evaluated.
        :return: `True` if any value matches the submatcher, otherwise `False`.
        """
        for value in values:
            if await submatcher.match(value):
                return True
        return False

    async def match(self, actual: MultiMapping[str]) -> bool:
        """
        Determine if the actual request data satisfies the expected key-value conditions.

        :param actual: A MultiMapping representing request attributes (e.g., headers or
                       query parameters).
        :return: `True` if all expected conditions are met, otherwise `False`.
        """
        if not isinstance(actual, MultiMapping):
            raise TypeError(f"Expected MultiMapping, got '{type(actual).__name__}'")

        for key, val in self._expected.items():
            # 1) Special case: key must NOT exist
            if isinstance(val, NotExistMatcher):
                # If the key exists in `actual`, fail immediately
                if key in actual:
                    return False
                # Otherwise, key does not exist, so this condition is met
                continue

            # 2) Normal case: key must exist, and at least one value must match
            submatcher = val if isinstance(val, AttributeMatcher) else EqualMatcher(val)
            values: List[Any] = actual.getall(key, [])
            if not await self._match_any(submatcher, values):
                return False

        # All expected conditions are satisfied
        return True

    def __repr__(self) -> str:
        """
        Return a string representation of the MultiDictMatcher instance.

        :return: A string describing the class and expected key-value pairs.
        """
        expected = [(key, val) for key, val in self._expected.items()]
        return f"{self.__class__.__qualname__}({expected!r})"

    def __packed__(self) -> Dict[str, Any]:
        """
        Pack the MultiDictMatcher instance for serialization.

        :return: A dictionary containing the serialized expected key-value pairs.
        """
        expected = [[key, val] for key, val in self._expected.items()]
        return {"expected": expected}

    @classmethod
    def __unpacked__(cls, *, expected: DictOrTupleList, **kwargs: Any) -> "MultiDictMatcher":
        """
        Unpack a MultiDictMatcher instance from its serialized form.

        :param expected: The expected key-value pairs to use for this matcher.
        :param kwargs: Additional keyword arguments (ignored).
        :return: A new instance of MultiDictMatcher.
        """
        return cls(expected)
