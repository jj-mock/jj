import pytest
from asynctest.mock import Mock
from multidict import CIMultiDict

from jj.matchers import HeaderMatcher, RequestMatcher, AttributeMatcher

from ..._test_utils.fixtures import request_, resolver_  # noqa: F401
from ..._test_utils.steps import given, then, when


@pytest.mark.asyncio
@pytest.mark.parametrize(("expected", "actual", "res"), [
    ({}, {}, True),
    ([], {}, True),
    ({}, {"key": "1"}, True),
    ([], {"key": "1"}, True),

    ({"key": "1"}, {}, False),
    ({"key": "1"}, {"key": "1"}, True),
    ({"key1": "1"}, {"key1": "1", "key2": "2"}, True),
    ({"key1": "1", "key2": "2"}, {"key1": "1"}, False),
    ({"key1": "1", "key2": "2"}, {"key1": "1", "key2": "2"}, True),

    ([("key", "1"), ("key", "2")], [], False),
    ([("key", "1"), ("key", "2")], [("key", "1")], False),
    ([("key", "1"), ("key", "2")], [("key", "2")], False),
    ([("key", "1"), ("key", "2")], [("key", "1"), ("key", "2")], True),
    ([("key", "1"), ("key", "2")], [("key", "1"), ("key", "3")], False),

    ({"key": "1"}, [("key", "1")], True),
    ({"key": "1"}, [("key", "1"), ("key", "2")], True),
    ({"key": "1"}, [("key", "3"), ("key", "2")], False),

    ({"q": "g"}, {"q": "g"}, True),
    ({"q": "g"}, {"Q": "g"}, True),
    ({"q": "g"}, {"q": "G"}, False),
])
async def test_header_matcher(expected, actual, res, *, resolver_, request_):
    with given:
        request_.headers = CIMultiDict(actual)
        matcher = HeaderMatcher(resolver_, expected)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is res


@pytest.mark.asyncio
@pytest.mark.parametrize(("ret_val", "headers"), [
    (True, {}),
    (False, {"key": "val"}),
    (True, [("key", "1"), ("key", "2")]),
    (False, [("key1", "1"), ("key2", "2")]),
])
async def test_header_matcher_with_custom_submatcher(ret_val, headers, *, resolver_, request_):
    with given:
        request_.headers = CIMultiDict(headers)
        submatcher_ = Mock(AttributeMatcher, match=Mock(return_value=ret_val))
        matcher = HeaderMatcher(resolver_, submatcher_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is ret_val
        assert submatcher_.match.assert_called_once_with(request_.headers) is None


@pytest.mark.asyncio
async def test_header_matcher_with_custom_value_submatcher():
    pass


def test_is_instance_of_request_matcher(*, resolver_):
    with given:
        matcher = HeaderMatcher(resolver_, {})

    with when:
        actual = isinstance(matcher, RequestMatcher)

    with then:
        assert actual is True
