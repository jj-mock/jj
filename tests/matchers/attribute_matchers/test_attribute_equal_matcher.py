import pytest
from asynctest.mock import sentinel

from jj.matchers import AttributeMatcher, EqualMatcher, NotEqualMatcher

from ..._test_utils.fixtures import request_, resolver_  # noqa: F401
from ..._test_utils.steps import given, then, when


@pytest.mark.parametrize(("expected", "actual", "res"), [
    (sentinel.value, sentinel.value, True),
    (sentinel.value, sentinel.another_value, False),
    (sentinel.another_value, sentinel.value, False),
])
def test_equal_matcher(expected, actual, res):
    with given:
        matcher = EqualMatcher(expected)

    with when:
        actual = matcher.match(actual)

    with then:
        assert actual is res


@pytest.mark.parametrize(("expected", "actual", "res"), [
    (sentinel.value, sentinel.value, False),
    (sentinel.value, sentinel.another_value, True),
    (sentinel.another_value, sentinel.value, True),
])
def test_not_equal_matcher(expected, actual, res):
    with given:
        matcher = NotEqualMatcher(expected)

    with when:
        actual = matcher.match(actual)

    with then:
        assert actual is res


@pytest.mark.parametrize("matcher_class", [
    EqualMatcher,
    NotEqualMatcher,
])
def test_is_instance_of_attribute_matcher(*, matcher_class):
    with given:
        matcher = matcher_class(sentinel.expected)

    with when:
        actual = isinstance(matcher, AttributeMatcher)

    with then:
        assert actual is True
