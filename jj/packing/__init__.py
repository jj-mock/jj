from typing import Dict, List, Union

__all__ = ("PackablePrimitiveType", "PackableType",)


PackablePrimitiveType = Union[None, bool, int, str, bytes]
PackableType = Union[
    PackablePrimitiveType,
    List["PackableType"],
    Dict["PackableType", "PackableType"]
]
