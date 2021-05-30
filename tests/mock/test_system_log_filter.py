from unittest.mock import Mock, sentinel

import pytest

from jj.mock import SystemLogFilter

from .._test_utils.steps import given, then, when
from ..logs._log_record import TestLogRecord


@pytest.fixture()
def record():
    return TestLogRecord(sentinel.message)


def test_log_filter(record: TestLogRecord):
    with given:
        log_filter = SystemLogFilter()

    with when:
        res = log_filter.filter(record)

    with then:
        assert res is True


def test_log_filter_request_without_header(record: TestLogRecord):
    with given:
        log_filter = SystemLogFilter()
        record.jj_request = Mock(headers={})

    with when:
        res = log_filter.filter(record)

    with then:
        assert res is True


def test_log_filter_request_with_header(record: TestLogRecord):
    with given:
        log_filter = SystemLogFilter()
        record.jj_request = Mock(headers={"x-jj-remote-mock": ""})

    with when:
        res = log_filter.filter(record)

    with then:
        assert res is False


def test_log_filter_response_without_header(record: TestLogRecord):
    with given:
        log_filter = SystemLogFilter()
        record.jj_request = Mock(headers={})
        record.jj_response = Mock()

    with when:
        res = log_filter.filter(record)

    with then:
        assert res is True


def test_log_filter_response_with_header(record: TestLogRecord):
    with given:
        log_filter = SystemLogFilter()
        record.jj_request = Mock(headers={"x-jj-remote-mock": ""})
        record.jj_response = Mock()

    with when:
        res = log_filter.filter(record)

    with then:
        assert res is False
