from typing import Dict

from ._abstract_app import AbstractApp


__all__ = ("DefaultApp",)


class _Singleton(type):
    _instances: Dict = {}

    def __call__(cls, *args, **kwargs) -> "_Singleton":
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DefaultApp(AbstractApp, metaclass=_Singleton):
    pass
