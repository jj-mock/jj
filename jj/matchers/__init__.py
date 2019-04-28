from typing import Any

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


def equals(expected: Any) -> EqualMatcher:
    return EqualMatcher(expected)


def contains(expected: Any) -> ContainMatcher:
    return ContainMatcher(expected)
