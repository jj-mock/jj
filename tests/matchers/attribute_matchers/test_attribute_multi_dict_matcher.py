import sys

if sys.version_info >= (3, 8):
    from unittest.mock import AsyncMock
else:
    from asynctest.mock import CoroutineMock as AsyncMock

from unittest.mock import Mock, call, sentinel

import pytest
from multidict import MultiDict

from jj.matchers import AttributeMatcher
from jj.matchers.attribute_matchers import MultiDictMatcher

from ..._test_utils.steps import given, then, when


@pytest.mark.asyncio
@pytest.mark.parametrize(("expected", "actual", "res"), [
    ({}, {}, True),
    ({}, {"key1": "1"}, True),
    ({"key1": "1"}, {}, False),
    ({"key1": "1"}, {"key1": "1"}, True),

    ({"key1": "1"}, {"key1": "1", "key2": "2"}, True),
    ({"key1": "1", "key2": "2"}, {"key1": "1"}, False),

    ({"key1": "1.1"}, [("key1", "1.1"), ("key1", "1.2")], True),
    ({"key1": "1.2"}, [("key1", "1.1"), ("key1", "1.2")], True),
    ([("key1", "1.1"), ("key1", "1.2")], [("key1", "1.1"), ("key1", "1.2")], True),
])
async def test_multi_dict_matcher(expected, actual, res):
    with given:
        matcher = MultiDictMatcher(expected)

    with when:
        actual = await matcher.match(MultiDict(actual))

    with then:
        assert actual is res


@pytest.mark.asyncio
async def test_multi_dict_matcher_with_value_submatchers_superset():
    with given:
        submatcher1_ = Mock(AttributeMatcher, match=AsyncMock(return_value=True))
        submatcher2_ = Mock(AttributeMatcher)
        matcher = MultiDictMatcher({
            "key1": submatcher1_,
            "key2": submatcher2_,
        })

    with when:
        actual = await matcher.match(MultiDict([
            ("key1", "1.1"),
            ("key1", "1.2"),
        ]))

    with then:
        assert actual is False
        assert submatcher1_.mock_calls == [call.match("1.1")]
        assert submatcher2_.mock_calls == []


@pytest.mark.asyncio
async def test_multi_dict_matcher_with_value_submatchers_subset():
    with given:
        submatcher1_ = Mock(AttributeMatcher, match=AsyncMock(side_effect=(True,)))
        submatcher2_ = Mock(AttributeMatcher, match=AsyncMock(side_effect=(False, True)))
        matcher = MultiDictMatcher({
            "key1": submatcher1_,
            "key2": submatcher2_,
        })

    with when:
        actual = await matcher.match(MultiDict([
            ("key1", "1"),
            ("key2", "2.1"),
            ("key2", "2.2"),
            ("key3", "3"),
        ]))

    with then:
        assert actual is True
        assert submatcher1_.mock_calls == [call.match("1")]
        assert submatcher2_.mock_calls == [call.match("2.1"), call.match("2.2")]


def test_is_instance_of_attribute_matcher():
    with given:
        matcher = MultiDictMatcher({})

    with when:
        actual = isinstance(matcher, AttributeMatcher)

    with then:
        assert actual is True


@pytest.mark.parametrize(("expected", "representation"), [
    ({}, "MultiDictMatcher([])"),
    ({"key": "val"}, "MultiDictMatcher([('key', 'val')])"),
    ({"key1": "1", "key2": "2"}, "MultiDictMatcher([('key1', '1'), ('key2', '2')])"),
])
def test_repr(expected, representation):
    with given:
        matcher = MultiDictMatcher(expected)

    with when:
        actual = repr(matcher)

    with then:
        assert actual == representation


def test_pack():
    with given:
        expected = [["key", "1"], ["key", "2"]]
        matcher = MultiDictMatcher(expected)

    with when:
        actual = matcher.__packed__()

    with then:
        assert actual == {"expected": expected}


def test_unpack():
    with given:
        kwargs = {
            "expected": [("key", "1"), ("key", "2")],
            "future_field": sentinel,
        }

    with when:
        actual = MultiDictMatcher.__unpacked__(**kwargs)

    with then:
        assert isinstance(actual, MultiDictMatcher)
