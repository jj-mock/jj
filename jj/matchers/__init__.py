from ._resolvable_matcher import ResolvableMatcher
from .attribute_matchers import (
    AttributeMatcher,
    ContainMatcher,
    EqualMatcher,
    ExistMatcher,
    NotContainMatcher,
    NotEqualMatcher,
)
from .logical_matchers import AllMatcher, AnyMatcher, LogicalMatcher
from .request_matchers import (
    HeaderMatcher,
    MethodMatcher,
    ParamMatcher,
    PathMatcher,
    RequestMatcher,
)

__all__ = (
    "AttributeMatcher", "EqualMatcher", "NotEqualMatcher", "ExistMatcher",
    "ContainMatcher", "NotContainMatcher", "LogicalMatcher", "AllMatcher", "AnyMatcher",
    "RequestMatcher", "MethodMatcher", "PathMatcher", "ParamMatcher", "HeaderMatcher",
    "ResolvableMatcher", "exists", "equals", "not_equals", "contains", "not_contains",
)


class equals(EqualMatcher):
    pass


class not_equals(NotEqualMatcher):
    pass


class contains(ContainMatcher):
    pass


class not_contains(NotContainMatcher):
    pass


class _exists(ExistMatcher):
    def __repr__(self) -> str:
        return "exists"


exists = _exists()
