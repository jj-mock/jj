from typing import Any, Dict, List, Tuple, Union

from multidict import MultiDict, MultiMapping

from ._attribute_matcher import AttributeMatcher
from ._equal_matcher import EqualMatcher

__all__ = ("MultiDictMatcher",)


StrOrAttrMatcher = Union[str, AttributeMatcher]
DictOrTupleList = Union[
    Dict[str, StrOrAttrMatcher],
    List[Tuple[str, StrOrAttrMatcher]],
]


class MultiDictMatcher(AttributeMatcher):
    def __init__(self, expected: DictOrTupleList) -> None:
        self._expected = MultiDict(expected)

    async def _match_any(self, submatcher: AttributeMatcher, values: List[Any]) -> bool:
        for value in values:
            if await submatcher.match(value):
                return True
        return False

    async def match(self, actual: MultiMapping[str]) -> bool:
        assert isinstance(actual, MultiMapping)

        for key, val in self._expected.items():
            submatcher = val if isinstance(val, AttributeMatcher) else EqualMatcher(val)
            values = actual.getall(key, [])
            if not await self._match_any(submatcher, values):
                return False
        return True

    def __repr__(self) -> str:
        expected = [(key, val) for key, val in self._expected.items()]
        return f"{self.__class__.__qualname__}({expected!r})"
