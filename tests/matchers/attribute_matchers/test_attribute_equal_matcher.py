import pytest
from asynctest.mock import MagicMock, Mock, sentinel

from jj.matchers import AttributeMatcher, EqualMatcher, NotEqualMatcher

from ..._test_utils.fixtures import request_, resolver_  # noqa: F401
from ..._test_utils.steps import given, then, when


@pytest.mark.parametrize(("expected", "actual", "res"), [
    ("1", "1", True),
    ("1", "2", False),
    ("2", "1", False),
])
def test_equal_matcher(expected, actual, res):
    with given:
        matcher = EqualMatcher(expected)

    with when:
        actual = matcher.match(actual)

    with then:
        assert actual is res


@pytest.mark.parametrize(("expected", "actual", "res"), [
    ("1", "1", False),
    ("1", "2", True),
    ("2", "1", True),
])
def test_not_equal_matcher(expected, actual, res):
    with given:
        matcher = NotEqualMatcher(expected)

    with when:
        actual = matcher.match(actual)

    with then:
        assert actual is res


@pytest.mark.parametrize("ret_val", [
    True,
    False,
])
def test_equal_matcher_with_magic_method(*, ret_val):
    with given:
        rec_ = MagicMock(__eq__=Mock(return_value=ret_val))
        matcher = EqualMatcher(sentinel.expected)

    with when:
        actual = matcher.match(rec_)

    with then:
        assert actual is ret_val
        assert rec_.__eq__.assert_called_with(sentinel.expected) is None


@pytest.mark.parametrize("ret_val", [
    True,
    False,
])
def test_not_equal_matcher_with_magic_method(*, ret_val):
    with given:
        rec_ = MagicMock(__ne__=Mock(return_value=ret_val))
        matcher = NotEqualMatcher(sentinel.expected)

    with when:
        actual = matcher.match(rec_)

    with then:
        assert actual is ret_val
        assert rec_.__ne__.assert_called_with(sentinel.expected) is None


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