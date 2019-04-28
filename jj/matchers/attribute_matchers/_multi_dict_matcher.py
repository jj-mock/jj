from typing import Dict, List, Tuple, Union

from multidict import MultiDict, MultiDictProxy

from ._attribute_matcher import AttributeMatcher
from ._contain_matcher import ContainMatcher

__all__ = ("MultiDictMatcher",)


StrOrAttrMatcher = Union[str, AttributeMatcher]
DictOrTupleList = Union[
    Dict[str, StrOrAttrMatcher],
    List[Tuple[str, StrOrAttrMatcher]],
]


class MultiDictMatcher(AttributeMatcher):
    def __init__(self, expected: DictOrTupleList) -> None:
        self._expected = MultiDictProxy(MultiDict(expected))

    def match(self, actual: Union[MultiDict, MultiDictProxy]) -> bool:
        for key, val in self._expected.items():
            matcher = val if isinstance(val, AttributeMatcher) else ContainMatcher(val)
            if not matcher.match(actual.getall(key, [])):
                return False
        return True
