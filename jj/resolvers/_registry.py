from collections import OrderedDict
from typing import Any, MutableMapping, Type

__all__ = ("Registry",)


class Registry:
    def __init__(self,
                 mutable_mapping_factory: Type[MutableMapping[Any, Any]] = OrderedDict) -> None:
        self._factory = mutable_mapping_factory
        self._registry = self._factory()

    def add(self, container: Any, name: str, key: Any, value: Any = None) -> None:
        if container not in self._registry:
            self._registry[container] = self._factory()
        if name not in self._registry[container]:
            self._registry[container][name] = self._factory()
        self._registry[container][name][key] = value

    def get(self, container: Any, name: str) -> Any:
        if (container not in self._registry) or (name not in self._registry[container]):
            return self._factory()
        return self._registry[container][name]

    def remove(self, container: Any, name: str, key: Any) -> None:
        if (container in self._registry) and (name in self._registry[container]):
            self._registry[container][name].pop(key, None)
