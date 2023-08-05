from typing import Any, Callable, Optional, Tuple, Union

from packed import pack, unpack

import jj
from jj import default_app, default_handler
from jj.apps import BaseApp, create_app
from jj.expiration_policy import ExpirationPolicy
from jj.http.codes import BAD_REQUEST, OK
from jj.http.methods import ANY, DELETE, GET, POST
from jj.matchers import LogicalMatcher, RequestMatcher, ResolvableMatcher, exists
from jj.requests import Request
from jj.resolvers import Registry, Resolver
from jj.responses import DelayedResponse, RelayResponse, Response, StreamResponse

from ._history import HistoryRepository
from ._remote_response import RemoteResponseType

__all__ = ("Mock",)

MatcherType = Union[RequestMatcher, LogicalMatcher]


class _DecodeError(Exception):
    pass


class Mock(jj.App):
    def __init__(self,
                 app_factory: Callable[..., BaseApp] = create_app,
                 resolver_factory: Callable[..., Resolver] = Resolver) -> None:
        self._resolver = resolver_factory(Registry(), default_app, default_handler)
        self._app = app_factory(resolver=self._resolver)
        self._repo = HistoryRepository()

    def _decode(self, payload: bytes) -> Tuple[str, MatcherType, RemoteResponseType,
                                               Optional[ExpirationPolicy]]:
        def resolver(cls: Any, **kwargs: Any) -> Any:
            return cls.__unpacked__(**kwargs, resolver=self._resolver)

        try:
            decoded = unpack(payload, {ResolvableMatcher: resolver})
        except Exception as e:
            raise _DecodeError(f"Decode Error: can't unpack message ({e})")

        errors = []

        handler_id = decoded.get("id")
        if not isinstance(handler_id, str):
            errors.append(f"Decode Error: invalid handler id ({handler_id!r})")

        matcher = decoded.get("request")
        if not isinstance(matcher, (RequestMatcher, LogicalMatcher)):
            errors.append(f"Decode Error: invalid request field ({matcher!r})")

        response = decoded.get("response")
        if not isinstance(response, (Response, RelayResponse, DelayedResponse)):
            errors.append(f"Decode Error: invalid response field ({response!r})")

        expiration_policy = decoded.get("expiration_policy")
        if not isinstance(expiration_policy, (ExpirationPolicy, type(None))):
            errors.append(f"Decode Error: invalid expiration policy ({expiration_policy!r})")

        if len(errors) > 0:
            raise _DecodeError("\n".join(errors))

        return handler_id, matcher, response, expiration_policy

    def _register_handler(self, handler_id: str,
                          matcher: MatcherType,
                          response: RemoteResponseType,
                          expiration_policy: Optional[ExpirationPolicy]) -> None:
        async def handler(req: Request) -> RemoteResponseType:
            res = response.copy()
            await res._prepare_hook(req)
            return res

        self._resolver.register_attribute("handler_id", handler_id, handler)
        self._resolver.register_attribute("expiration_policy", expiration_policy, handler)
        setattr(self._app.__class__, handler_id, matcher(handler))

    def _deregister_handler(self, handler_id: str) -> None:
        handler = getattr(self._app.__class__, handler_id, None)
        if handler is None:
            return

        try:
            delattr(self._app.__class__, handler_id)
        except AttributeError:
            pass

        matchers = self._resolver.get_matchers(handler)
        for matcher in matchers:
            self._resolver.deregister_matcher(matcher, handler)

        attributes = self._resolver.get_attributes(handler)
        for attribute in attributes:
            self._resolver.deregister_attribute(attribute, handler)

        self._resolver._registry.remove_container(handler)

    @jj.match(POST, "/__jj__/reset", headers={"x-jj-remote-mock": exists})
    async def reset(self, request: Request) -> Response:
        await request.read()

        handlers = self._resolver.get_handlers(self._app.__class__)
        for handler in handlers:
            handler_id = self._resolver.get_attribute("handler_id", handler, None)
            if handler_id:
                self._deregister_handler(handler_id)

        await self._repo.clear()

        return Response(status=OK, json={"status": OK})

    @jj.match_any([
        jj.match(POST, "/__jj__/register", headers={"x-jj-remote-mock": exists}),
        # backward compatibility
        jj.match(POST, headers={"x-jj-remote-mock": exists})
    ])
    async def register(self, request: Request) -> Response:
        payload = await request.read()
        try:
            handler_id, matcher, response, expiration_policy = self._decode(payload)
        except Exception as e:
            return Response(status=BAD_REQUEST, json={"status": BAD_REQUEST, "error": str(e)})

        self._register_handler(handler_id, matcher, response, expiration_policy)

        return Response(status=OK, json={"status": OK})

    @jj.match_any([
        jj.match(DELETE, "/__jj__/deregister", headers={"x-jj-remote-mock": exists}),
        # backward compatibility
        jj.match(DELETE, headers={"x-jj-remote-mock": exists})
    ])
    async def deregister(self, request: Request) -> Response:
        payload = await request.read()
        try:
            handler_id, *_ = self._decode(payload)
        except Exception as e:
            return Response(status=BAD_REQUEST, json={"status": BAD_REQUEST, "error": str(e)})

        self._deregister_handler(handler_id)
        await self._repo.delete_by_tag(handler_id)  # delete history

        return Response(status=OK, json={"status": OK})

    @jj.match_any([
        jj.match(GET, "/__jj__/history", headers={"x-jj-remote-mock": exists}),
        # backward compatibility
        jj.match(GET, headers={"x-jj-remote-mock": exists})
    ])
    async def history(self, request: Request) -> Response:
        payload = await request.read()
        try:
            handler_id, *_ = self._decode(payload)
        except Exception as e:
            return Response(status=BAD_REQUEST, json={"status": BAD_REQUEST, "error": str(e)})

        history = await self._repo.get_by_tag(handler_id)
        packed = pack(history)
        return Response(status=OK, body=packed)

    @jj.match(ANY)
    async def resolve(self, request: Request) -> StreamResponse:
        handler = await self._resolver.resolve(request, self._app)
        response = await handler(request)

        handler_id = self._resolver.get_attribute("handler_id", handler, default=None)
        if handler_id:
            await self._repo.add(request, response, tags=[handler_id])

        return response
