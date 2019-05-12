import re

import pytest

from jj.matchers import AttributeMatcher, RegexMatcher

from ..._test_utils.steps import given, then, when


@pytest.mark.asyncio
@pytest.mark.parametrize(("expected_factory", "actual", "res"), [
    (lambda: RegexMatcher("smth"), "smth", True),
    (lambda: RegexMatcher("smth"), "test", False),

    (lambda: RegexMatcher("[0-9]+"), "1234", True),
    (lambda: RegexMatcher("[0-9]+"), "test", False),

    # search vs match
    (lambda: RegexMatcher("smth"), "-smth-", True),
    (lambda: RegexMatcher("[0-9]+"), "-1234-", True),

    # flags
    (lambda: RegexMatcher("smth"), "SMTH", False),
    (lambda: RegexMatcher("smth", re.I), "SMTH", True),
    (lambda: RegexMatcher("[a-z]+"), "smth", True),
    (lambda: RegexMatcher("[a-z]+"), "SMTH", False),
    (lambda: RegexMatcher("[a-z]+", re.I), "SMTH", True),
])
async def test_exist_matcher(expected_factory, actual, res):
    with given:
        matcher = expected_factory()

    with when:
        actual = await matcher.match(actual)

    with then:
        assert actual is res


def test_is_instance_of_attribute_matcher():
    with given:
        matcher = RegexMatcher(".*")

    with when:
        actual = isinstance(matcher, AttributeMatcher)

    with then:
        assert actual is True


@pytest.mark.parametrize(("instance_factory", "representation"), [
    (lambda: RegexMatcher(".*"), "RegexMatcher('.*')"),

    (lambda: RegexMatcher(".*", re.I),
     "RegexMatcher('.*', <RegexFlag.IGNORECASE: 2>)"),

    (lambda: RegexMatcher(".*", re.I | re.M),
     "RegexMatcher('.*', <RegexFlag.MULTILINE|IGNORECASE: 10>)"),
])
def test_repr(instance_factory, representation):
    with given:
        matcher = instance_factory()

    with when:
        actual = repr(matcher)

    with then:
        assert actual == representation
