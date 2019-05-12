import pytest

from jj.matchers import (
    ContainMatcher,
    EqualMatcher,
    ExistMatcher,
    NotContainMatcher,
    NotEqualMatcher,
    contains,
    equals,
    exists,
    not_contains,
    not_equals,
)

from ..._test_utils.steps import given, then, when


@pytest.mark.parametrize(("instance_factory", "instance_class"), [
    (lambda: exists, ExistMatcher),
    (lambda: equals("smth"), EqualMatcher),
    (lambda: not_equals("smth"), NotEqualMatcher),
    (lambda: contains("smth"), ContainMatcher),
    (lambda: not_contains("smth"), NotContainMatcher),
])
def test_is_instance_of(instance_factory, instance_class):
    with given:
        matcher = instance_factory()

    with when:
        actual = isinstance(matcher, instance_class)

    with then:
        assert actual is True


@pytest.mark.parametrize(("instance_factory", "representation"), [
    (lambda: exists, "exists"),
    (lambda: equals("smth"), "equals('smth')"),
    (lambda: not_equals("smth"), "not_equals('smth')"),
    (lambda: contains("smth"), "contains('smth')"),
    (lambda: not_contains("smth"), "not_contains('smth')"),
])
def test_repr(instance_factory, representation):
    with given:
        matcher = instance_factory()

    with when:
        actual = repr(matcher)

    with then:
        assert actual == representation
