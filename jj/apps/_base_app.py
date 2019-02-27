from typing import Type, Dict, Optional, Union, Tuple
from inspect import getmembers

from ._abstract_app import AbstractApp
from ..resolvers import Resolver
from ..handlers import HandlerFunction


__all__ = ("BaseApp", "define_app", "create_app")


def _register(cls, name: str, value: HandlerFunction) -> None:
    if callable(value) and not name.startswith("_"):
        cls.resolver.register_handler(value, cls)


class _Registrar(type):
    def __init__(cls, name: str, bases: Tuple[Type[AbstractApp]], namespace: Dict) -> None:
        for name, value in namespace.items():
            _register(cls, name, value)
        for base in bases:
            for name, member in getmembers(base):
                _register(cls, name, member)
        super().__init__(name, bases, namespace)

    def __setattr__(cls, name: str, value: HandlerFunction) -> None:
        _register(cls, name, value)
        super().__setattr__(name, value)


class BaseApp(AbstractApp, metaclass=_Registrar):
    @property
    def resolver(self) -> Resolver:
        raise NotImplementedError()

    def __setattr__(self, name: str, value: HandlerFunction) -> None:
        _register(type(self), name, value)
        super().__setattr__(name, value)


def define_app(name: Optional[str] = None, *,
               resolver: Optional[Resolver] = None,
               handlers: Optional[Dict[str, HandlerFunction]] = None) -> Type[BaseApp]:
    if name is None:
        define_app.count = getattr(define_app, "count", 1) + 1  # type: ignore
        name = "App" + str(define_app.count)  # type: ignore

    namespace: Dict[str, Union[Resolver, HandlerFunction]] = {}
    if resolver:
        namespace["resolver"] = resolver
    if handlers:
        namespace.update(handlers)

    return type(name, (BaseApp,), namespace)


def create_app(name: Optional[str] = None, *,
               resolver: Optional[Resolver] = None,
               handlers: Optional[Dict[str, HandlerFunction]] = None) -> BaseApp:
    return define_app(name, resolver=resolver, handlers=handlers)()
