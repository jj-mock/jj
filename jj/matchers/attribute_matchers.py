from typing import Union, Dict, Any, List, Tuple

from aiohttp.web_urldispatcher import DynamicResource
from multidict import MultiDict, MultiDictProxy


__all__ = ("AttributeMatcher", "EqualMatcher", "NotEqualMatcher",
           "ContainMatcher", "NotContainMatcher",
           "RouteMatcher", "MultiDictMatcher")


class AttributeMatcher:
    def match(self, expected: Any) -> bool:
        raise NotImplementedError()


class EqualMatcher(AttributeMatcher):
    def __init__(self, expected: Any) -> None:
        self._expected = expected

    def match(self, actual: Any) -> bool:
        return self._expected == actual


class NotEqualMatcher(EqualMatcher):
    def match(self, actual: Any) -> bool:
        return self._expected != actual


class ContainMatcher(AttributeMatcher):
    def __init__(self, expected: Any) -> None:
        self._expected = expected

    def match(self, actual: Any) -> bool:
        return self._expected in actual


class NotContainMatcher(ContainMatcher):
    def match(self, actual: Any) -> bool:
        return self._expected not in actual


class RouteMatcher(AttributeMatcher):
    class Resource(DynamicResource):
        # Метод match почему-то protected, поэтому пришлось унаследоваться
        def match(self, path: str) -> Union[Dict[str, str], None]:
            return self._match(path)

    def __init__(self, path: str) -> None:
        # Сохраняем полную совместимость с aiohttp матчером роутов
        self._resource = self.Resource(path)

    def match(self, path: str) -> bool:
        return self._resource.match(path) is not None


StrOrAttrMatcher = Union[
    str,
    AttributeMatcher
]
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
