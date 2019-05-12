from ._resolvable_matcher import ResolvableMatcher
from .attribute_matchers import (
    AttributeMatcher,
    ContainMatcher,
    EqualMatcher,
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
    "AttributeMatcher", "EqualMatcher", "NotEqualMatcher",
    "ContainMatcher", "NotContainMatcher", "LogicalMatcher", "AllMatcher", "AnyMatcher",
    "RequestMatcher", "MethodMatcher", "PathMatcher", "ParamMatcher", "HeaderMatcher",
    "ResolvableMatcher", "equals", "contains",
)


class equals(EqualMatcher):
    pass


class not_equals(NotEqualMatcher):
    pass


class contains(ContainMatcher):
    pass


class not_contains(NotContainMatcher):
    pass
