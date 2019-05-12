import logging
import asynctest
from asynctest import Mock, call

import jj
from jj.apps import create_app
from jj.resolvers import Registry, ReversedResolver
from jj.matchers import MethodMatcher
from jj.handlers import default_handler
from jj.requests import Request
from jj.responses import Response
from jj.middlewares import BaseMiddleware, LoggerMiddleware

from .._test_utils import run


class TestLoggerMiddleware(asynctest.TestCase):
    def setUp(self):
        self.default_app = create_app()
        self.resolver = ReversedResolver(Registry(), self.default_app, default_handler)

    def test_middleware_without_resolver(self):
        with self.assertRaises(Exception):
            LoggerMiddleware()

    def test_middleware_without_logger(self):
        with self.assertRaises(Exception):
            LoggerMiddleware(self.resolver)

    def test_middleware_with_instance_resolver(self):
        logger = Mock()
        middleware = LoggerMiddleware(self.resolver, logger)
        self.assertIsInstance(middleware, BaseMiddleware)

    async def test_app_logger(self):
        mock = Mock()
        record = {"request": None, "response": None}

        @LoggerMiddleware(self.resolver, mock)
        class App(jj.App):
            resolver = self.resolver
            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                record["request"] = request
                response = Response(status=200)
                record["response"] = response
                return response

        async with run(App()) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 200)

        mock.assert_has_calls([
            call.info(record["request"], extra={
                "jj_request": record["request"],
            }),
            call.info(record["response"], extra={
                "jj_request": record["request"],
                "jj_response": record["response"],
            }),
        ])
        self.assertEqual(mock.info.call_count, 2)

    async def test_handler_logger(self):
        mock = Mock()
        record = {"request": None, "response": None}

        class App(jj.App):
            resolver = self.resolver
            @LoggerMiddleware(self.resolver, mock)
            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                record["request"] = request
                response = Response(status=200)
                record["response"] = response
                return response

        async with run(App()) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 200)

        mock.assert_has_calls([
            call.info(record["request"], extra={
                "jj_request": record["request"],
            }),
            call.info(record["response"], extra={
                "jj_request": record["request"],
                "jj_response": record["response"],
            }),
        ])
        self.assertEqual(mock.info.call_count, 2)

    async def test_app_and_handler_logger(self):
        app_logger, handler_logger = Mock(), Mock()

        @LoggerMiddleware(self.resolver, app_logger)
        class App(jj.App):
            resolver = self.resolver
            @LoggerMiddleware(resolver, handler_logger)
            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                return Response(status=200)

        async with run(App()) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 200)

        self.assertEqual(app_logger.info.call_count, 0)
        self.assertEqual(handler_logger.info.call_count, 2)

    async def test_handler_without_logger(self):
        class App(jj.App):
            resolver = self.resolver
            @LoggerMiddleware(self.resolver, None)
            @MethodMatcher("*", resolver=resolver)
            async def handler(request):
                response = Response(status=200)
                return response

        async with run(App()) as client:
            response = await client.get("/")
            self.assertEqual(response.status, 200)
