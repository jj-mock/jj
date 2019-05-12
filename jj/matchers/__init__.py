from ._resolvable_matcher import ResolvableMatcher
from .attribute_matchers import (
    AttributeMatcher,
    ContainMatcher,
    EqualMatcher,
    ExistMatcher,
    NotContainMatcher,
    NotEqualMatcher,
    RegexMatcher,
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
    "AllMatcher",
    "AnyMatcher",
    "AttributeMatcher",
    "ContainMatcher",
    "contains",
    "EqualMatcher",
    "equals",
    "ExistMatcher",
    "exists",
    "HeaderMatcher",
    "LogicalMatcher",
    "MethodMatcher",
    "not_contains",
    "not_equals",
    "NotContainMatcher",
    "NotEqualMatcher",
    "ParamMatcher",
    "PathMatcher",
    "regex",
    "RegexMatcher",
    "RequestMatcher",
    "ResolvableMatcher",
)


class equals(EqualMatcher):
    pass


class not_equals(NotEqualMatcher):
    pass


class contains(ContainMatcher):
    pass


class not_contains(NotContainMatcher):
    pass


class regex(RegexMatcher):
    pass


class _exists(ExistMatcher):
    def __repr__(self) -> str:
        return "exists"


exists = _exists()
