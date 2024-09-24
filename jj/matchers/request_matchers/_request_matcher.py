from .._resolvable_matcher import ResolvableMatcher

__all__ = ("RequestMatcher",)


class RequestMatcher(ResolvableMatcher):
    """
    Serves as a base class for specific HTTP request matchers.

    Inherits from `ResolvableMatcher` and is intended to be subclassed by
    matchers that deal with different aspects of an HTTP request, such as
    method, path, headers, etc.
    """
    pass
