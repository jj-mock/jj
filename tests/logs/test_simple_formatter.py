from unittest.mock import Mock, sentinel

import pytest

from jj.logs import SimpleFormatter

from .._test_utils.steps import given, then, when
from ._log_record import TestLogRecord


@pytest.fixture()
def formatter():
    return SimpleFormatter()


@pytest.fixture()
def record():
    return TestLogRecord(sentinel.message)


def test_format_without_request_and_response(formatter: SimpleFormatter, record: TestLogRecord):
    with when:
        res = formatter.format(record)

    with then:
        assert res == str(sentinel.message)


def test_format_with_request(formatter: SimpleFormatter, record: TestLogRecord):
    with given:
        record.jj_request = Mock(url=Mock(path=sentinel.path))

    with when:
        res = formatter.format(record)

    with then:
        assert res == "-> {}".format(sentinel.path)


def test_format_with_response(formatter: SimpleFormatter, record: TestLogRecord):
    with given:
        record.jj_request = Mock()
        record.jj_response = Mock(status=sentinel.status, reason=sentinel.reason)

    with when:
        res = formatter.format(record)

    with then:
        assert res == "<- {} {}\n".format(sentinel.status, sentinel.reason)
