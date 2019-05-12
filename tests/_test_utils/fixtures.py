import pytest
from asynctest.mock import CoroutineMock, Mock, sentinel

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
    return CoroutineMock(return_value=sentinel.response)
