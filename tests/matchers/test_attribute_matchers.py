import unittest
from unittest.mock import sentinel

from jj.matchers import (AttributeMatcher, EqualMatcher, NotEqualMatcher,
                         ContainMatcher, NotContainMatcher, equals, contains)


class TestAttributeMatchers(unittest.TestCase):
    def test_abstract_attribute_matcher(self):
        matcher = AttributeMatcher()
        with self.assertRaises(NotImplementedError):
            matcher.match(sentinel)

    def test_equal_matcher(self):
        matcher = EqualMatcher(sentinel.expected)
        self.assertTrue(matcher.match(sentinel.expected))

        self.assertFalse(matcher.match(sentinel.actual))

    def test_partial_equal_matcher(self):
        self.assertIsInstance(equals(sentinel), EqualMatcher)

    def test_not_equal_matcher(self):
        matcher = NotEqualMatcher(sentinel.expected)
        self.assertFalse(matcher.match(sentinel.expected))

        self.assertTrue(matcher.match(sentinel.actual))

    def test_contain_matcher(self):
        matcher = ContainMatcher(sentinel.expected)
        self.assertTrue(matcher.match([sentinel.expected, sentinel.actual]))

        self.assertFalse(matcher.match([sentinel.actual]))

    def test_partial_contain_matcher(self):
        self.assertIsInstance(contains(sentinel), ContainMatcher)

    def test_not_contain_matcher(self):
        matcher = NotContainMatcher(sentinel.expected)
        self.assertFalse(matcher.match([sentinel.expected, sentinel.actual]))

        self.assertTrue(matcher.match([sentinel.actual]))
