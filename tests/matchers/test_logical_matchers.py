import asynctest
from asynctest import CoroutineMock, Mock, call

from jj import Request
from jj.matchers import LogicalMatcher, AllMatcher, AnyMatcher


class TestLogicalMatchers(asynctest.TestCase):
    async def test_abstract_logical_matcher(self):
        resolver = Mock()
        submatcher = Mock(match=CoroutineMock())
        matcher = LogicalMatcher(resolver, matchers=[submatcher])

        request = Mock(Request)
        with self.assertRaises(NotImplementedError):
            await matcher.match(request)

    def test_logical_matcher_with_empty_submatchers(self):
        resolver = Mock()
        with self.assertRaises(AssertionError):
            LogicalMatcher(resolver, matchers=[])

    # AllMatcher

    async def test_all_matcher_with_single_truthy_submatcher(self):
        resolver = Mock()
        submatcher = Mock(match=CoroutineMock(return_value=True))
        matcher = AllMatcher(resolver, [submatcher])

        request = Mock(Request)
        self.assertTrue(await matcher.match(request))

        submatcher.match.assert_called_once_with(request)

    async def test_all_matcher_with_single_falsy_submatcher(self):
        resolver = Mock()
        submatcher = Mock(match=CoroutineMock(return_value=False))
        matcher = AllMatcher(resolver, [submatcher])

        request = Mock(Request)
        self.assertFalse(await matcher.match(request))

        submatcher.match.assert_called_once_with(request)

    async def test_all_matcher_with_multiple_truthy_submatchers(self):
        resolver = Mock()
        submatcher = Mock(match=CoroutineMock(side_effect=(True, True)))
        matcher = AllMatcher(resolver, [submatcher, submatcher])

        request = Mock(Request)
        self.assertTrue(await matcher.match(request))

        submatcher.match.assert_has_calls([call(request), call(request)])
        self.assertEqual(submatcher.match.call_count, 2)

    async def test_all_matcher_with_multiple_falsy_submatchers(self):
        resolver = Mock()
        submatcher = Mock(match=CoroutineMock(side_effect=(False, False)))
        matcher = AllMatcher(resolver, [submatcher, submatcher])

        request = Mock(Request)
        self.assertFalse(await matcher.match(request))

        submatcher.match.assert_called_once_with(request)

    async def test_all_matcher_with_multiple_submatchers(self):
        resolver = Mock()
        submatcher = Mock(match=CoroutineMock(side_effect=(True, False)))
        matcher = AllMatcher(resolver, [submatcher, submatcher])

        request = Mock(Request)
        self.assertFalse(await matcher.match(request))

        submatcher.match.assert_has_calls([call(request), call(request)])
        self.assertEqual(submatcher.match.call_count, 2)

    # AnyMatcher

    async def test_any_matcher_with_single_truthy_submatcher(self):
        resolver = Mock()
        submatcher = Mock(match=CoroutineMock(return_value=True))
        matcher = AnyMatcher(resolver, [submatcher])

        request = Mock(Request)
        self.assertTrue(await matcher.match(request))

        submatcher.match.assert_called_once_with(request)

    async def test_any_matcher_with_single_falsy_submatcher(self):
        resolver = Mock()
        submatcher = Mock(match=CoroutineMock(return_value=False))
        matcher = AnyMatcher(resolver, [submatcher])

        request = Mock(Request)
        self.assertFalse(await matcher.match(request))

        submatcher.match.assert_called_once_with(request)

    async def test_any_matcher_with_multiple_truthy_submatchers(self):
        resolver = Mock()
        submatcher = Mock(match=CoroutineMock(side_effect=(True, True)))
        matcher = AnyMatcher(resolver, [submatcher, submatcher])

        request = Mock(Request)
        self.assertTrue(await matcher.match(request))

        submatcher.match.assert_called_once_with(request)

    async def test_any_matcher_with_multiple_falsy_submatchers(self):
        resolver = Mock()
        submatcher = Mock(match=CoroutineMock(side_effect=(False, False)))
        matcher = AnyMatcher(resolver, [submatcher, submatcher])

        request = Mock(Request)
        self.assertFalse(await matcher.match(request))

        submatcher.match.assert_has_calls([call(request), call(request)])
        self.assertEqual(submatcher.match.call_count, 2)

    async def test_any_matcher_with_multiple_submatchers(self):
        resolver = Mock()
        submatcher = Mock(match=CoroutineMock(side_effect=(True, False)))
        matcher = AnyMatcher(resolver, [submatcher, submatcher])

        request = Mock(Request)
        self.assertTrue(await matcher.match(request))

        submatcher.match.assert_called_once_with(request)
