import pytest
from asynctest.mock import MagicMock, Mock, sentinel

from jj.matchers import AttributeMatcher, ContainMatcher, NotContainMatcher

from ..._test_utils.fixtures import request_, resolver_  # noqa: F401
from ..._test_utils.steps import given, then, when


@pytest.mark.parametrize(("expected", "actual", "res"), [
    ("1", ["1"], True),
    ("1", ["2", "1"], True),
    ("2", ["1"], False),
    ("2", ["1", "3"], False),
])
def test_contain_matcher(expected, actual, res):
    with given:
        matcher = ContainMatcher(expected)

    with when:
        actual = matcher.match(actual)

    with then:
        assert actual is res


@pytest.mark.parametrize(("expected", "actual", "res"), [
    ("1", ["1"], False),
    ("1", ["2", "1"], False),
    ("2", ["1"], True),
    ("2", ["1", "3"], True),
])
def test_not_not_contain_matcher(expected, actual, res):
    with given:
        matcher = NotContainMatcher(expected)

    with when:
        actual = matcher.match(actual)

    with then:
        assert actual is res


@pytest.mark.parametrize("ret_val", [
    True,
    False,
])
def test_contain_matcher_with_magic_method(*, ret_val):
    with given:
        rec_ = MagicMock(__contains__=Mock(return_value=ret_val))
        matcher = ContainMatcher(sentinel.expected)

    with when:
        actual = matcher.match(rec_)

    with then:
        assert actual is ret_val
        assert rec_.__contains__.assert_called_with(sentinel.expected) is None


@pytest.mark.parametrize("ret_val", [
    True,
    False,
])
def test_not_contain_matcher_with_magic_method(*, ret_val):
    with given:
        rec_ = MagicMock(__contains__=Mock(return_value=not ret_val))
        matcher = NotContainMatcher(sentinel.expected)

    with when:
        actual = matcher.match(rec_)

    with then:
        assert actual is ret_val
        assert rec_.__contains__.assert_called_with(sentinel.expected) is None


@pytest.mark.parametrize("matcher_class", [
    ContainMatcher,
    NotContainMatcher,
])
def test_is_instance_of_attribute_matcher(*, matcher_class):
    with given:
        matcher = matcher_class(sentinel.expected)

    with when:
        actual = isinstance(matcher, AttributeMatcher)

    with then:
        assert actual is True