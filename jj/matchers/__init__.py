from packed import packable

from ._resolvable_matcher import ResolvableMatcher
from .attribute_matchers import (
    AttributeMatcher,
    ContainMatcher,
    EqualMatcher,
    ExistMatcher,
    NotContainMatcher,
    NotEqualMatcher,
    NotExistMatcher,
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
    "NotExistMatcher",
    "exists",
    "not_exists",
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


@packable("jj.matchers.equals")
class equals(EqualMatcher):
    pass


@packable("jj.matchers.not_equals")
class not_equals(NotEqualMatcher):
    pass


@packable("jj.matchers.contains")
class contains(ContainMatcher):
    pass


@packable("jj.matchers.not_contains")
class not_contains(NotContainMatcher):
    pass


@packable("jj.matchers.regex")
class regex(RegexMatcher):
    pass


@packable("jj.matchers.exists")
class _exists(ExistMatcher):
    def __repr__(self) -> str:
        return "exists"


exists = _exists()


@packable("jj.matchers.not_exists")
class _not_exists(NotExistMatcher):
    def __repr__(self) -> str:
        return "not_exists"


not_exists = _not_exists()
