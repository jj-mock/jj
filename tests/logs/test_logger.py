import unittest
import logging

from jj.logs import Logger


class TestLogger(unittest.TestCase):
    def setUp(self):
        self.logger = Logger(__name__)

    def test_inheritance(self):
        self.assertIsInstance(self.logger, logging.Logger)

    def test_no_default_handlers(self):
        self.assertEqual(len(self.logger.handlers), 0)

    def test_add_handler(self):
        handler = logging.NullHandler()
        self.logger.addHandler(handler)
        self.assertEqual(len(self.logger.handlers), 1)

    def test_clear_handlers(self):
        handler = logging.NullHandler()
        self.logger.addHandler(handler)

        res = self.logger.clearHandlers()

        self.assertIsInstance(res, type(self.logger))
        self.assertEqual(res, self.logger)
        self.assertEqual(len(self.logger.handlers), 0)
