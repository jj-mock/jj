from unittest.mock import Mock, call, sentinel

import pytest

from jj.logs import Filter

from .._test_utils.steps import given, then, when
from ._log_record import TestLogRecord


@pytest.fixture()
def record():
    return TestLogRecord(sentinel.message)


def test_filter_without_request_and_response(record: TestLogRecord):
    with given:
        filter = Filter()
        filter.filter_request = Mock(return_value=False)
        filter.filter_response = Mock(return_value=False)

    with when:
        res = filter.filter(record)

    with then:
        assert res is True
        assert filter.filter_request.mock_calls == []
        assert filter.filter_response.mock_calls == []


@pytest.mark.parametrize("value", [False, True])
def test_filter_with_request(value: bool, record: TestLogRecord):
    with given:
        filter = Filter()
        filter.filter_request = Mock(return_value=value)
        filter.filter_response = Mock(return_value=True)
        record.jj_request = sentinel.request

    with when:
        res = filter.filter(record)

    with then:
        assert res is value
        assert filter.filter_request.mock_calls == [
            call(sentinel.request, record)
        ]
        assert filter.filter_response.mock_calls == []


@pytest.mark.parametrize("value", [False, True])
def test_filter_with_response(value: bool, record: TestLogRecord):
    with given:
        filter = Filter()
        filter.filter_request = Mock(return_value=True)
        filter.filter_response = Mock(return_value=value)
        record.jj_request = sentinel.request
        record.jj_response = sentinel.response

    with when:
        res = filter.filter(record)

    with then:
        assert res is value
        assert filter.filter_request.mock_calls == []
        assert filter.filter_response.mock_calls == [
            call(sentinel.response, sentinel.request, record)
        ]


def test_request_filter(record: TestLogRecord):
    with given:
        filter = Filter()

    with when:
        res = filter.filter_request(sentinel.request, record)

    with then:
        assert res is True


def test_response_filter(record: TestLogRecord):
    with given:
        filter = Filter()

    with when:
        res = filter.filter_response(sentinel.response, sentinel.request, record)

    with then:
        assert res is True
