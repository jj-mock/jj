from unittest.mock import AsyncMock, Mock, call, sentinel

import pytest
from pytest import raises

from jj.matchers import AllMatcher, LogicalMatcher, ResolvableMatcher

from ..._test_utils.fixtures import request_, resolver_
from ..._test_utils.steps import given, then, when

__all__ = ("request_", "resolver_",)


@pytest.mark.asyncio
@pytest.mark.parametrize(("ret_val", "res"), [
    (True, True),
    (False, False),
])
async def test_single_submatcher(ret_val, res, *, resolver_, request_):
    with given:
        submatcher_ = Mock(ResolvableMatcher, match=AsyncMock(return_value=ret_val))
        matcher = AllMatcher([submatcher_], resolver=resolver_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is res
        assert submatcher_.mock_calls == [call.match(request_)]


@pytest.mark.asyncio
@pytest.mark.parametrize(("ret_val1", "ret_val2", "res"), [
    (True, True, True),
    (True, False, False),
])
async def test_multiple_truthy_submatchers(ret_val1, ret_val2, res, *, resolver_, request_):
    with given:
        submatcher1_ = Mock(ResolvableMatcher, match=AsyncMock(return_value=ret_val1))
        submatcher2_ = Mock(ResolvableMatcher, match=AsyncMock(return_value=ret_val2))
        matcher = AllMatcher([submatcher1_, submatcher2_], resolver=resolver_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is res
        assert submatcher1_.mock_calls == [call.match(request_)]
        assert submatcher2_.mock_calls == [call.match(request_)]


@pytest.mark.asyncio
@pytest.mark.parametrize(("ret_val1", "ret_val2", "res"), [
    (False, True, False),
    (False, False, False),
])
async def test_multiple_false_submatchers(ret_val1, ret_val2, res, *, resolver_, request_):
    with given:
        submatcher1_ = Mock(ResolvableMatcher, match=AsyncMock(return_value=ret_val1))
        submatcher2_ = Mock(ResolvableMatcher, match=AsyncMock(return_value=ret_val2))
        matcher = AllMatcher([submatcher1_, submatcher2_], resolver=resolver_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is res
        assert submatcher1_.mock_calls == [call.match(request_)]
        assert submatcher2_.mock_calls == []


def test_empty_submatchers_raises_exception(*, resolver_):
    with when, raises(Exception) as exception:
        AllMatcher([], resolver=resolver_)

    with then:
        assert exception.type is AssertionError


def test_is_instance_of_logical_matcher(*, resolver_):
    with given:
        submatcher_ = Mock(ResolvableMatcher)
        matcher = AllMatcher([submatcher_], resolver=resolver_)

    with when:
        actual = isinstance(matcher, LogicalMatcher)

    with then:
        assert actual is True


def test_repr(*, resolver_):
    with given:
        resolver_.__repr__ = Mock(return_value="<Resolver>")
        matcher = AllMatcher(resolver=resolver_, matchers=[
            Mock(ResolvableMatcher, __repr__=Mock(return_value="<SubMatcher1>")),
            Mock(ResolvableMatcher, __repr__=Mock(return_value="<SubMatcher2>")),
        ])

    with when:
        actual = repr(matcher)

    with then:
        assert actual == "AllMatcher([<SubMatcher1>, <SubMatcher2>], resolver=<Resolver>)"


def test_pack(*, resolver_):
    with given:
        submatchers = [Mock(ResolvableMatcher), Mock(ResolvableMatcher)]
        matcher = AllMatcher(submatchers, resolver=resolver_)

    with when:
        actual = matcher.__packed__()

    with then:
        assert actual == {"matchers": submatchers}


def test_unpack(*, resolver_):
    with given:
        submatchers = [Mock(ResolvableMatcher), Mock(ResolvableMatcher)]
        kwargs = {
            "matchers": submatchers,
            "resolver": resolver_,
            "future_field": sentinel,
        }

    with when:
        actual = AllMatcher.__unpacked__(**kwargs)

    with then:
        assert isinstance(actual, AllMatcher)


def test_sub_matchers_property(*, resolver_):
    with given:
        sub_matchers = [Mock(ResolvableMatcher), Mock(ResolvableMatcher)]
        matcher = AllMatcher(sub_matchers, resolver=resolver_)

    with when:
        actual = matcher.sub_matchers

    with then:
        assert actual == sub_matchers
