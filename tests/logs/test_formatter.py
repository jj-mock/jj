from unittest.mock import Mock, call, sentinel

import pytest

from jj.logs import Formatter

from .._test_utils.steps import given, then, when
from ._log_record import TestLogRecord


class _Formatter(Formatter):
    format_request: Mock
    format_response: Mock


@pytest.fixture()
def formatter():
    formatter = Formatter()
    formatter.format_request = Mock(return_value=sentinel.formatted_request)
    formatter.format_response = Mock(return_value=sentinel.formatted_response)
    return formatter


@pytest.fixture()
def record():
    return TestLogRecord(sentinel.message)


def test_format_without_request_and_response(formatter: _Formatter, record: TestLogRecord):
    with when:
        res = formatter.format(record)

    with then:
        assert res == str(record.msg)
        assert formatter.format_request.mock_calls == []
        assert formatter.format_response.mock_calls == []


def test_format_with_request(formatter: _Formatter, record: TestLogRecord):
    with given:
        record.jj_request = sentinel.request

    with when:
        res = formatter.format(record)

    with then:
        assert res == formatter.format_request.return_value
        assert formatter.format_request.mock_calls == [
            call(sentinel.request, record)
        ]
        assert formatter.format_response.mock_calls == []


def test_format_with_response(formatter: _Formatter, record: TestLogRecord):
    with given:
        record.jj_request = sentinel.request
        record.jj_response = sentinel.response

    with when:
        res = formatter.format(record)

    with then:
        assert res == formatter.format_response.return_value
        assert formatter.format_request.mock_calls == []
        assert formatter.format_response.mock_calls == [
            call(sentinel.response, sentinel.request, record)
        ]


def test_request_format(record: TestLogRecord):
    with given:
        formatter = Formatter()

    with when:
        res = formatter.format_request(sentinel.request, record)

    with then:
        assert res == str(record.msg)


def test_response_format(record: TestLogRecord):
    with given:
        formatter = Formatter()

    with when:
        res = formatter.format_response(sentinel.response, sentinel.request, record)

    with then:
        assert res == str(record.msg)
