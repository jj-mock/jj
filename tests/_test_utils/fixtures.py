import sys

if sys.version_info >= (3, 8):
    from unittest.mock import AsyncMock
else:
    from asynctest.mock import CoroutineMock as AsyncMock

from unittest.mock import Mock, sentinel

import pytest

from jj.requests import Request
from jj.resolvers import Resolver


@pytest.fixture
def resolver_():
    return Mock(Resolver)


@pytest.fixture
def request_():
    return Mock(Request)


@pytest.fixture
def handler_():
    return AsyncMock(return_value=sentinel.response)
