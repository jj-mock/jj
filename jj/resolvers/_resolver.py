from inspect import isclass
from typing import Any, List, Optional, Type, Union
from unittest.mock import sentinel as nil

from undecorated import undecorated

from jj.expiration_policy import ExpirationPolicy

from ..apps import AbstractApp
from ..handlers import HandlerFunction
from ..requests import Request
from ._matcher_function import MatcherFunction
from ._registry import Registry

__all__ = ("Resolver",)

AppOrHandler = Union[Type[AbstractApp], HandlerFunction]


class Resolver:
    def __init__(self, registry: Registry,
                 default_app: AbstractApp,
                 default_handler: HandlerFunction) -> None:
        self._registry = registry
        self._default_app = default_app
        self._default_handler = default_handler

    def unwrap(self, fn: Any) -> Any:
        try:
            unwrapped = undecorated(fn)
        except ValueError:
            return fn
        return fn if (unwrapped is None) else unwrapped

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

        matchers = self._registry.get(unwrapped, "matchers")
        if len(matchers) == 0:
            self._registry.remove_name(unwrapped, "matchers")

    def get_matchers(self, handler: HandlerFunction) -> List[MatcherFunction]:
        unwrapped = self.unwrap(handler)
        matchers = self._registry.get(unwrapped, "matchers")
        return list(matchers.keys())

    # Attributes

    def register_attribute(self, name: Any, value: Any, handler: AppOrHandler) -> None:
        unwrapped = self.unwrap(handler)
        self._registry.add(unwrapped, "attributes", name, value)

    def deregister_attribute(self, attribute_name: Any, handler: AppOrHandler) -> None:
        unwrapped = self.unwrap(handler)
        self._registry.remove(unwrapped, "attributes", attribute_name)

        attributes = self._registry.get(unwrapped, "attributes")
        if len(attributes) == 0:
            self._registry.remove_name(unwrapped, "attributes")

    def get_attribute(self, attribute_name: Any,
                      handler: AppOrHandler,
                      default: Any = nil) -> Any:
        unwrapped = self.unwrap(handler)
        attributes = self._registry.get(unwrapped, "attributes")
        return attributes.get(attribute_name, default)

    def get_attributes(self, handler: AppOrHandler) -> List[Any]:
        unwrapped = self.unwrap(handler)
        attributes = self._registry.get(unwrapped, "attributes")
        return list(attributes.keys())

    # Resolve

    async def _match_request(self, request: Request, matchers: List[MatcherFunction]) -> bool:
        if len(matchers) == 0:
            return False
        for matcher in matchers:
            if not await matcher(request):
                return False
        return True

    # ExpirationPolicy

    async def _is_handler_expired(self, handler: HandlerFunction, request: Request) -> bool:
        expiration_policy: Optional[ExpirationPolicy] = self.get_attribute(
            "expiration_policy", handler, default=None
        )
        if expiration_policy is None:
            return False

        return await expiration_policy.is_expired(request)

    async def resolve(self, request: Request, app: AbstractApp) -> HandlerFunction:
        assert not isclass(app)
        handlers = self.get_handlers(type(app))
        for handler in reversed(handlers):
            matchers = self.get_matchers(handler)
            if await self._match_request(request, matchers):
                if await self._is_handler_expired(handler, request):
                    continue
                return handler
        return self._default_handler
