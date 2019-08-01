from typing import Any, Callable, Tuple, Union

from packed import unpack

import jj
from jj import default_app, default_handler
from jj.apps import BaseApp, create_app
from jj.http.codes import BAD_REQUEST, OK
from jj.http.methods import ANY, DELETE, POST
from jj.matchers import LogicalMatcher, RequestMatcher, ResolvableMatcher, exists
from jj.requests import Request
from jj.resolvers import Registry, Resolver, ReversedResolver
from jj.responses import Response

__all__ = ("Mock",)


MatcherType = Union[RequestMatcher, LogicalMatcher]


class Mock(jj.App):
    def __init__(self,
                 app_factory: Callable[..., BaseApp] = create_app,
                 resolver_factory: Callable[..., Resolver] = ReversedResolver) -> None:
        self._resolver = resolver_factory(Registry(), default_app, default_handler)
        self._app = app_factory(resolver=self._resolver)

    def _decode(self, payload: bytes) -> Tuple[str, MatcherType, Response]:
        def resolver(cls: Any, **kwargs: Any) -> Any:
            return cls.__unpacked__(**kwargs, resolver=self._resolver)
        decoded = unpack(payload, {ResolvableMatcher: resolver})

        handler_id = decoded.get("id")
        assert isinstance(handler_id, str)

        matcher = decoded.get("request")
        assert isinstance(matcher, (RequestMatcher, LogicalMatcher))

        response = decoded.get("response")
        assert isinstance(response, Response)

        return handler_id, matcher, response

    @jj.match_method(POST)
    @jj.match_header("x-jj-remote-mock", exists)
    async def register(self, request: Request) -> Response:
        payload = await request.read()
        try:
            handler_id, matcher, response = self._decode(payload)
        except Exception:
            return Response(status=BAD_REQUEST, json={"status": BAD_REQUEST})

        async def handler(request: Request) -> Response:
            return response.copy()

        setattr(self._app.__class__, handler_id, matcher(handler))

        return Response(status=OK, json={"status": OK})

    @jj.match_method(DELETE)
    @jj.match_header("x-jj-remote-mock", exists)
    async def deregister(self, request: Request) -> Response:
        payload = await request.read()
        try:
            handler_id, *_ = self._decode(payload)
        except Exception:
            return Response(status=BAD_REQUEST, json={"status": BAD_REQUEST})

        try:
            delattr(self._app.__class__, handler_id)
        except AttributeError:
            pass

        return Response(status=OK, json={"status": OK})

    @jj.match(ANY)
    async def resolve(self, request: Request) -> Response:
        handler = await self._resolver.resolve(request, self._app)
        return await handler(request)
