import pytest
from asynctest.mock import Mock

from jj.matchers import PathMatcher, RequestMatcher, AttributeMatcher

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
        matcher = PathMatcher(resolver_, expected)

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
        submatcher_ = Mock(AttributeMatcher, match=Mock(return_value=ret_val))
        matcher = PathMatcher(resolver_, submatcher_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is ret_val
        assert submatcher_.match.assert_called_once_with(path) is None


def test_is_instance_of_request_matcher(*, resolver_):
    with given:
        matcher = PathMatcher(resolver_, "/")

    with when:
        actual = isinstance(matcher, RequestMatcher)

    with then:
        assert actual is True
