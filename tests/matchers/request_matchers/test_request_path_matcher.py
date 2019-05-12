import pytest
from asynctest.mock import CoroutineMock as CoroMock
from asynctest.mock import Mock, call

from jj.matchers import AttributeMatcher, PathMatcher, RequestMatcher

from ..._test_utils.fixtures import request_, resolver_  # noqa: F401
from ..._test_utils.steps import given, then, when


@pytest.mark.asyncio
@pytest.mark.parametrize(("expected", "actual", "res"), [
    ("/", "/", True),
    ("/", "/smth", False),
    ("/smth", "/", False),

    ("/users/{id}", "/users/1", True),
    ("/users/{id}", "/users", False),
    ("/users/{id}", "/users/", False),
    ("/users/{id}", "/users/1/profile", False),

    ("/{tail:.*}", "/", True),
    ("/{tail:.*}", "/users", True),
    ("/{tail:.*}", "/users/1/profile", True),
])
async def test_path_matcher(expected, actual, res, *, resolver_, request_):
    with given:
        request_.path = actual
        matcher = PathMatcher(expected, resolver=resolver_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is res


@pytest.mark.asyncio
@pytest.mark.parametrize(("ret_val", "path"), [
    (True, "/"),
    (True, "/smth"),
    (False, "/"),
])
async def test_path_matcher_with_custom_submatcher(ret_val, path, *, resolver_, request_):
    with given:
        request_.path = path
        submatcher_ = Mock(AttributeMatcher, match=CoroMock(return_value=ret_val))
        matcher = PathMatcher(submatcher_, resolver=resolver_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is ret_val
        assert submatcher_.mock_calls == [call.match(path)]


def test_is_instance_of_request_matcher(*, resolver_):
    with given:
        matcher = PathMatcher("/", resolver=resolver_)

    with when:
        actual = isinstance(matcher, RequestMatcher)

    with then:
        assert actual is True


@pytest.mark.parametrize("path", ["/", "/users", "/users/{id}"])
def test_repr(path, *, resolver_):
    with given:
        resolver_.__repr__ = Mock(return_value="<Resolver>")
        matcher = PathMatcher(path, resolver=resolver_)

    with when:
        actual = repr(matcher)

    with then:
        assert actual == f"PathMatcher(RouteMatcher({path!r}), resolver=<Resolver>)"
