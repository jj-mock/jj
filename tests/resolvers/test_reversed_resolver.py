from unittest import IsolatedAsyncioTestCase as TestCase
from unittest.mock import AsyncMock, Mock, call, sentinel

import pytest

from jj.apps import create_app
from jj.resolvers import Registry, ReversedResolver


class TestReversedResolver(TestCase):
    def setUp(self):
        self.default_handler = AsyncMock(return_value=sentinel.default_response)
        self.default_app = create_app()
        self.resolver = ReversedResolver(Registry(), self.default_app, self.default_handler)

    def test_handler_getter_without_handlers(self):
        handlers = self.resolver.get_handlers(type(self.default_app))
        self.assertEqual(handlers, [])

    def test_handler_getter_with_one_handler(self):
        handler = AsyncMock(return_value=sentinel.response)
        self.resolver.register_handler(handler, type(self.default_app))

        handlers = self.resolver.get_handlers(type(self.default_app))
        self.assertEqual(handlers, [handler])

    def test_handler_getter_with_multiple_handlers(self):
        handler1 = AsyncMock(return_value=sentinel.response)
        handler2 = AsyncMock(return_value=sentinel.response)
        self.resolver.register_handler(handler1, type(self.default_app))
        self.resolver.register_handler(handler2, type(self.default_app))

        handlers = self.resolver.get_handlers(type(self.default_app))
        self.assertEqual(handlers, [handler2, handler1])

    @pytest.mark.asyncio
    async def test_resolve_request_with_multiple_handlers(self):
        matcher = AsyncMock(side_effect=(False, True))
        handler1 = AsyncMock(return_value=sentinel.response1)
        handler2 = AsyncMock(return_value=sentinel.response2)
        self.resolver.register_matcher(matcher, handler1)
        self.resolver.register_matcher(matcher, handler2)

        request = Mock()
        response = await self.resolver.resolve(request, self.default_app)
        self.assertEqual(response, handler2)

        handler1.assert_not_called()
        handler2.assert_not_called()
        matcher.assert_has_calls([call(request)] * 2, any_order=True)
        self.assertEqual(matcher.call_count, 2)

    @pytest.mark.asyncio
    async def test_resolve_request_priority(self):
        matcher = AsyncMock(side_effect=(True, True))
        handler1 = AsyncMock(return_value=sentinel.response1)
        handler2 = AsyncMock(return_value=sentinel.response2)
        self.resolver.register_matcher(matcher, handler1)
        self.resolver.register_matcher(matcher, handler2)

        request = Mock()
        response = await self.resolver.resolve(request, self.default_app)
        self.assertEqual(response, handler1)

        handler1.assert_not_called()
        handler2.assert_not_called()
        matcher.assert_called_once_with(request)
