from unittest.mock import AsyncMock, Mock, sentinel

import pytest

from jj.matchers import FormDataMatcher, RequestMatcher

from ..._test_utils.fixtures import request_, resolver_
from ..._test_utils.steps import given, then, when

__all__ = ("request_", "resolver_",)


@pytest.mark.asyncio
@pytest.mark.parametrize(("body", "res"), [
    ("refresh_token=abc", True),
    ("refresh_token=abc&grant_type=refresh_token", True),
    ("grant_type=refresh_token", False),
    ("refresh_token=xyz", False),
    ("", False),
])
async def test_form_data_matcher(body, res, *, resolver_, request_):
    with given:
        request_.text = AsyncMock(return_value=body)
        matcher = FormDataMatcher("refresh_token", "abc", resolver=resolver_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is res


@pytest.mark.asyncio
async def test_form_data_matcher_when_body_read_fails(*, resolver_, request_):
    with given:
        request_.text = AsyncMock(side_effect=ValueError("broken body"))
        matcher = FormDataMatcher("key", "value", resolver=resolver_)

    with when:
        actual = await matcher.match(request_)

    with then:
        assert actual is False


def test_is_instance_of_request_matcher(*, resolver_):
    with given:
        matcher = FormDataMatcher("key", "value", resolver=resolver_)

    with when:
        actual = isinstance(matcher, RequestMatcher)

    with then:
        assert actual is True


def test_repr(*, resolver_):
    with given:
        resolver_.__repr__ = Mock(return_value="<Resolver>")
        matcher = FormDataMatcher("key", "value", resolver=resolver_)

    with when:
        actual = repr(matcher)

    with then:
        assert actual == "FormDataMatcher(key='key', value='value', resolver=<Resolver>)"


def test_pack(*, resolver_):
    with given:
        matcher = FormDataMatcher("key", "value", resolver=resolver_)

    with when:
        actual = matcher.__packed__()

    with then:
        assert actual == {"key": "key", "value": "value"}


def test_unpack(*, resolver_):
    with given:
        kwargs = {
            "key": "key",
            "value": "value",
            "resolver": resolver_,
            "future_field": sentinel,
        }

    with when:
        actual = FormDataMatcher.__unpacked__(**kwargs)

    with then:
        assert isinstance(actual, FormDataMatcher)
