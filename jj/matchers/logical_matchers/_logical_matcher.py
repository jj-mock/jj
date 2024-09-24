from .._resolvable_matcher import ResolvableMatcher

__all__ = ("LogicalMatcher",)


class LogicalMatcher(ResolvableMatcher):
    """
    Serves as a base class for logical matchers that combine multiple matchers.

    Logical matchers, such as `AnyMatcher` and `AllMatcher`, use this class as
    a foundation to combine several `ResolvableMatcher` instances, enabling
    the creation of more complex matching rules.
    """
    pass
