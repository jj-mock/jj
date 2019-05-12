import pytest
from asynctest.mock import CoroutineMock as CoroMock
from asynctest.mock import Mock, call
from multidict import MultiDict

from jj.matchers import AttributeMatcher, ParamMatcher, RequestMatcher

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
    ({"a": "b"}, {"A": "b"}, False),
    ({"A": "b"}, {"a": "b"}, False),
    ({"a": "b"}, {"a": "B"}, False),
    ({"a": "B"}, {"a": "b"}, False),
])
async def test_param_matcher(expected, actual, res, *, resolver_, request_):
    with given:
        request_.query = MultiDict(actual)
        matcher = ParamMatcher(expected, resolver=resolver_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is res


@pytest.mark.asyncio
@pytest.mark.parametrize(("ret_val", "params"), [
    (True, {}),
    (False, {"key": "val"}),
    (True, [("key", "1"), ("key", "2")]),
    (False, [("key1", "1"), ("key2", "2")]),
])
async def test_param_matcher_with_custom_submatcher(ret_val, params, *, resolver_, request_):
    with given:
        request_.query = MultiDict(params)
        submatcher_ = Mock(AttributeMatcher, match=CoroMock(return_value=ret_val))
        matcher = ParamMatcher(submatcher_, resolver=resolver_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is ret_val
        assert submatcher_.mock_calls == [call.match(request_.query)]


@pytest.mark.asyncio
async def test_param_matcher_with_value_submatchers_superset(request_):
    with given:
        request_.query = MultiDict([
            ("key1", "1.1"),
            ("key1", "1.2"),
        ])
        submatcher1_ = Mock(AttributeMatcher, match=CoroMock(return_value=True))
        submatcher2_ = Mock(AttributeMatcher)
        matcher = ParamMatcher(resolver=resolver_, params={
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
async def test_param_matcher_with_value_submatchers_subset(request_):
    with given:
        request_.query = MultiDict([
            ("key1", "1"),
            ("key2", "2.1"),
            ("key2", "2.2"),
            ("key3", "3"),
        ])
        submatcher1_ = Mock(AttributeMatcher, match=CoroMock(side_effect=(True,)))
        submatcher2_ = Mock(AttributeMatcher, match=CoroMock(side_effect=(False, True)))
        matcher = ParamMatcher(resolver=resolver_, params={
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
        matcher = ParamMatcher({}, resolver=resolver_)

    with when:
        actual = isinstance(matcher, RequestMatcher)

    with then:
        assert actual is True


@pytest.mark.parametrize(("params", "representation"), [
    ({}, "[]"),
    ({"KEY": "Val"}, "[('KEY', 'Val')]"),
    ({"key1": "1", "key2": "2"}, "[('key1', '1'), ('key2', '2')]"),
])
def test_repr(params, representation, *, resolver_):
    with given:
        resolver_.__repr__ = Mock(return_value="<Resolver>")
        matcher = ParamMatcher(params, resolver=resolver_)

    with when:
        actual = repr(matcher)

    with then:
        assert actual == f"ParamMatcher(MultiDictMatcher({representation}), resolver=<Resolver>)"
