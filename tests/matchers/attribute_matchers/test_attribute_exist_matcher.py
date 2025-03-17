from unittest.mock import sentinel

import pytest

from jj.matchers import AttributeMatcher, ExistMatcher, NotExistMatcher

from ..._test_utils.steps import given, then, when


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [None, "smth", sentinel.value])
async def test_exist_matcher(value):
    with given:
        matcher = ExistMatcher()

    with when:
        actual = await matcher.match(value)

    with then:
        assert actual is True


@pytest.mark.parametrize("matcher_class", [ExistMatcher, NotExistMatcher])
def test_is_instance_of_attribute_matcher(matcher_class):
    with given:
        matcher = matcher_class()

    with when:
        actual = isinstance(matcher, AttributeMatcher)

    with then:
        assert actual is True


@pytest.mark.parametrize(("matcher_class", "expected"), [
    (ExistMatcher, "ExistMatcher()"),
    (NotExistMatcher, "NotExistMatcher()"),
])
def test_repr(matcher_class, expected):
    with given:
        matcher = matcher_class()

    with when:
        actual = repr(matcher)

    with then:
        assert actual == expected


@pytest.mark.parametrize("matcher_class", [ExistMatcher, NotExistMatcher])
def test_pack(matcher_class):
    with given:
        matcher = matcher_class()

    with when:
        actual = matcher.__packed__()

    with then:
        assert actual == {}


@pytest.mark.parametrize("matcher_class", [ExistMatcher, NotExistMatcher])
def test_unpack(matcher_class):
    with given:
        kwargs = {"future_field": sentinel}

    with when:
        actual = matcher_class.__unpacked__(**kwargs)

    with then:
        assert isinstance(actual, matcher_class)


@pytest.mark.asyncio
@pytest.mark.parametrize("value", [None, "smth", sentinel.value])
async def test_not_exist_matcher(value):
    with given:
        matcher = NotExistMatcher()

    with when:
        actual = await matcher.match(value)

    with then:
        assert actual is False
