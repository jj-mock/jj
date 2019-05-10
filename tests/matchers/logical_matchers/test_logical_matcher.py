import pytest
from asynctest.mock import Mock
from pytest import raises

from jj.matchers import LogicalMatcher, ResolvableMatcher

from ..._test_utils.fixtures import request_, resolver_
from ..._test_utils.steps import given, then, when


@pytest.mark.asyncio
async def test_abstract_match_method_raises_exception(*, resolver_, request_):
    with given:
        submatcher_ = Mock(ResolvableMatcher)
        matcher = LogicalMatcher(resolver_, matchers=[submatcher_])

    with when, raises(Exception) as exception:
        await matcher.match(request_)

    with then:
        assert exception.type is NotImplementedError


def test_empty_submatchers_raises_exception(*, resolver_):
    with when, raises(Exception) as exception:
        LogicalMatcher(resolver_, matchers=[])

    with then:
        assert exception.type is AssertionError


def test_is_instance_of_resolvable_matcher(*, resolver_):
    with given:
        submatcher_ = Mock(ResolvableMatcher)
        matcher = LogicalMatcher(resolver_, matchers=[submatcher_])

    with when:
        actual = isinstance(matcher, ResolvableMatcher)

    with then:
        assert actual is True
