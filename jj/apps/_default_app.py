from typing import Any, Dict

from ._abstract_app import AbstractApp

__all__ = ("DefaultApp",)


class _Singleton(type):
    _instances: Dict[Any, "_Singleton"] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> "_Singleton":
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DefaultApp(AbstractApp, metaclass=_Singleton):
    pass
