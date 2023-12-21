from unittest.mock import AsyncMock, Mock, sentinel

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
