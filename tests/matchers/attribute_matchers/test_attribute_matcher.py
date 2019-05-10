import pytest
from asynctest.mock import sentinel
from pytest import raises

from jj.matchers import AttributeMatcher

from ..._test_utils.fixtures import request_, resolver_  # noqa: F401
from ..._test_utils.steps import given, then, when


@pytest.mark.asyncio
async def test_abstract_match_method_raises_exception():
    with given:
        matcher = AttributeMatcher()

    with when, raises(Exception) as exception:
        await matcher.match(sentinel.value)

    with then:
        assert exception.type is NotImplementedError
