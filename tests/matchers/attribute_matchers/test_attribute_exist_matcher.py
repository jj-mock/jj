from unittest.mock import sentinel

import pytest

from jj.matchers import AttributeMatcher, ExistMatcher

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


def test_is_instance_of_attribute_matcher():
    with given:
        matcher = ExistMatcher()

    with when:
        actual = isinstance(matcher, AttributeMatcher)

    with then:
        assert actual is True


def test_repr():
    with given:
        matcher = ExistMatcher()

    with when:
        actual = repr(matcher)

    with then:
        assert actual == "ExistMatcher()"


def test_pack():
    with given:
        matcher = ExistMatcher()

    with when:
        actual = matcher.__packed__()

    with then:
        assert actual == {}


def test_unpack():
    with given:
        kwargs = {"future_field": sentinel}

    with when:
        actual = ExistMatcher.__unpacked__(**kwargs)

    with then:
        assert isinstance(actual, ExistMatcher)
