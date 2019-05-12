import pytest
from asynctest.mock import sentinel

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
