from jj.matchers import AttributeMatcher
from jj.matchers.attribute_matchers import RouteMatcher

from ..._test_utils.steps import given, then, when


def test_is_instance_of_attribute_matcher():
    with given:
        matcher = RouteMatcher("/")

    with when:
        actual = isinstance(matcher, AttributeMatcher)

    with then:
        assert actual is True


def test_repr():
    with given:
        matcher = RouteMatcher("/")

    with when:
        actual = repr(matcher)

    with then:
        assert actual == "RouteMatcher('/')"
