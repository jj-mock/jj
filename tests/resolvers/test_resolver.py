import asynctest
from asynctest import CoroutineMock, Mock, sentinel, call

from jj.apps import create_app
from jj.resolvers import Registry, Resolver


class TestResolver(asynctest.TestCase):
    def setUp(self):
        self.default_handler = CoroutineMock(return_value=sentinel.default_response)
        self.default_app = create_app()
        self.resolver = Resolver(Registry(), self.default_app, self.default_handler)

    # Apps

    def test_get_apps(self):
        apps = self.resolver.get_apps()
        self.assertEqual(apps, [])

    def test_register_app(self):
        res = self.resolver.register_app(type(self.default_app))
        self.assertIsNone(res)

        apps = self.resolver.get_apps()
        self.assertEqual(apps, [type(self.default_app)])

    def test_register_another_app(self):
        self.resolver.register_app(type(self.default_app))

        app = create_app()
        self.resolver.register_app(type(app))

        apps = self.resolver.get_apps()
        self.assertEqual(apps, [type(self.default_app), type(app)])

    def test_register_app_twice(self):
        self.resolver.register_app(type(self.default_app))

        res = self.resolver.register_app(type(self.default_app))
        self.assertIsNone(res)

        apps = self.resolver.get_apps()
        self.assertEqual(apps, [type(self.default_app)])

    def test_deregister_single_app(self):
        self.resolver.register_app(type(self.default_app))

        res = self.resolver.deregister_app(type(self.default_app))
        self.assertIsNone(res)

        apps = self.resolver.get_apps()
        self.assertEqual(apps, [])

    def test_deregister_app(self):
        app1, app2 = create_app(), create_app()
        self.resolver.register_app(type(app1))
        self.resolver.register_app(type(app2))

        self.resolver.deregister_app(type(app1))

        apps = self.resolver.get_apps()
        self.assertEqual(apps, [type(app2)])

    def test_deregister_nonexisting_app(self):
        app = create_app()

        res = self.resolver.deregister_app(type(app))
        self.assertIsNone(res)

    # Handlers

    def test_get_handlers(self):
        handlers = self.resolver.get_handlers(type(self.default_app))
        self.assertEqual(handlers, [])

    def test_get_handlers_with_nonexisting_app(self):
        app = create_app()

        handlers = self.resolver.get_handlers(type(app))
        self.assertEqual(handlers, [])

    def test_register_handler(self):
        handler = CoroutineMock(return_value=sentinel.response)
        res = self.resolver.register_handler(handler, type(self.default_app))
        self.assertIsNone(res)

        handlers = self.resolver.get_handlers(type(self.default_app))
        self.assertEqual(handlers, [handler])

    def test_register_another_handler(self):
        handler1 = CoroutineMock(return_value=sentinel.response)
        handler2 = CoroutineMock(return_value=sentinel.response)
        self.resolver.register_handler(handler1, type(self.default_app))

        self.resolver.register_handler(handler2, type(self.default_app))

        handlers = self.resolver.get_handlers(type(self.default_app))
        self.assertEqual(handlers, [handler1, handler2])

    def test_register_handler_twice(self):
        handler = CoroutineMock(return_value=sentinel.response)
        self.resolver.register_handler(handler, type(self.default_app))

        res = self.resolver.register_handler(handler, type(self.default_app))
        self.assertIsNone(res)

        handlers = self.resolver.get_handlers(type(self.default_app))
        self.assertEqual(handlers, [handler])

    def test_deregister_single_handler(self):
        handler = CoroutineMock(return_value=sentinel.response)
        self.resolver.register_handler(handler, type(self.default_app))

        res = self.resolver.deregister_handler(handler, type(self.default_app))
        self.assertIsNone(res)

        handlers = self.resolver.get_handlers(type(self.default_app))
        self.assertEqual(handlers, [])

    def test_deregister_handler(self):
        handler1 = CoroutineMock(return_value=sentinel.response)
        self.resolver.register_handler(handler1, type(self.default_app))
        handler2 = CoroutineMock(return_value=sentinel.response)
        self.resolver.register_handler(handler2, type(self.default_app))

        self.resolver.deregister_handler(handler1, type(self.default_app))

        handlers = self.resolver.get_handlers(type(self.default_app))
        self.assertEqual(handlers, [handler2])

    def test_deregister_nonexisting_handler(self):
        handler = CoroutineMock(return_value=sentinel.response)

        res = self.resolver.deregister_handler(handler, type(self.default_app))
        self.assertIsNone(res)

    def test_deregister_handler_with_nonexisting_app(self):
        handler = CoroutineMock(return_value=sentinel.response)
        self.resolver.register_handler(handler, type(self.default_app))

        app = create_app()
        res = self.resolver.deregister_handler(handler, type(app))
        self.assertIsNone(res)

    # Attributes

    def test_get_nonexisting_attribute(self):
        handler = CoroutineMock(return_value=sentinel.response)
        self.resolver.register_handler(handler, type(self.default_app))

        attribute_value = self.resolver.get_attribute(sentinel.name, handler)
        self.assertEqual(attribute_value, sentinel)

    def test_get_attribute_with_non_existing_handler(self):
        handler = CoroutineMock(return_value=sentinel.response)

        default = None
        attribute_value = self.resolver.get_attribute(sentinel.name, handler, default)
        self.assertEqual(attribute_value, default)

    def test_register_attribute(self):
        handler = CoroutineMock(return_value=sentinel.response)
        self.resolver.register_handler(handler, type(self.default_app))

        res = self.resolver.register_attribute(sentinel.name, sentinel.value, handler)
        self.assertIsNone(res)

        attribute_value = self.resolver.get_attribute(sentinel.name, handler)
        self.assertEqual(attribute_value, sentinel.value)

    def test_register_another_attribute(self):
        handler = CoroutineMock(return_value=sentinel.response)
        self.resolver.register_handler(handler, type(self.default_app))
        self.resolver.register_attribute(sentinel.name1, sentinel.value1, handler)

        self.resolver.register_attribute(sentinel.name2, sentinel.value2, handler)

        attribute_value2 = self.resolver.get_attribute(sentinel.name2, handler)
        self.assertEqual(attribute_value2, sentinel.value2)
        attribute_value1 = self.resolver.get_attribute(sentinel.name1, handler)
        self.assertEqual(attribute_value1, sentinel.value1)

    def test_register_attribute_twice(self):
        handler = CoroutineMock(return_value=sentinel.response)
        self.resolver.register_handler(handler, type(self.default_app))
        self.resolver.register_attribute(sentinel.name1, sentinel.value1, handler)

        res = self.resolver.register_attribute(sentinel.name, sentinel.value, handler)
        self.assertIsNone(res)

        attribute_value = self.resolver.get_attribute(sentinel.name, handler)
        self.assertEqual(attribute_value, sentinel.value)

    def test_deregister_attribute(self):
        handler = CoroutineMock(return_value=sentinel.response)
        self.resolver.register_handler(handler, type(self.default_app))
        self.resolver.register_attribute(sentinel.name, sentinel.value, handler)

        res = self.resolver.deregister_attribute(sentinel.name, handler)
        self.assertIsNone(res)

        attribute_value = self.resolver.get_attribute(sentinel.name, handler, default=None)
        self.assertEqual(attribute_value, None)

    def test_deregister_nonexisting_attribute(self):
        handler = CoroutineMock(return_value=sentinel.response)
        self.resolver.register_handler(handler, type(self.default_app))

        res = self.resolver.deregister_attribute(sentinel.name, handler)
        self.assertIsNone(res)

    def test_deregister_attribute_with_nonexisting_handler(self):
        handler = CoroutineMock(return_value=sentinel.response)

        res = self.resolver.deregister_attribute(sentinel.name, handler)
        self.assertIsNone(res)

    # Matchers

    def test_get_matchers_without_matchers(self):
        matchers = self.resolver.get_matchers(self.default_handler)
        self.assertEqual(matchers, [])

    def test_get_matchers_with_one_matcher(self):
        matcher = CoroutineMock(return_value=True)
        self.resolver.register_matcher(matcher, self.default_handler)

        matchers = self.resolver.get_matchers(self.default_handler)
        self.assertEqual(matchers, [matcher])

    def test_get_matchers_with_multiple_matchers(self):
        matcher1 = CoroutineMock(return_value=True)
        matcher2 = CoroutineMock(return_value=True)
        self.resolver.register_matcher(matcher1, self.default_handler)
        self.resolver.register_matcher(matcher2, self.default_handler)

        matchers = self.resolver.get_matchers(self.default_handler)
        self.assertEqual(matchers, [matcher1, matcher2])

    def test_register_matcher(self):
        handler = CoroutineMock(return_value=sentinel.response)
        matcher = CoroutineMock(return_value=True)
        self.assertIsNone(self.resolver.register_matcher(matcher, handler))

    def test_deregister_matcher(self):
        handler = CoroutineMock(return_value=sentinel.response)
        matcher = CoroutineMock(return_value=True)
        self.resolver.register_matcher(matcher, handler)

        res = self.resolver.deregister_matcher(matcher, handler)
        self.assertIsNone(res)

        matchers = self.resolver.get_matchers(handler)
        self.assertEqual(matchers, [])

    def test_deregister_matcher_with_nonexisting_handler(self):
        handler = CoroutineMock(return_value=sentinel.response)
        matcher = CoroutineMock(return_value=True)

        res = self.resolver.deregister_matcher(matcher, handler)
        self.assertIsNone(res)

    # Resolver

    async def test_resolve_request_with_all_truthy_matchers(self):
        handler = CoroutineMock(return_value=sentinel.response)
        matcher1 = CoroutineMock(return_value=True)
        matcher2 = CoroutineMock(return_value=True)
        self.resolver.register_matcher(matcher1, handler)
        self.resolver.register_matcher(matcher2, handler)

        request = Mock()
        response = await self.resolver.resolve(request, self.default_app)
        self.assertEqual(response, handler)

        matcher1.assert_called_once_with(request)
        matcher2.assert_called_once_with(request)
        handler.assert_not_called()

    async def test_resolve_request_with_all_falsy_matchers(self):
        handler = CoroutineMock(return_value=sentinel.response)
        matcher1 = CoroutineMock(return_value=False)
        matcher2 = CoroutineMock(return_value=False)
        self.resolver.register_matcher(matcher1, handler)
        self.resolver.register_matcher(matcher2, handler)

        request = Mock()
        response = await self.resolver.resolve(request, self.default_app)
        self.assertEqual(response, self.default_handler)

        matcher1.assert_called_once_with(request)
        matcher2.assert_not_called()
        handler.assert_not_called()

    async def test_resolve_request_with_first_falsy_matcher(self):
        handler = CoroutineMock(return_value=sentinel.response)
        matcher1 = CoroutineMock(return_value=False)
        matcher2 = CoroutineMock(return_value=True)
        self.resolver.register_matcher(matcher1, handler)
        self.resolver.register_matcher(matcher2, handler)

        request = Mock()
        response = await self.resolver.resolve(request, self.default_app)
        self.assertEqual(response, self.default_handler)

        matcher1.assert_called_once_with(request)
        matcher2.assert_not_called()
        handler.assert_not_called()

    async def test_resolve_request_with_last_falsy_matcher(self):
        handler = CoroutineMock(return_value=sentinel.response)
        matcher1 = CoroutineMock(return_value=True)
        matcher2 = CoroutineMock(return_value=False)
        self.resolver.register_matcher(matcher1, handler)
        self.resolver.register_matcher(matcher2, handler)

        request = Mock()
        response = await self.resolver.resolve(request, self.default_app)
        self.assertEqual(response, self.default_handler)

        matcher1.assert_called_once_with(request)
        matcher2.assert_called_once_with(request)
        handler.assert_not_called()

    async def test_resolve_request_without_handlers(self):
        request = Mock()
        response = await self.resolver.resolve(request, self.default_app)
        self.assertEqual(response, self.default_handler)

    async def test_resolve_request_with_nonexisting_app(self):
        app = create_app()
        request = Mock()
        response = await self.resolver.resolve(request, app)
        self.assertEqual(response, self.default_handler)

    async def test_resolve_request_without_matchers(self):
        handler = CoroutineMock(return_value=sentinel.response)
        self.resolver.register_handler(handler, type(self.default_app))

        request = Mock()
        response = await self.resolver.resolve(request, self.default_app)
        self.assertEqual(response, self.default_handler)

    async def test_resolve_request_with_single_matcher(self):
        handler = CoroutineMock(return_value=sentinel.response)
        matcher = CoroutineMock(return_value=True)
        self.resolver.register_matcher(matcher, handler)

        request = Mock()
        response = await self.resolver.resolve(request, self.default_app)
        self.assertEqual(response, handler)

        matcher.assert_called_once_with(request)
        handler.assert_not_called()

    async def test_resolve_request_with_multiple_handlers(self):
        matcher = CoroutineMock(side_effect=(False, True))
        handler1 = CoroutineMock(return_value=sentinel.response1)
        handler2 = CoroutineMock(return_value=sentinel.response2)
        self.resolver.register_matcher(matcher, handler1)
        self.resolver.register_matcher(matcher, handler2)

        request = Mock()
        response = await self.resolver.resolve(request, self.default_app)
        self.assertEqual(response, handler1)

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
        self.assertEqual(response, handler2)

        handler1.assert_not_called()
        handler2.assert_not_called()
        matcher.assert_called_once_with(request)
