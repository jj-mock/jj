import pytest
from asynctest.mock import CoroutineMock as CoroMock
from asynctest.mock import Mock, call

from jj.matchers import AttributeMatcher, MethodMatcher, RequestMatcher

from ..._test_utils.fixtures import request_, resolver_  # noqa: F401
from ..._test_utils.steps import given, then, when


@pytest.mark.asyncio
@pytest.mark.parametrize(("expected", "actual", "res"), [
    ("*", "GET", True),
    ("*", "POST", True),
    ("*", "CUSTOM", True),

    ("GET", "GET", True),
    ("get", "GET", True),
    ("POST", "POST", True),
    ("GET", "POST", False),
])
async def test_method_matcher(expected, actual, res, *, resolver_, request_):
    with given:
        request_.method = actual
        matcher = MethodMatcher(expected, resolver=resolver_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is res


@pytest.mark.asyncio
@pytest.mark.parametrize(("ret_vals", "res", "called_with"), [
    ([True, True], True, ["*"]),
    ([True, False], True, ["*"]),
    ([False, True], True, ["*", "GET"]),
    ([False, False], False, ["*", "GET"]),
])
async def test_method_matcher_with_custom_submatcher(ret_vals, res, called_with, *,
                                                     resolver_, request_):
    with given:
        request_.method = "GET"
        submatcher_ = Mock(AttributeMatcher, match=CoroMock(side_effect=ret_vals))
        matcher = MethodMatcher(submatcher_, resolver=resolver_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is res
        assert submatcher_.mock_calls == [call.match(x) for x in called_with]


def test_is_instance_of_request_matcher(*, resolver_):
    with given:
        matcher = MethodMatcher("*", resolver=resolver_)

    with when:
        actual = isinstance(matcher, RequestMatcher)

    with then:
        assert actual is True


@pytest.mark.parametrize(("method", "representation"), [
    ("*", "*"),
    ("GET", "GET"),
    ("post", "POST"),
])
def test_repr(method, representation, *, resolver_):
    with given:
        resolver_.__repr__ = Mock(return_value="<Resolver>")
        matcher = MethodMatcher(method, resolver=resolver_)

    with when:
        actual = repr(matcher)

    with then:
        assert actual == f"MethodMatcher(EqualMatcher({representation!r}), resolver=<Resolver>)"
