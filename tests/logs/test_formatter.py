import logging
import unittest
from unittest.mock import Mock, sentinel

from jj.logs import Formatter

from ._log_record import TestLogRecord


class TestFormatter(unittest.TestCase):
    def setUp(self):
        self.formatter = Formatter()
        self.formatter.format_request = Mock(return_value=sentinel.formatted_request)
        self.formatter.format_response = Mock(return_value=sentinel.formatted_response)

    def test_inheritance(self):
        self.assertIsInstance(self.formatter, logging.Formatter)

    def test_format_without_request_and_response(self):
        record = TestLogRecord(sentinel.message)

        self.assertEqual(self.formatter.format(record), str(sentinel.message))

        self.formatter.format_request.assert_not_called()
        self.formatter.format_response.assert_not_called()

    def test_format_with_request(self):
        record = TestLogRecord(sentinel.message)
        record.jj_request = sentinel.request

        expected = self.formatter.format_request.return_value
        self.assertEqual(self.formatter.format(record), expected)

        self.formatter.format_request.assert_called_once_with(sentinel.request, record)
        self.formatter.format_response.assert_not_called()

    def test_format_with_response(self):
        record = TestLogRecord(sentinel.message)
        record.jj_request = sentinel.request
        record.jj_response = sentinel.response

        expected = self.formatter.format_response.return_value
        self.assertEqual(self.formatter.format(record), expected)

        self.formatter.format_response.assert_called_once_with(sentinel.response, sentinel.request, record)
        self.formatter.format_request.assert_not_called()

    def test_request_format(self):
        formatter = Formatter()
        record = TestLogRecord(sentinel.message)

        res = formatter.format_request(sentinel.request, record)
        self.assertEqual(res, str(sentinel.message))

    def test_response_format(self):
        formatter = Formatter()
        record = TestLogRecord(sentinel.message)

        res = formatter.format_response(sentinel.response, sentinel.request, record)
        self.assertEqual(res, str(sentinel.message))
