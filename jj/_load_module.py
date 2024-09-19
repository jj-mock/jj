import importlib.util
from importlib.abc import Loader
from pathlib import Path
from types import ModuleType

__all__ = ("load_module",)

from typing import cast


def _path_to_module_name(path: Path) -> str:
    """
    Convert a file path to a valid Python module name.

    This helper function transforms the given file path into a module name by removing
    the file extension and converting the path structure into a dot-separated string,
    as required for module names. If the path is absolute, the leading part of the
    path is removed.

    :param path: The file path to be converted.
    :return: A string representing the module name derived from the path.
    """
    parts = path.with_suffix("").parts
    if path.is_absolute():
        parts = parts[1:]
    return ".".join(parts)


def load_module(path: Path) -> ModuleType:
    """
    Load a Python module from the specified file path.

    This function dynamically loads a module from the given path, using the
    importlib utilities to create and load the module. It converts the file path
    into a valid module name and registers the module in `sys.modules`.

    :param path: The file path from which to load the module.
    :return: The loaded module as a `ModuleType` object.
    :raises ModuleNotFoundError: If the module cannot be found or loaded.
    """
    module_name = _path_to_module_name(path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        raise ModuleNotFoundError(module_name)

    module = importlib.util.module_from_spec(spec)
    cast(Loader, spec.loader).exec_module(module)

    return module
