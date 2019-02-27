import asynctest
from asynctest import CoroutineMock, Mock, sentinel, call

from jj.apps import create_app
from jj.resolvers import Registry, ReversedResolver


class TestReversedResolver(asynctest.TestCase):
    def setUp(self):
        self.default_handler = CoroutineMock(return_value=sentinel.default_response)
        self.default_app = create_app()
        self.resolver = ReversedResolver(Registry(), self.default_app, self.default_handler)

    def test_handler_getter_without_handlers(self):
        handlers = self.resolver.get_handlers(type(self.default_app))
        self.assertEqual(handlers, [])

    def test_handler_getter_with_one_handler(self):
        handler = CoroutineMock(return_value=sentinel.response)
        self.resolver.register_handler(handler, type(self.default_app))

        handlers = self.resolver.get_handlers(type(self.default_app))
        self.assertEqual(handlers, [handler])

    def test_handler_getter_with_multiple_handlers(self):
        handler1 = CoroutineMock(return_value=sentinel.response)
        handler2 = CoroutineMock(return_value=sentinel.response)
        self.resolver.register_handler(handler1, type(self.default_app))
        self.resolver.register_handler(handler2, type(self.default_app))

        handlers = self.resolver.get_handlers(type(self.default_app))
        self.assertEqual(handlers, [handler2, handler1])

    async def test_resolve_request_with_multiple_handlers(self):
        matcher = CoroutineMock(side_effect=(False, True))
        handler1 = CoroutineMock(return_value=sentinel.response1)
        handler2 = CoroutineMock(return_value=sentinel.response2)
        self.resolver.register_matcher(matcher, handler1)
        self.resolver.register_matcher(matcher, handler2)

        request = Mock()
        response = await self.resolver.resolve(request, self.default_app)
        self.assertEqual(response, handler2)

        handler1.assert_not_called()
        handler2.assert_not_called()
        matcher.assert_has_calls([call(request)] * 2)
        self.assertEqual(matcher.call_count, 2)

    async def test_resolve_request_priority(self):
        matcher = CoroutineMock(side_effect=(True, True))
        handler1 = CoroutineMock(return_value=sentinel.response1)
        handler2 = CoroutineMock(return_value=sentinel.response2)
        self.resolver.register_matcher(matcher, handler1)
        self.resolver.register_matcher(matcher, handler2)

        request = Mock()
        response = await self.resolver.resolve(request, self.default_app)
        self.assertEqual(response, handler1)

        handler1.assert_not_called()
        handler2.assert_not_called()
        matcher.assert_called_once_with(request)
