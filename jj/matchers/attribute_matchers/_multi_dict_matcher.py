from typing import Dict, List, Tuple, Union

from multidict import MultiDict, MultiDictProxy, MultiMapping

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
        self._expected = MultiDictProxy(MultiDict(expected))

    def match(self, actual: MultiMapping[str]) -> bool:
        assert isinstance(actual, MultiMapping)

        for key, val in self._expected.items():
            submatcher = val if isinstance(val, AttributeMatcher) else EqualMatcher(val)
            values = actual.getall(key, [])
            if not any(submatcher.match(value) for value in values):
                return False

        return True
