import pytest
from asynctest.mock import CoroutineMock, Mock, sentinel
from pytest import raises

from jj.matchers import ResolvableMatcher
from jj.requests import Request
from jj.resolvers import Resolver

from .._test_utils import given, then, when


@pytest.fixture
def resolver_():
    return Mock(Resolver)


@pytest.fixture
def request_():
    return Mock(Request)


@pytest.fixture
def handler_():
    return CoroutineMock(return_value=sentinel.response)


@pytest.mark.asyncio
async def test_abstract_match_method_raises_error(resolver_: Mock, request_: Mock):
    with given:
        matcher = ResolvableMatcher(resolver_)

    with when, raises(Exception) as exception:
        await matcher.match(request_)

    with then:
        assert exception.type == NotImplementedError


@pytest.mark.asyncio
async def test_concrete_match_method_not_raises_error(resolver_: Mock, request_: Mock):
    with given:
        rec_ = Mock(return_value=True)

        class CustomResolvableMatcher(ResolvableMatcher):
            async def match(self, request):
                return rec_(request)

        matcher = CustomResolvableMatcher(resolver_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is True
        assert rec_.assert_called_once_with(request_) is None


@pytest.mark.asyncio
async def test_decorator_registers_matcher(resolver_: Mock, handler_: CoroutineMock):
    with given:
        matcher = ResolvableMatcher(resolver_)

    with when:
        actual = matcher(handler_)

    with then:
        assert actual == handler_
        assert (resolver_.register_matcher
                             .assert_called_once_with(matcher.match, handler_)) is None
        assert handler_.assert_not_called() is None
