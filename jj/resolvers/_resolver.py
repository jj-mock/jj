from typing import Any, List, Type
from inspect import isclass
from unittest.mock import sentinel as nil

from undecorated import undecorated

from ..apps import AbstractApp
from ..requests import Request
from ..handlers import HandlerFunction
from ._matcher_function import MatcherFunction
from ._registry import Registry


__all__ = ("Resolver",)


class Resolver:
    def __init__(self, registry: Registry,
                 default_app: AbstractApp,
                 default_handler: HandlerFunction) -> None:
        self._registry = registry
        self._default_app = default_app
        self._default_handler = default_handler

    def unwrap(self, fn: HandlerFunction) -> HandlerFunction:
        try:
            unwrapped = undecorated(fn)
        except ValueError:
            return fn
        return fn if unwrapped is None else unwrapped

    # Apps

    def register_app(self, app: Type[AbstractApp]) -> None:
        assert isclass(app)
        self._registry.add(None, "apps", app)

    def deregister_app(self, app: Type[AbstractApp]) -> None:
        assert isclass(app)
        self._registry.remove(None, "apps", app)

    def get_apps(self) -> List[Type[AbstractApp]]:
        apps = self._registry.get(None, "apps")
        return list(apps.keys())

    # Handlers

    def register_handler(self, handler: HandlerFunction, app: Type[AbstractApp]) -> None:
        assert isclass(app)
        self.deregister_handler(handler, type(self._default_app))
        self.register_app(app)
        self._registry.add(app, "handlers", handler)

    def deregister_handler(self, handler: HandlerFunction, app: Type[AbstractApp]) -> None:
        assert isclass(app)
        self._registry.remove(app, "handlers", handler)

    def get_handlers(self, app: Type[AbstractApp]) -> List[HandlerFunction]:
        assert isclass(app)
        handlers = self._registry.get(app, "handlers")
        return list(handlers.keys())

    # Matchers

    def register_matcher(self, matcher: MatcherFunction, handler: HandlerFunction) -> None:
        unwrapped = self.unwrap(handler)
        self.register_handler(unwrapped, type(self._default_app))
        self._registry.add(unwrapped, "matchers", matcher)

    def deregister_matcher(self, matcher: MatcherFunction, handler: HandlerFunction) -> None:
        unwrapped = self.unwrap(handler)
        self._registry.remove(unwrapped, "matchers", matcher)

    def get_matchers(self, handler: HandlerFunction) -> List[MatcherFunction]:
        unwrapped = self.unwrap(handler)
        matchers = self._registry.get(unwrapped, "matchers")
        return list(matchers.keys())

    # Attributes

    def register_attribute(self, name: Any, value: Any, handler: HandlerFunction) -> None:
        unwrapped = self.unwrap(handler)
        self._registry.add(unwrapped, "attributes", name, value)

    def deregister_attribute(self, attribute_name: Any, handler: HandlerFunction) -> None:
        unwrapped = self.unwrap(handler)
        self._registry.remove(unwrapped, "attributes", attribute_name)

    def get_attribute(self, attribute_name: Any,
                      handler: HandlerFunction,
                      default: Any = nil) -> Any:
        unwrapped = self.unwrap(handler)
        attributes = self._registry.get(unwrapped, "attributes")
        return attributes.get(attribute_name, default)

    # Resolve

    async def _match_request(self, request: Request, matchers: List[MatcherFunction]) -> bool:
        if len(matchers) == 0:
            return False
        for matcher in matchers:
            if not await matcher(request):
                return False
        return True

    async def resolve(self, request: Request, app: AbstractApp) -> HandlerFunction:
        assert not isclass(app)
        handlers = self.get_handlers(type(app))
        for handler in reversed(handlers):
            matchers = self.get_matchers(handler)
            if await self._match_request(request, matchers):
                return handler
        return self._default_handler
