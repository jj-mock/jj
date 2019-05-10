import pytest
from asynctest.mock import CoroutineMock as CoroMock
from asynctest.mock import Mock

from jj.matchers import AnyMatcher, LogicalMatcher, ResolvableMatcher

from ..._test_utils.fixtures import request_, resolver_
from ..._test_utils.steps import given, then, when


@pytest.mark.asyncio
@pytest.mark.parametrize(("ret_val", "res"), [
    (True, True),
    (False, False),
])
async def test_single_submatcher(ret_val, res, *, resolver_, request_):
    with given:
        submatcher_ = Mock(ResolvableMatcher, match=CoroMock(return_value=ret_val))
        matcher = AnyMatcher(resolver_, [submatcher_])

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is res
        assert submatcher_.match.assert_called_once_with(request_) is None


@pytest.mark.asyncio
@pytest.mark.parametrize(("ret_val1", "ret_val2", "res"), [
    (True, True, True),
    (True, False, True),
])
async def test_multiple_truthy_submatchers(ret_val1, ret_val2, res, *, resolver_, request_):
    with given:
        submatcher1_ = Mock(ResolvableMatcher, match=CoroMock(return_value=ret_val1))
        submatcher2_ = Mock(ResolvableMatcher, match=CoroMock(return_value=ret_val2))
        matcher = AnyMatcher(resolver_, [submatcher1_, submatcher2_])

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is res
        assert submatcher1_.match.assert_called_once_with(request_) is None
        assert submatcher2_.match.assert_not_called() is None


@pytest.mark.asyncio
@pytest.mark.parametrize(("ret_val1", "ret_val2", "res"), [
    (False, True, True),
    (False, False, False),
])
async def test_multiple_false_submatchers(ret_val1, ret_val2, res, *, resolver_, request_):
    with given:
        submatcher1_ = Mock(ResolvableMatcher, match=CoroMock(return_value=ret_val1))
        submatcher2_ = Mock(ResolvableMatcher, match=CoroMock(return_value=ret_val2))
        matcher = AnyMatcher(resolver_, [submatcher1_, submatcher2_])

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is res
        assert submatcher1_.match.assert_called_once_with(request_) is None
        assert submatcher2_.match.assert_called_once_with(request_) is None


def test_is_instance_of_logical_matcher(*, resolver_):
    with given:
        submatcher_ = Mock(ResolvableMatcher)
        matcher = AnyMatcher(resolver_, matchers=[submatcher_])

    with when:
        actual = isinstance(matcher, LogicalMatcher)

    with then:
        actual is True
