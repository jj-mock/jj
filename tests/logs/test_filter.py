import logging
import unittest
from unittest.mock import sentinel

from jj.logs import Filter


class TestFilter(unittest.TestCase):
    def setUp(self):
        self.filter = Filter()

    def test_inheritance(self):
        self.assertIsInstance(self.filter, logging.Filter)

    def test_filter(self):
        self.assertTrue(self.filter.filter(sentinel.any))
