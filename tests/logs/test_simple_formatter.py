import unittest
import logging
from unittest.mock import Mock, sentinel

from jj.logs import SimpleFormatter

from ._log_record import TestLogRecord


class TestSimpleFormatter(unittest.TestCase):
    def setUp(self):
        self.formatter = SimpleFormatter()

    def test_inheritance(self):
        self.assertIsInstance(self.formatter, logging.Formatter)

    def test_format_without_request_and_response(self):
        record = TestLogRecord(sentinel.message)
        self.assertEqual(self.formatter.format(record), str(sentinel.message))

    def test_format_with_request(self):
        record = TestLogRecord(sentinel.message)
        record.jj_request = Mock(url=Mock(path=sentinel.path))

        expected = "-> {}".format(sentinel.path)
        self.assertEqual(self.formatter.format(record), expected)

    def test_format_with_response(self):
        record = TestLogRecord(sentinel.message)
        record.jj_request = Mock()
        record.jj_response = Mock(status=sentinel.status, reason=sentinel.reason)

        expected = "<- {} {}\n".format(sentinel.status, sentinel.reason)
        self.assertEqual(self.formatter.format(record), expected)
