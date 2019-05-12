import pytest
from asynctest.mock import CoroutineMock as CoroMock
from asynctest.mock import Mock, call
from multidict import CIMultiDict

from jj.matchers import AttributeMatcher, HeaderMatcher, RequestMatcher

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

    ({"a": "b"}, {"a": "b"}, True),
    ({"a": "b"}, {"A": "b"}, True),
    ({"A": "b"}, {"a": "b"}, True),
    ({"a": "b"}, {"a": "B"}, False),
    ({"a": "B"}, {"a": "b"}, False),
])
async def test_header_matcher(expected, actual, res, *, resolver_, request_):
    with given:
        request_.headers = CIMultiDict(actual)
        matcher = HeaderMatcher(expected, resolver=resolver_)

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
        submatcher_ = Mock(AttributeMatcher, match=CoroMock(return_value=ret_val))
        matcher = HeaderMatcher(submatcher_, resolver=resolver_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is ret_val
        assert submatcher_.mock_calls == [call.match(request_.headers)]


@pytest.mark.asyncio
async def test_header_matcher_with_value_submatchers_superset(request_):
    with given:
        request_.headers = CIMultiDict([
            ("key1", "1.1"),
            ("key1", "1.2"),
        ])
        submatcher1_ = Mock(AttributeMatcher, match=CoroMock(return_value=True))
        submatcher2_ = Mock(AttributeMatcher)
        matcher = HeaderMatcher(resolver=resolver_, headers={
            "key1": submatcher1_,
            "key2": submatcher2_,
        })

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is False
        assert submatcher1_.mock_calls == [call.match("1.1")]
        assert submatcher2_.mock_calls == []


@pytest.mark.asyncio
async def test_header_matcher_with_value_submatchers_subset(request_):
    with given:
        request_.headers = CIMultiDict([
            ("key1", "1"),
            ("key2", "2.1"),
            ("key2", "2.2"),
            ("key3", "3"),
        ])
        submatcher1_ = Mock(AttributeMatcher, match=CoroMock(side_effect=(True,)))
        submatcher2_ = Mock(AttributeMatcher, match=CoroMock(side_effect=(False, True)))
        matcher = HeaderMatcher(resolver=resolver_, headers={
            "key1": submatcher1_,
            "key2": submatcher2_,
        })

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is True
        assert submatcher1_.mock_calls == [call.match("1")]
        assert submatcher2_.mock_calls == [call.match("2.1"), call.match("2.2")]


def test_is_instance_of_request_matcher(*, resolver_):
    with given:
        matcher = HeaderMatcher({}, resolver=resolver_)

    with when:
        actual = isinstance(matcher, RequestMatcher)

    with then:
        assert actual is True


@pytest.mark.parametrize(("headers", "representation"), [
    ({}, "[]"),
    ({"KEY": "Val"}, "[('KEY', 'Val')]"),
    ({"key1": "1", "key2": "2"}, "[('key1', '1'), ('key2', '2')]"),
])
def test_repr(headers, representation, *, resolver_):
    with given:
        resolver_.__repr__ = Mock(return_value="<Resolver>")
        matcher = HeaderMatcher(headers, resolver=resolver_)

    with when:
        actual = repr(matcher)

    with then:
        assert actual == f"HeaderMatcher(MultiDictMatcher({representation}), resolver=<Resolver>)"
