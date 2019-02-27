from typing import Any

from .attribute_matchers import (AttributeMatcher, EqualMatcher, NotEqualMatcher,
                                 ContainMatcher, NotContainMatcher)
from .logical_matchers import LogicalMatcher, AllMatcher, AnyMatcher
from .request_matchers import (RequestMatcher, MethodMatcher, PathMatcher,
                               ParamMatcher, HeaderMatcher)
from .resolvable_matcher import ResolvableMatcher


__all__ = (
    "AttributeMatcher", "EqualMatcher", "NotEqualMatcher", "ContainMatcher", "NotContainMatcher",
    "LogicalMatcher", "AllMatcher", "AnyMatcher",
    "RequestMatcher", "MethodMatcher", "PathMatcher", "ParamMatcher", "HeaderMatcher",
    "ResolvableMatcher",
    "equals", "contains",
)


def equals(expected: Any) -> EqualMatcher:
    return EqualMatcher(expected)


def contains(expected: Any) -> ContainMatcher:
    return ContainMatcher(expected)
