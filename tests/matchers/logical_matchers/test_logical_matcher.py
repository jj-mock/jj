import pytest
from asynctest.mock import Mock
from pytest import raises

from jj.matchers import LogicalMatcher, ResolvableMatcher

from ..._test_utils.fixtures import request_, resolver_  # noqa: F401
from ..._test_utils.steps import given, then, when


@pytest.mark.asyncio
async def test_abstract_match_method_raises_exception(*, resolver_, request_):
    with given:
        matcher = LogicalMatcher(resolver=resolver_)

    with when, raises(Exception) as exception:
        await matcher.match(request_)

    with then:
        assert exception.type is NotImplementedError


def test_is_instance_of_resolvable_matcher(*, resolver_):
    with given:
        matcher = LogicalMatcher(resolver=resolver_)

    with when:
        actual = isinstance(matcher, ResolvableMatcher)

    with then:
        assert actual is True


def test_repr(*, resolver_):
    with given:
        resolver_.__repr__ = Mock(return_value="<Resolver>")
        matcher = LogicalMatcher(resolver=resolver_)

    with when:
        actual = repr(matcher)

    with then:
        assert actual == f"LogicalMatcher(resolver=<Resolver>)"
