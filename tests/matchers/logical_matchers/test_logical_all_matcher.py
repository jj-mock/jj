import pytest
from asynctest.mock import CoroutineMock as CoroMock
from asynctest.mock import Mock, call
from pytest import raises

from jj.matchers import AllMatcher, LogicalMatcher, ResolvableMatcher

from ..._test_utils.fixtures import request_, resolver_  # noqa: F401
from ..._test_utils.steps import given, then, when


@pytest.mark.asyncio
@pytest.mark.parametrize(("ret_val", "res"), [
    (True, True),
    (False, False),
])
async def test_single_submatcher(ret_val, res, *, resolver_, request_):
    with given:
        submatcher_ = Mock(ResolvableMatcher, match=CoroMock(return_value=ret_val))
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
        submatcher1_ = Mock(ResolvableMatcher, match=CoroMock(return_value=ret_val1))
        submatcher2_ = Mock(ResolvableMatcher, match=CoroMock(return_value=ret_val2))
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
        submatcher1_ = Mock(ResolvableMatcher, match=CoroMock(return_value=ret_val1))
        submatcher2_ = Mock(ResolvableMatcher, match=CoroMock(return_value=ret_val2))
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
        assert actual == f"AllMatcher([<SubMatcher1>, <SubMatcher2>], resolver=<Resolver>)"
