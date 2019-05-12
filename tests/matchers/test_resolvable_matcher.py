import pytest
from asynctest.mock import CoroutineMock as CoroMock
from asynctest.mock import Mock, call
from pytest import raises

from jj.matchers import ResolvableMatcher

from .._test_utils.fixtures import handler_, request_, resolver_  # noqa: F401
from .._test_utils.steps import given, then, when


@pytest.mark.asyncio
async def test_abstract_match_method_raises_error(*, resolver_, request_):
    with given:
        matcher = ResolvableMatcher(resolver=resolver_)

    with when, raises(Exception) as exception:
        await matcher.match(request_)

    with then:
        assert exception.type is NotImplementedError


@pytest.mark.asyncio
async def test_concrete_match_method_not_raises_error(*, resolver_, request_):
    with given:
        matcher_ = Mock(ResolvableMatcher, match=CoroMock(return_value=True))

    with when:
        actual = await matcher_.match(request_)

    with then:
        assert actual is True
        assert matcher_.mock_calls == [call.match(request_)]


@pytest.mark.asyncio
async def test_decorator_registers_matcher(*, resolver_, handler_):
    with given:
        matcher = ResolvableMatcher(resolver=resolver_)

    with when:
        actual = matcher(handler_)

    with then:
        assert actual == handler_
        assert resolver_.mock_calls == [call.register_matcher(matcher.match, handler_)]
        assert handler_.mock_calls == []


def test_repr(*, resolver_):
    with given:
        resolver_.__repr__ = Mock(return_value="<Resolver>")
        matcher = ResolvableMatcher(resolver=resolver_)

    with when:
        actual = repr(matcher)

    with then:
        assert actual == f"ResolvableMatcher(resolver=<Resolver>)"
